"""
Reusable Data Quality Framework for Glue Jobs.

Production pattern: define checks as config dicts, run them generically.
Same checks work across any DataFrame — claims, policies, customers.

In real AWS:
  - Results go to CloudWatch metrics + DynamoDB
  - Alerts via SNS on critical failures
  - Integrated with Glue Data Quality (new AWS feature)
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from datetime import datetime
from typing import Dict, List, Optional


class QualityCheckResult:
    """Single check result."""

    def __init__(self, check_name: str, passed: bool, details: str,
                 rows_checked: int = 0, rows_failed: int = 0):
        self.check_name = check_name
        self.passed = passed
        self.details = details
        self.rows_checked = rows_checked
        self.rows_failed = rows_failed
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "check_name": self.check_name,
            "passed": self.passed,
            "details": self.details,
            "rows_checked": self.rows_checked,
            "rows_failed": self.rows_failed,
            "timestamp": self.timestamp,
        }


class DataQualityChecker:
    """
    Generic quality checker.

    Usage:
        checker = DataQualityChecker(df)
        checker.check_not_null("claim_id")
        checker.check_unique("claim_id")
        checker.check_range("claim_amount", min_val=0)
        checker.check_referential_integrity("policy_id", policies_df, "policy_id")
        results = checker.get_results()
    """

    def __init__(self, df: DataFrame, table_name: str = "unknown"):
        self.df = df
        self.table_name = table_name
        self.results: List[QualityCheckResult] = []
        self.total_rows = df.count()

    def check_not_null(self, column: str) -> "DataQualityChecker":
        """Check column has no nulls or empty strings."""
        null_count = self.df.filter(
            F.col(column).isNull() | (F.trim(F.col(column)) == "")
        ).count()

        passed = null_count == 0
        self.results.append(QualityCheckResult(
            check_name=f"not_null_{column}",
            passed=passed,
            details=f"{null_count} null/empty rows in {column}",
            rows_checked=self.total_rows,
            rows_failed=null_count,
        ))
        return self  # chainable

    def check_unique(self, column: str) -> "DataQualityChecker":
        """Check column has no duplicates."""
        total = self.df.select(column).count()
        distinct = self.df.select(column).distinct().count()
        dupe_count = total - distinct

        passed = dupe_count == 0
        self.results.append(QualityCheckResult(
            check_name=f"unique_{column}",
            passed=passed,
            details=f"{dupe_count} duplicate rows in {column}",
            rows_checked=total,
            rows_failed=dupe_count,
        ))
        return self

    def check_range(self, column: str, min_val: Optional[float] = None,
                    max_val: Optional[float] = None) -> "DataQualityChecker":
        """Check numeric column within range."""
        conditions = []
        if min_val is not None:
            conditions.append(F.col(column) < min_val)
        if max_val is not None:
            conditions.append(F.col(column) > max_val)

        if not conditions:
            return self

        combined = conditions[0]
        for c in conditions[1:]:
            combined = combined | c

        # Also count nulls as failures
        fail_count = self.df.filter(combined | F.col(column).isNull()).count()

        passed = fail_count == 0
        range_desc = f"[{min_val}, {max_val}]"
        self.results.append(QualityCheckResult(
            check_name=f"range_{column}",
            passed=passed,
            details=f"{fail_count} rows outside {range_desc} in {column}",
            rows_checked=self.total_rows,
            rows_failed=fail_count,
        ))
        return self

    def check_accepted_values(self, column: str,
                              accepted: List[str]) -> "DataQualityChecker":
        """Check column only contains accepted values."""
        fail_count = self.df.filter(
            ~F.lower(F.trim(F.col(column))).isin([v.lower() for v in accepted])
        ).count()

        passed = fail_count == 0
        self.results.append(QualityCheckResult(
            check_name=f"accepted_values_{column}",
            passed=passed,
            details=f"{fail_count} rows with unexpected values in {column}. Expected: {accepted}",
            rows_checked=self.total_rows,
            rows_failed=fail_count,
        ))
        return self

    def check_referential_integrity(self, column: str, ref_df: DataFrame,
                                    ref_column: str) -> "DataQualityChecker":
        """Check all values in column exist in reference table (FK check)."""
        source_values = self.df.select(column).distinct()
        ref_values = ref_df.select(ref_column).distinct()

        orphan_count = source_values.join(
            ref_values,
            source_values[column] == ref_values[ref_column],
            "left_anti"
        ).count()

        passed = orphan_count == 0
        self.results.append(QualityCheckResult(
            check_name=f"ref_integrity_{column}",
            passed=passed,
            details=f"{orphan_count} orphan values in {column}",
            rows_checked=source_values.count(),
            rows_failed=orphan_count,
        ))
        return self

    def check_freshness(self, date_column: str,
                        max_age_days: int = 7) -> "DataQualityChecker":
        """Check most recent record not older than max_age_days."""
        max_date = self.df.agg(F.max(F.col(date_column))).collect()[0][0]

        if max_date is None:
            self.results.append(QualityCheckResult(
                check_name=f"freshness_{date_column}",
                passed=False,
                details=f"No dates found in {date_column}",
            ))
            return self

        from datetime import timedelta
        age = (datetime.utcnow().date() - max_date).days if hasattr(max_date, 'year') else None

        passed = age is not None and age <= max_age_days
        self.results.append(QualityCheckResult(
            check_name=f"freshness_{date_column}",
            passed=passed,
            details=f"Most recent: {max_date}, age: {age} days (max: {max_age_days})",
        ))
        return self

    def check_row_count(self, min_rows: int = 1,
                        max_rows: Optional[int] = None) -> "DataQualityChecker":
        """Check row count within expected range."""
        count = self.total_rows
        passed = count >= min_rows
        if max_rows is not None:
            passed = passed and count <= max_rows

        self.results.append(QualityCheckResult(
            check_name="row_count",
            passed=passed,
            details=f"Row count: {count} (expected: [{min_rows}, {max_rows or 'inf'}])",
            rows_checked=count,
        ))
        return self

    # ============================================================
    # RESULTS
    # ============================================================

    def get_results(self) -> List[Dict]:
        """Return all results as dicts."""
        return [r.to_dict() for r in self.results]

    def all_passed(self) -> bool:
        """True if every check passed."""
        return all(r.passed for r in self.results)

    def get_failures(self) -> List[Dict]:
        """Return only failed checks."""
        return [r.to_dict() for r in self.results if not r.passed]

    def print_report(self):
        """Print human-readable report."""
        print(f"\n{'='*60}")
        print(f"QUALITY REPORT: {self.table_name}")
        print(f"Total rows: {self.total_rows}")
        print(f"{'='*60}")

        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            print(f"  [{status}] {r.check_name}: {r.details}")

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        print(f"\nResult: {passed}/{total} checks passed")
        print(f"{'='*60}")
