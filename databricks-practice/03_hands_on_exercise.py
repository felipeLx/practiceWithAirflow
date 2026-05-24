# Databricks notebook source
# MAGIC %md
# MAGIC # Hands-On Exercise: Build a Complete Pipeline
# MAGIC ## Scenario: Financial Transaction Pipeline (your domain!)
# MAGIC
# MAGIC **Goal**: Build a complete Bronze → Silver → Gold pipeline
# MAGIC that processes financial transactions.
# MAGIC
# MAGIC Upload this notebook to Databricks Community Edition and run it.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Create Bronze Layer (Raw Ingestion)

# COMMAND ----------

from pyspark.sql.types import *
from pyspark.sql.functions import *

# Simulate raw transaction data (in real life, this comes from AutoLoader)
raw_data = [
    ("TXN001", "C100", 5000.00, "BRL", "pix", "2025-01-15", "completed", "bank_a"),
    ("TXN002", "C101", 12000.00, "BRL", "ted", "2025-01-15", "completed", "bank_b"),
    ("TXN003", "C100", 3500.00, "BRL", "pix", "2025-01-16", "pending", "bank_a"),
    ("TXN004", "C102", -500.00, "BRL", "pix", "2025-01-16", "completed", "bank_a"),  # negative = bad data
    ("TXN005", "C101", 8000.00, "BRL", "boleto", "2025-01-17", "completed", "bank_c"),
    ("TXN001", "C100", 5000.00, "BRL", "pix", "2025-01-15", "completed", "bank_a"),  # duplicate!
    ("TXN006", "C103", None, "BRL", "ted", "2025-01-17", "failed", "bank_b"),  # null amount
    ("TXN007", "C104", 25000.00, "USD", "wire", "2025-01-18", "completed", "bank_d"),
    ("TXN008", "C100", 1200.00, "BRL", "pix", "2025-01-18", "completed", "bank_a"),
    ("TXN009", "C105", 45000.00, "EUR", "swift", "2025-01-19", "completed", "bank_e"),
]

schema = StructType([
    StructField("transaction_id", StringType()),
    StructField("customer_id", StringType()),
    StructField("amount", DoubleType()),
    StructField("currency", StringType()),
    StructField("payment_method", StringType()),
    StructField("transaction_date", StringType()),
    StructField("status", StringType()),
    StructField("source_bank", StringType()),
])

bronze_df = spark.createDataFrame(raw_data, schema) \
    .withColumn("_ingestion_timestamp", current_timestamp()) \
    .withColumn("_source_file", lit("batch_2025_01.json"))

bronze_df.write.format("delta").mode("overwrite").saveAsTable("bronze_financial_transactions")
print(f"Bronze: {bronze_df.count()} records ingested")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Create Silver Layer (Clean + Validate)

# COMMAND ----------

silver_df = (
    spark.table("bronze_financial_transactions")
    # Remove duplicates
    .dropDuplicates(["transaction_id"])
    # Remove nulls in critical fields
    .filter(col("amount").isNotNull())
    # Remove invalid amounts
    .filter(col("amount") > 0)
    # Remove failed transactions
    .filter(col("status") != "failed")
    # Type casting
    .withColumn("transaction_date", to_date(col("transaction_date")))
    # Standardize currency to USD
    .withColumn("amount_usd",
        when(col("currency") == "BRL", round(col("amount") / 5.65, 2))
        .when(col("currency") == "EUR", round(col("amount") * 1.08, 2))
        .otherwise(col("amount"))
    )
    # Add processing metadata
    .withColumn("_processed_timestamp", current_timestamp())
)

silver_df.write.format("delta").mode("overwrite").saveAsTable("silver_financial_transactions")
print(f"Silver: {silver_df.count()} records after cleaning")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Verify data quality: what got filtered out?
# MAGIC SELECT
# MAGIC     (SELECT COUNT(*) FROM bronze_financial_transactions) as bronze_count,
# MAGIC     (SELECT COUNT(*) FROM silver_financial_transactions) as silver_count,
# MAGIC     (SELECT COUNT(*) FROM bronze_financial_transactions) -
# MAGIC     (SELECT COUNT(*) FROM silver_financial_transactions) as records_filtered

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Create Gold Layer (Business Aggregations)

# COMMAND ----------

# Gold 1: Customer Summary
spark.sql("""
    CREATE OR REPLACE TABLE gold_customer_transactions AS
    SELECT
        customer_id,
        COUNT(*) as total_transactions,
        ROUND(SUM(amount_usd), 2) as total_volume_usd,
        ROUND(AVG(amount_usd), 2) as avg_transaction_usd,
        MIN(transaction_date) as first_transaction,
        MAX(transaction_date) as last_transaction,
        COUNT(DISTINCT payment_method) as payment_methods_used,
        COUNT(DISTINCT source_bank) as banks_used
    FROM silver_financial_transactions
    GROUP BY customer_id
""")

# Gold 2: Daily Volume
spark.sql("""
    CREATE OR REPLACE TABLE gold_daily_volume AS
    SELECT
        transaction_date,
        payment_method,
        COUNT(*) as num_transactions,
        ROUND(SUM(amount_usd), 2) as total_volume_usd,
        ROUND(AVG(amount_usd), 2) as avg_amount_usd
    FROM silver_financial_transactions
    GROUP BY transaction_date, payment_method
    ORDER BY transaction_date, payment_method
""")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Business-ready query (this feeds Power BI / dashboards)
# MAGIC SELECT * FROM gold_customer_transactions ORDER BY total_volume_usd DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM gold_daily_volume

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Delta Lake Features (show in interviews!)

# COMMAND ----------

# Time Travel - see previous versions
spark.sql("DESCRIBE HISTORY silver_financial_transactions").show(truncate=False)

# COMMAND ----------

# OPTIMIZE - compact small files (important for performance)
spark.sql("OPTIMIZE silver_financial_transactions")

# COMMAND ----------

# VACUUM - clean up old files (save storage costs)
# spark.sql("VACUUM silver_financial_transactions RETAIN 168 HOURS")

# COMMAND ----------

# Schema Evolution - add new column without breaking anything
spark.sql("""
    ALTER TABLE silver_financial_transactions
    ADD COLUMNS (risk_score DOUBLE)
""")

# COMMAND ----------

# MERGE (Upsert) - key operation for incremental loads
new_data = [
    ("TXN003", "C100", 3500.00, "BRL", "pix", "2025-01-16", "completed", "bank_a"),  # update status
    ("TXN010", "C106", 7500.00, "BRL", "pix", "2025-01-20", "completed", "bank_a"),  # new record
]

updates_df = spark.createDataFrame(new_data, schema) \
    .withColumn("transaction_date", to_date(col("transaction_date"))) \
    .withColumn("amount_usd", round(col("amount") / 5.65, 2)) \
    .withColumn("_processed_timestamp", current_timestamp())

updates_df.createOrReplaceTempView("updates")

spark.sql("""
    MERGE INTO silver_financial_transactions AS target
    USING updates AS source
    ON target.transaction_id = source.transaction_id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Congratulations!
# MAGIC
# MAGIC You just built a complete Databricks pipeline:
# MAGIC - ✅ Bronze → Silver → Gold (Medallion Architecture)
# MAGIC - ✅ Delta Lake (ACID, Time Travel, Schema Evolution)
# MAGIC - ✅ Data Quality (filtering, dedup, validation)
# MAGIC - ✅ MERGE / Upsert (incremental processing)
# MAGIC - ✅ OPTIMIZE / VACUUM (performance tuning)
# MAGIC - ✅ Financial domain data (your expertise!)
# MAGIC
# MAGIC **Next steps:**
# MAGIC 1. Sign up at https://community.cloud.databricks.com
# MAGIC 2. Import this notebook
# MAGIC 3. Run it cell by cell
# MAGIC 4. Modify it — add more transformations, try different queries
# MAGIC 5. You're ready to talk Databricks in interviews!
