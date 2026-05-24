# Databricks Interview Questions - Study Guide

## Questions You WILL Get (and how to answer)

### 1. "What is Delta Lake?"
**Your answer:** "Delta Lake is an open-source storage layer that brings ACID transactions to data lakes. It's similar to Apache Iceberg — which I use in production — providing schema enforcement, time travel, and data versioning. The key difference is Delta Lake is Databricks-native and tightly integrated with the platform."

### 2. "Explain the Medallion Architecture"
**Your answer:** "It's a data design pattern with three layers:
- **Bronze**: Raw data, ingested as-is from source systems. No transformations.
- **Silver**: Cleaned, validated, deduplicated. Business rules applied.
- **Gold**: Aggregated, business-ready tables optimized for analytics and BI.

In my current work, I use an equivalent pattern on AWS in S3. Same concept, different naming."

### 3. "What's the difference between Delta Lake and Apache Iceberg?"
**Your answer:** "Both are open table formats providing ACID transactions, time travel, and schema evolution. Delta Lake is Databricks-native with tighter integration. Iceberg is vendor-neutral and works across engines (Spark, Flink, Trino). I work with Iceberg in production on AWS EMR, so the concepts transfer directly — partitioning, snapshot management, metadata handling."

### 4. "How do you handle slowly changing dimensions (SCD) in Delta Lake?"
**Your answer:** "Delta Lake supports MERGE INTO which makes SCD Type 2 straightforward:
```sql
MERGE INTO target USING source
ON target.id = source.id
WHEN MATCHED AND target.value != source.value THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...
```
This is similar to how I handle upserts with Iceberg using MERGE."

### 5. "What is AutoLoader?"
**Your answer:** "AutoLoader is Databricks' streaming ingestion tool that automatically detects and processes new files arriving in cloud storage. It uses Structured Streaming under the hood with cloudFiles format. It handles schema inference, evolution, and exactly-once processing. It's the Databricks equivalent of watching an S3 bucket for new files — which I do in my current pipelines."

### 6. "What is Unity Catalog?"
**Your answer:** "Unity Catalog is Databricks' governance layer. It provides a three-level namespace (catalog.schema.table), centralized access control, data lineage tracking, and audit logging. It's how you manage who can access what data across the organization."

### 7. "How do you optimize Delta tables?"
**Your answer:**
- **OPTIMIZE**: Compacts small files into larger ones (similar to Iceberg compaction)
- **Z-ORDER**: Co-locates related data for faster queries (like Iceberg sort orders)
- **VACUUM**: Removes old files no longer referenced (like Iceberg snapshot expiration)
- **Liquid Clustering**: Modern replacement for partitioning + Z-ORDER
- **Photon**: Databricks' native query engine for faster execution

### 8. "Explain Structured Streaming in Databricks"
**Your answer:** "Structured Streaming treats streaming data as a continuously appended table. You write the same DataFrame/SQL code for batch and streaming — the engine handles the incremental processing. Combined with Delta Lake as the sink, you get exactly-once guarantees and the ability to query streaming data with regular SQL."

### 9. "What's the difference between a Job and a Workflow in Databricks?"
**Your answer:** "A Workflow orchestrates multiple tasks (notebooks, Python scripts, SQL queries) with dependencies, retries, and scheduling. It's Databricks' built-in alternative to Airflow. A Job is a single task within a workflow. Workflows support conditional logic, parallel execution, and alerts."

### 10. "How do you handle data quality?"
**Your answer:** "Databricks offers Delta Live Tables with Expectations — declarative data quality rules:
```python
@dlt.expect_or_drop('valid_amount', 'amount > 0')
@dlt.expect_or_fail('valid_currency', "currency IN ('BRL','USD','EUR')")
```
This is similar to Great Expectations but native to Databricks. In my current work, I implement validation checks in my PySpark pipelines before writing to production tables."

---

## Your Cheat Sheet: Databricks ↔ What You Already Know

| Databricks | What you use today | Notes |
|---|---|---|
| Delta Lake | Apache Iceberg | Same concept, different format |
| Medallion (Bronze/Silver/Gold) | Raw/Processed/Curated S3 layers | Same pattern |
| AutoLoader | S3 event triggers + PySpark | Databricks-native |
| Unity Catalog | IAM + Glue Catalog | Governance layer |
| Databricks Workflows | Manual orchestration / scripts | Like Airflow |
| Databricks SQL Warehouse | Athena | Serverless SQL |
| Delta Live Tables (DLT) | PySpark pipeline code | Declarative pipelines |
| DBFS / Volumes | S3 buckets | Storage |
| Photon engine | Spark engine | Faster native engine |
| Liquid Clustering | Partitioning + sort | Modern optimization |

---

## Free Resources to Practice

1. **Databricks Community Edition** (FREE):
   https://community.cloud.databricks.com
   - Real Databricks workspace
   - Run notebooks with Spark
   - Practice Delta Lake, SQL, PySpark
   - Limited but enough to learn

2. **Databricks Academy** (FREE courses):
   - "Data Engineering with Databricks"
   - "Delta Lake Fundamentals"
   - "Databricks SQL"

3. **Databricks Certified Data Engineer Associate**:
   - Good certification to add to CV
   - Study guide available free
   - Exam: ~$200 USD
