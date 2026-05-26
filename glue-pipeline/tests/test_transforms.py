"""
Unit tests for ClaimsProcessor.

Pattern: shared SparkSession fixture, small test DataFrames.
In interview: shows you test Spark code, not just write it.

Run: pytest tests/ -v
"""
import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType
import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jobs.process_claims import ClaimsProcessor
from utils.quality_checks import DataQualityChecker


# ============================================================
# FIXTURES — shared across all tests
# ============================================================

@pytest.fixture(scope="session")
def spark():
    """
    One SparkSession for entire test session.
    scope="session" = expensive object created once, reused.
    """
    spark = SparkSession.builder \
        .appName("test_claims") \
        .master("local[1]") \
        .config("spark.sql.shuffle.partitions", "1") \
        .config("spark.ui.enabled", "false") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    yield spark
    spark.stop()


@pytest.fixture
def processor(spark):
    """Fresh ClaimsProcessor for each test."""
    config = {"input_path": "test", "output_path": "test"}
    return ClaimsProcessor(spark, config)


@pytest.fixture
def sample_claims_df(spark):
    """Small DataFrame with mix of good and bad data."""
    schema = StructType([
        StructField("claim_id", StringType(), True),
        StructField("policy_id", StringType(), True),
        StructField("claim_date", StringType(), True),
        StructField("claim_amount", StringType(), True),
        StructField("claim_type", StringType(), True),
        StructField("claim_status", StringType(), True),
        StructField("description", StringType(), True),
        StructField("filed_by", StringType(), True),
        StructField("created_at", StringType(), True),
        StructField("loaded_at", StringType(), True),
    ])
    data = [
        # Good records
        ("C001", "P001", "2021-06-15", "5200.00", "collision", "paid", "Test", "1001", "2021-06-15", "2024-01-01"),
        ("C002", "P001", "2021-09-20", "1800.00", "comprehensive", "approved", "Test", "1001", "2021-09-20", "2024-01-01"),
        ("C003", "P002", "2021-11-10", "15000.00", "property", "under_review", "Test", "1001", "2021-11-10", "2024-01-01"),
        # Bad: negative amount
        ("BAD1", "P001", "2021-06-15", "-500.00", "collision", "paid", "Negative", "1001", "2021-06-15", "2024-01-01"),
        # Bad: future date
        ("BAD2", "P001", "2099-12-31", "1000.00", "medical", "submitted", "Future", "1001", "2099-12-31", "2024-01-01"),
        # Bad: null policy
        ("BAD3", None, "2021-08-01", "2000.00", "collision", "paid", "NullPolicy", "1001", "2021-08-01", "2024-01-01"),
        # Bad: null amount
        ("BAD4", "P001", "2021-09-01", None, "collision", "paid", "NullAmount", "1001", "2021-09-01", "2024-01-01"),
        # Bad: empty claim_id
        ("", "P001", "2021-10-01", "3000.00", "collision", "paid", "EmptyID", "1001", "2021-10-01", "2024-01-01"),
    ]
    return spark.createDataFrame(data, schema)


@pytest.fixture
def policies_df(spark):
    """Reference policies for orphan check."""
    data = [("P001",), ("P002",), ("P003",)]
    return spark.createDataFrame(data, ["policy_id"])


# ============================================================
# VALIDATION TESTS
# ============================================================

class TestValidation:
    """Test quarantine logic separates bad data correctly."""

    def test_clean_records_pass_validation(self, processor, sample_claims_df):
        """Good records survive validation."""
        df_clean, df_quarantine = processor.validate_and_quarantine(sample_claims_df)

        # 3 good records should pass
        assert df_clean.count() == 3
        # 5 bad records quarantined (negative, future, null policy, null amount, empty ID)
        assert df_quarantine.count() == 5

    def test_negative_amount_quarantined(self, processor, sample_claims_df):
        """Negative amounts go to quarantine."""
        _, df_quarantine = processor.validate_and_quarantine(sample_claims_df)

        negative_reasons = df_quarantine.filter(
            F.col("quarantine_reason") == "invalid_amount"
        )
        # BAD1 (negative) and BAD4 (null amount) both match invalid_amount
        assert negative_reasons.count() >= 1

    def test_future_date_quarantined(self, processor, sample_claims_df):
        """Future dates go to quarantine."""
        _, df_quarantine = processor.validate_and_quarantine(sample_claims_df)

        future = df_quarantine.filter(
            F.col("quarantine_reason") == "future_date"
        )
        assert future.count() == 1

    def test_null_policy_quarantined(self, processor, sample_claims_df):
        """Null policy_id goes to quarantine."""
        _, df_quarantine = processor.validate_and_quarantine(sample_claims_df)

        null_policy = df_quarantine.filter(
            F.col("quarantine_reason") == "null_policy_id"
        )
        assert null_policy.count() == 1

    def test_null_claim_id_quarantined(self, processor, sample_claims_df):
        """Empty/null claim_id goes to quarantine."""
        _, df_quarantine = processor.validate_and_quarantine(sample_claims_df)

        null_id = df_quarantine.filter(
            F.col("quarantine_reason") == "null_claim_id"
        )
        assert null_id.count() == 1

    def test_orphan_policy_quarantined(self, processor, sample_claims_df, policies_df):
        """Claims with non-existent policy_id quarantined when policies provided."""
        # Add orphan record
        spark = sample_claims_df.sparkSession
        orphan_data = [("ORPHAN1", "P9999", "2021-07-01", "3000.00", "collision",
                        "paid", "Orphan", "1001", "2021-07-01", "2024-01-01")]
        schema = sample_claims_df.schema
        orphan_df = spark.createDataFrame(orphan_data, schema)
        combined = sample_claims_df.union(orphan_df)

        _, df_quarantine = processor.validate_and_quarantine(combined, policies_df)

        orphans = df_quarantine.filter(
            F.col("quarantine_reason") == "orphan_policy"
        )
        assert orphans.count() == 1

    def test_quarantine_has_timestamp(self, processor, sample_claims_df):
        """Quarantined records get quarantined_at timestamp."""
        _, df_quarantine = processor.validate_and_quarantine(sample_claims_df)

        assert "quarantined_at" in df_quarantine.columns

    def test_clean_has_no_quarantine_reason(self, processor, sample_claims_df):
        """Clean records don't have quarantine_reason column."""
        df_clean, _ = processor.validate_and_quarantine(sample_claims_df)

        assert "quarantine_reason" not in df_clean.columns

    def test_metrics_updated(self, processor, sample_claims_df):
        """Processor metrics track quarantine counts."""
        processor.validate_and_quarantine(sample_claims_df)

        assert processor.metrics["clean_rows"] == 3
        assert processor.metrics["quarantined_rows"] == 5
        assert len(processor.metrics["quarantine_reasons"]) > 0


# ============================================================
# TRANSFORM TESTS
# ============================================================

class TestTransform:
    """Test business transformations on clean data."""

    def test_transform_output_columns(self, processor, sample_claims_df):
        """Transform produces expected column set."""
        df_clean, _ = processor.validate_and_quarantine(sample_claims_df)
        df_transformed = processor.transform(df_clean)

        expected_cols = {
            "claim_id", "policy_id", "claim_date", "claim_amount",
            "claim_type", "claim_status", "description", "filed_by",
            "claim_month", "claim_year", "is_high_value",
            "created_at", "loaded_at", "processed_at"
        }
        assert set(df_transformed.columns) == expected_cols

    def test_high_value_flag(self, processor, sample_claims_df):
        """Claims over 10000 flagged as high_value."""
        df_clean, _ = processor.validate_and_quarantine(sample_claims_df)
        df_transformed = processor.transform(df_clean)

        high_value = df_transformed.filter(F.col("is_high_value") == True)
        # C003 = 15000.00 should be high value
        assert high_value.count() == 1

        row = high_value.collect()[0]
        assert row["claim_id"] == "C003"

    def test_claim_type_lowercased(self, processor, spark):
        """Claim type normalized to lowercase."""
        schema = StructType([
            StructField("claim_id", StringType(), True),
            StructField("policy_id", StringType(), True),
            StructField("claim_date", StringType(), True),
            StructField("claim_amount", StringType(), True),
            StructField("claim_type", StringType(), True),
            StructField("claim_status", StringType(), True),
            StructField("description", StringType(), True),
            StructField("filed_by", StringType(), True),
            StructField("created_at", StringType(), True),
            StructField("loaded_at", StringType(), True),
        ])
        data = [("C099", "P001", "2021-06-15", "5000.00", "COLLISION", "PAID",
                 "Test", "1001", "2021-06-15", "2024-01-01")]
        df = spark.createDataFrame(data, schema)

        df_clean, _ = processor.validate_and_quarantine(df)
        df_transformed = processor.transform(df_clean)

        row = df_transformed.collect()[0]
        assert row["claim_type"] == "collision"
        assert row["claim_status"] == "paid"

    def test_claim_month_extracted(self, processor, sample_claims_df):
        """claim_month derived from claim_date."""
        df_clean, _ = processor.validate_and_quarantine(sample_claims_df)
        df_transformed = processor.transform(df_clean)

        assert "claim_month" in df_transformed.columns
        assert "claim_year" in df_transformed.columns

        # C001 date = 2021-06-15 -> year = 2021
        row = df_transformed.filter(F.col("claim_id") == "C001").collect()[0]
        assert row["claim_year"] == 2021

    def test_no_data_loss_in_transform(self, processor, sample_claims_df):
        """Transform doesn't lose rows."""
        df_clean, _ = processor.validate_and_quarantine(sample_claims_df)
        clean_count = df_clean.count()

        df_transformed = processor.transform(df_clean)
        assert df_transformed.count() == clean_count


# ============================================================
# QUALITY CHECKS TESTS
# ============================================================

class TestQualityChecker:
    """Test reusable quality framework."""

    def test_not_null_passes(self, spark):
        data = [("a",), ("b",), ("c",)]
        df = spark.createDataFrame(data, ["col1"])

        checker = DataQualityChecker(df, "test")
        checker.check_not_null("col1")

        assert checker.all_passed()

    def test_not_null_fails(self, spark):
        data = [("a",), (None,), ("c",)]
        df = spark.createDataFrame(data, ["col1"])

        checker = DataQualityChecker(df, "test")
        checker.check_not_null("col1")

        assert not checker.all_passed()
        failures = checker.get_failures()
        assert len(failures) == 1
        assert failures[0]["rows_failed"] == 1

    def test_unique_passes(self, spark):
        data = [("a",), ("b",), ("c",)]
        df = spark.createDataFrame(data, ["col1"])

        checker = DataQualityChecker(df, "test")
        checker.check_unique("col1")

        assert checker.all_passed()

    def test_unique_fails(self, spark):
        data = [("a",), ("a",), ("c",)]
        df = spark.createDataFrame(data, ["col1"])

        checker = DataQualityChecker(df, "test")
        checker.check_unique("col1")

        assert not checker.all_passed()

    def test_range_check(self, spark):
        data = [(1.0,), (5.0,), (10.0,)]
        df = spark.createDataFrame(data, ["amount"])

        checker = DataQualityChecker(df, "test")
        checker.check_range("amount", min_val=0, max_val=100)
        assert checker.all_passed()

        checker2 = DataQualityChecker(df, "test")
        checker2.check_range("amount", min_val=0, max_val=5)
        assert not checker2.all_passed()

    def test_chaining(self, spark):
        """Checks can be chained fluently."""
        data = [("a", 1.0), ("b", 2.0)]
        df = spark.createDataFrame(data, ["id", "amount"])

        checker = DataQualityChecker(df, "test")
        checker.check_not_null("id") \
               .check_unique("id") \
               .check_range("amount", min_val=0)

        results = checker.get_results()
        assert len(results) == 3
        assert checker.all_passed()

    def test_referential_integrity(self, spark):
        """FK check catches orphans."""
        source = spark.createDataFrame([("P001",), ("P999",)], ["policy_id"])
        ref = spark.createDataFrame([("P001",), ("P002",)], ["policy_id"])

        checker = DataQualityChecker(source, "test")
        checker.check_referential_integrity("policy_id", ref, "policy_id")

        assert not checker.all_passed()
        failures = checker.get_failures()
        assert failures[0]["rows_failed"] == 1  # P999 orphan
