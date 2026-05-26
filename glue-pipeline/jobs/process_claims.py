"""
AWS Glue Job: Process insurance claims
- Extract from S3 (or local CSV)
- Validate and quarantine bad records
- Transform clean records
- Load to Snowflake (or local CSV for testing)

In real AWS Glue:
  - Replace SparkSession with GlueContext
  - Replace CSV read with Glue Catalog / DynamicFrame
  - Replace sys.argv with getResolvedOptions
  - Add job bookmarks for incremental processing

Standalone: python jobs/process_claims.py
From DAG:   from jobs.process_claims import run_job; metrics = run_job(config)
"""
import sys
import logging
from datetime import datetime, timezone
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType,
    DateType, TimestampType
)

# ============================================================
# In real Glue, these would come from:
# from awsglue.context import GlueContext
# from awsglue.job import Job
# from awsglue.utils import getResolvedOptions
# from awsglue.dynamicframe import DynamicFrame
# ============================================================

logger = logging.getLogger(__name__)


class ClaimsProcessor:
    """
    Encapsulated claims processing pipeline.
    Production pattern: class-based for testability and reuse.
    """

    def __init__(self, spark, config):
        self.spark = spark
        self.config = config
        self.metrics = {
            "job_start": datetime.now(timezone.utc).isoformat(),
            "input_rows": 0,
            "clean_rows": 0,
            "quarantined_rows": 0,
            "output_rows": 0,
            "quarantine_reasons": {},
        }

    # ============================================================
    # EXTRACT
    # ============================================================

    def extract(self, input_path):
        """
        Read raw claims from source.

        In Glue: glue_context.create_dynamic_frame.from_catalog(
            database="insurance_raw", table_name="raw_claims"
        ).toDF()
        """
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

        df = self.spark.read \
            .option("header", "true") \
            .schema(schema) \
            .csv(input_path)

        self.metrics["input_rows"] = df.count()
        logger.info("EXTRACT: Read %d rows from %s", self.metrics["input_rows"], input_path)
        return df

    # ============================================================
    # VALIDATE + QUARANTINE
    # ============================================================

    def validate_and_quarantine(self, df, policies_df=None):
        """
        Split data: valid records continue, invalid go to quarantine.
        NEVER stop pipeline for bad data — isolate and continue.

        Each rule adds a quarantine_reason column.
        Records can match multiple rules — first match wins.
        """
        # Cast types for validation
        df = df \
            .withColumn("claim_amount_num", F.col("claim_amount").cast(DoubleType())) \
            .withColumn("claim_date_parsed", F.to_date(F.col("claim_date"), "yyyy-MM-dd"))

        # Rule 1: null claim_id
        rule_null_id = F.col("claim_id").isNull() | (F.trim(F.col("claim_id")) == "")

        # Rule 2: null policy_id
        rule_null_policy = F.col("policy_id").isNull() | (F.trim(F.col("policy_id")) == "")

        # Rule 3: null or negative amount
        rule_bad_amount = F.col("claim_amount_num").isNull() | (F.col("claim_amount_num") < 0)

        # Rule 4: future date
        rule_future_date = F.col("claim_date_parsed") > F.current_date()

        # Rule 5: invalid date (unparseable)
        rule_invalid_date = F.col("claim_date_parsed").isNull() & F.col("claim_date").isNotNull()

        # Combine: any rule = quarantine
        quarantine_reason = F.when(rule_null_id, "null_claim_id") \
            .when(rule_null_policy, "null_policy_id") \
            .when(rule_bad_amount, "invalid_amount") \
            .when(rule_future_date, "future_date") \
            .when(rule_invalid_date, "invalid_date") \
            .otherwise(None)

        df = df.withColumn("quarantine_reason", quarantine_reason)

        # Rule 6: orphan policy (no matching policy record)
        if policies_df is not None:
            valid_policies = policies_df.select("policy_id").distinct()
            df = df.join(
                valid_policies.withColumn("_policy_exists", F.lit(True)),
                on="policy_id",
                how="left"
            )
            # Only mark as orphan if not already quarantined for another reason
            df = df.withColumn(
                "quarantine_reason",
                F.when(
                    F.col("quarantine_reason").isNull() & F.col("_policy_exists").isNull(),
                    "orphan_policy"
                ).otherwise(F.col("quarantine_reason"))
            ).drop("_policy_exists")

        # Split: clean vs quarantine
        df_quarantine = df.filter(F.col("quarantine_reason").isNotNull()) \
            .withColumn("quarantined_at", F.current_timestamp())

        df_clean = df.filter(F.col("quarantine_reason").isNull()) \
            .drop("quarantine_reason")

        # Metrics
        quarantine_count = df_quarantine.count()
        clean_count = df_clean.count()
        self.metrics["quarantined_rows"] = quarantine_count
        self.metrics["clean_rows"] = clean_count

        # Reason breakdown
        if quarantine_count > 0:
            reasons = df_quarantine.groupBy("quarantine_reason").count().collect()
            self.metrics["quarantine_reasons"] = {
                row["quarantine_reason"]: row["count"] for row in reasons
            }

        logger.info("VALIDATE: Clean=%d | Quarantined=%d", clean_count, quarantine_count)
        logger.info("VALIDATE: Reasons=%s", self.metrics["quarantine_reasons"])

        return df_clean, df_quarantine

    # ============================================================
    # TRANSFORM
    # ============================================================

    def transform(self, df):
        """
        Apply business transformations to clean data.
        All type casting + enrichment happens here.
        """
        df_transformed = df \
            .withColumn("claim_amount", F.col("claim_amount_num")) \
            .withColumn("claim_date", F.col("claim_date_parsed")) \
            .withColumn("claim_type", F.lower(F.trim(F.col("claim_type")))) \
            .withColumn("claim_status", F.lower(F.trim(F.col("claim_status")))) \
            .withColumn("claim_month", F.date_trunc("month", F.col("claim_date"))) \
            .withColumn("claim_year", F.year(F.col("claim_date"))) \
            .withColumn("is_high_value",
                F.when(F.col("claim_amount") > 10000, True).otherwise(False)
            ) \
            .withColumn("processed_at", F.current_timestamp()) \
            .drop("claim_amount_num", "claim_date_parsed", "quarantine_reason")

        # Select final columns in order
        final_columns = [
            "claim_id", "policy_id", "claim_date", "claim_amount",
            "claim_type", "claim_status", "description", "filed_by",
            "claim_month", "claim_year", "is_high_value",
            "created_at", "loaded_at", "processed_at"
        ]

        self.metrics["output_rows"] = df_transformed.count()
        logger.info("TRANSFORM: Output=%d rows", self.metrics["output_rows"])
        return df_transformed.select(final_columns)

    # ============================================================
    # LOAD
    # ============================================================

    def load_to_snowflake(self, df, table_name):
        """
        Write to Snowflake via Spark connector.
        In Glue: can also use JDBC or Snowflake Glue connector.
        """
        sf_options = self.config.get("snowflake", {})
        if not sf_options:
            logger.warning("LOAD: Snowflake not configured — skipping")
            return

        df.write \
            .format("snowflake") \
            .options(**sf_options) \
            .option("dbtable", table_name) \
            .mode("append") \
            .save()
        logger.info("LOAD: Written %d rows to Snowflake: %s", df.count(), table_name)

    def load_to_local(self, df, output_path, format="csv"):
        """
        Local output for testing — uses toPandas() to avoid Hadoop native libs on Windows.
        In AWS Glue: df.write.parquet(s3_path) or write to Iceberg table.
        """
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf = df.toPandas()
        pdf.to_csv(output_path, index=False)
        logger.info("LOAD: Written %d rows to %s", len(pdf), output_path)

    def save_quarantine(self, df_quarantine, quarantine_path):
        """Save quarantined records for investigation."""
        if df_quarantine.count() == 0:
            logger.info("QUARANTINE: No records to quarantine")
            return

        import os
        os.makedirs(os.path.dirname(quarantine_path), exist_ok=True)
        pdf = df_quarantine.toPandas()
        pdf.to_csv(quarantine_path, index=False)
        logger.info("QUARANTINE: Saved %d records to %s", len(pdf), quarantine_path)

    # ============================================================
    # METRICS
    # ============================================================

    def get_metrics(self):
        """Return job metrics for DynamoDB/CloudWatch tracking."""
        self.metrics["job_end"] = datetime.now(timezone.utc).isoformat()
        return self.metrics


# ============================================================
# RUN_JOB — callable from DAG or standalone
# ============================================================

def run_job(config=None):
    """
    Execute full pipeline. Returns metrics dict.

    Why this function exists:
      - DAG calls run_job(config) → no SparkSession in DAG code
      - CLI calls main() → which calls run_job()
      - Tests call ClaimsProcessor directly → finer control

    SparkSession created HERE, not in DAG.
    Airflow = orchestrator, NOT compute engine.
    """
    if config is None:
        config = {
            "input_path": "data/raw/raw_claims.csv",
            "policies_path": "data/raw/raw_policies.csv",
            "output_path": "data/processed/claims.csv",
            "quarantine_path": "data/quarantine/claims.csv",
        }

    spark = SparkSession.builder \
        .appName("process_claims") \
        .master("local[*]") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    try:
        processor = ClaimsProcessor(spark, config)

        # 1. Extract
        df_raw = processor.extract(config["input_path"])

        # 2. Load policies for orphan check
        df_policies = None
        if config.get("policies_path"):
            df_policies = spark.read \
                .option("header", "true") \
                .csv(config["policies_path"])

        # 3. Validate + Quarantine (bad data separated, pipeline continues)
        df_clean, df_quarantine = processor.validate_and_quarantine(df_raw, df_policies)

        # 4. Save quarantine for investigation
        processor.save_quarantine(df_quarantine, config["quarantine_path"])

        # 5. Transform clean data
        df_final = processor.transform(df_clean)

        # 6. Load
        if config.get("snowflake"):
            processor.load_to_snowflake(df_final, config.get("output_table", "RAW.glue_claims"))
        else:
            processor.load_to_local(df_final, config["output_path"])

        # 7. Metrics
        metrics = processor.get_metrics()
        logger.info("JOB COMPLETE: input=%d clean=%d quarantined=%d output=%d",
                     metrics["input_rows"], metrics["clean_rows"],
                     metrics["quarantined_rows"], metrics["output_rows"])
        logger.info("Quarantine reasons: %s", metrics["quarantine_reasons"])

        return metrics

    except Exception as e:
        logger.error("Job failed: %s", e)
        raise
    finally:
        spark.stop()


# ============================================================
# MAIN — CLI entry point
# ============================================================

def main():
    """
    Entry point for standalone execution.
    In real Glue:
        args = getResolvedOptions(sys.argv, [
            'JOB_NAME', 'input_path', 'output_table',
            'quarantine_path', 'policies_path'
        ])
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    config = {
        "input_path": "data/raw/raw_claims.csv",
        "policies_path": "data/raw/raw_policies.csv",
        "output_path": "data/processed/claims.csv",
        "quarantine_path": "data/quarantine/claims.csv",
    }

    # Override from command line if provided
    if len(sys.argv) > 1:
        config["input_path"] = sys.argv[1]

    metrics = run_job(config)

    print(f"\n{'='*50}")
    print(f"JOB COMPLETE")
    print(f"  Input:       {metrics['input_rows']}")
    print(f"  Clean:       {metrics['clean_rows']}")
    print(f"  Quarantined: {metrics['quarantined_rows']}")
    print(f"  Output:      {metrics['output_rows']}")
    print(f"  Reasons:     {metrics['quarantine_reasons']}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
