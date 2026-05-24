# Databricks notebook source
# MAGIC %md
# MAGIC # Databricks Fundamentals - Practice Notebook
# MAGIC ## Felipe Lisboa - Learning Path
# MAGIC
# MAGIC ### What you ALREADY know (from PySpark/AWS):
# MAGIC - PySpark DataFrames, transformations, actions ✅
# MAGIC - SQL queries ✅
# MAGIC - S3/cloud storage ✅
# MAGIC - ETL pipeline design ✅
# MAGIC - Apache Iceberg (similar to Delta Lake) ✅
# MAGIC
# MAGIC ### What you need to learn (Databricks-specific):
# MAGIC 1. Delta Lake (table format, ACID transactions, time travel)
# MAGIC 2. Medallion Architecture (Bronze → Silver → Gold)
# MAGIC 3. Unity Catalog (governance)
# MAGIC 4. Databricks Workflows (orchestration)
# MAGIC 5. Databricks SQL (warehouses, dashboards)
# MAGIC 6. AutoLoader (streaming ingestion)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Delta Lake Basics
# MAGIC Delta Lake is like Apache Iceberg (you know this!) but Databricks-native.
# MAGIC Both provide: ACID transactions, schema evolution, time travel.

# COMMAND ----------

# Creating a Delta table (this is what you do with Iceberg, same concept)
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType
from pyspark.sql.functions import col, current_date, lit, when

# Sample financial data (your domain!)
schema = StructType([
    StructField("transaction_id", StringType(), False),
    StructField("customer_id", StringType(), False),
    StructField("amount", DoubleType(), False),
    StructField("currency", StringType(), False),
    StructField("transaction_type", StringType(), False),
    StructField("status", StringType(), False),
])

data = [
    ("TXN001", "C001", 1500.00, "BRL", "credit", "completed"),
    ("TXN002", "C002", 3200.50, "USD", "debit", "completed"),
    ("TXN003", "C001", 750.00, "BRL", "credit", "pending"),
    ("TXN004", "C003", 12000.00, "EUR", "transfer", "completed"),
    ("TXN005", "C002", 500.00, "BRL", "debit", "failed"),
]

df = spark.createDataFrame(data, schema)

# Write as Delta table (instead of Iceberg, you write Delta)
df.write.format("delta").mode("overwrite").saveAsTable("transactions")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Delta Lake Time Travel
# MAGIC This is like Iceberg snapshots — you can query previous versions

# COMMAND ----------

# Query current version
spark.sql("SELECT * FROM transactions").show()

# Update some records
spark.sql("""
    UPDATE transactions
    SET status = 'reversed'
    WHERE transaction_id = 'TXN005'
""")

# Time travel - query PREVIOUS version (before update)
spark.sql("SELECT * FROM transactions VERSION AS OF 0").show()

# See history of changes
spark.sql("DESCRIBE HISTORY transactions").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Medallion Architecture (Bronze → Silver → Gold)
# MAGIC This is THE key concept in Databricks interviews.
# MAGIC
# MAGIC - **Bronze**: Raw data, as-is from source (like your raw S3 layer)
# MAGIC - **Silver**: Cleaned, validated, deduplicated (like your processed layer)
# MAGIC - **Gold**: Business-level aggregations, ready for BI (like your curated layer)
# MAGIC
# MAGIC You already do this! Just different names.

# COMMAND ----------

# BRONZE layer - raw ingestion (you do this with S3 + PySpark today)
bronze_df = df.withColumn("ingestion_date", current_date()) \
              .withColumn("source_system", lit("payment_gateway"))

bronze_df.write.format("delta").mode("overwrite").saveAsTable("bronze_transactions")

# COMMAND ----------

# SILVER layer - cleaned and validated
silver_df = spark.table("bronze_transactions") \
    .filter(col("status") != "failed") \
    .dropDuplicates(["transaction_id"]) \
    .withColumn("amount_usd",
        when(col("currency") == "BRL", col("amount") / 5.65)
        .when(col("currency") == "EUR", col("amount") * 1.08)
        .otherwise(col("amount"))
    )

silver_df.write.format("delta").mode("overwrite").saveAsTable("silver_transactions")

# COMMAND ----------

# GOLD layer - business aggregations (ready for Power BI / dashboards)
gold_df = spark.sql("""
    SELECT
        customer_id,
        COUNT(*) as total_transactions,
        SUM(amount_usd) as total_amount_usd,
        AVG(amount_usd) as avg_amount_usd,
        COUNT(CASE WHEN transaction_type = 'credit' THEN 1 END) as credit_count,
        COUNT(CASE WHEN transaction_type = 'debit' THEN 1 END) as debit_count
    FROM silver_transactions
    GROUP BY customer_id
""")

gold_df.write.format("delta").mode("overwrite").saveAsTable("gold_customer_summary")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. AutoLoader (Streaming Ingestion)
# MAGIC AutoLoader = automatic file ingestion from cloud storage.
# MAGIC Like watching an S3 bucket for new files — but Databricks-native.

# COMMAND ----------

# AutoLoader example (use in Databricks, not locally)
# This watches a folder and automatically ingests new files
"""
df_stream = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/mnt/schema/transactions")
    .load("/mnt/data/raw/transactions/")
)

df_stream.writeStream \
    .format("delta") \
    .option("checkpointLocation", "/mnt/checkpoints/transactions") \
    .outputMode("append") \
    .toTable("bronze_transactions_stream")
"""

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Databricks SQL
# MAGIC Same SQL you already write — just runs on Databricks SQL Warehouses.
# MAGIC Key difference: serverless compute, pay per query.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- This is standard SQL (you know this!)
# MAGIC -- In Databricks, this runs on a SQL Warehouse
# MAGIC
# MAGIC SELECT
# MAGIC     t.customer_id,
# MAGIC     t.transaction_type,
# MAGIC     t.amount,
# MAGIC     t.currency,
# MAGIC     g.total_amount_usd,
# MAGIC     g.total_transactions
# MAGIC FROM silver_transactions t
# MAGIC JOIN gold_customer_summary g ON t.customer_id = g.customer_id
# MAGIC ORDER BY g.total_amount_usd DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Unity Catalog (Governance)
# MAGIC Three-level namespace: catalog.schema.table
# MAGIC Like a data catalog for security, lineage, and access control.

# COMMAND ----------

# Unity Catalog structure:
# catalog_name.schema_name.table_name
# Example: production.finance.transactions

"""
-- Create catalog
CREATE CATALOG IF NOT EXISTS production;

-- Create schema
CREATE SCHEMA IF NOT EXISTS production.finance;

-- Create table in catalog
CREATE TABLE production.finance.transactions AS
SELECT * FROM silver_transactions;

-- Grant access (governance!)
GRANT SELECT ON TABLE production.finance.transactions TO `analysts`;
"""
