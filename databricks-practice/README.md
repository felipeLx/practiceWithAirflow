# Databricks Practice Workspace

This repository is a focused practice folder for a senior data engineer who already knows Python, SQL, and PySpark and wants to become productive in Databricks fast.

The goal is not to relearn Spark. The goal is to map what you already know into Databricks-specific concepts, workflows, and interview language.

## What is in this folder

- `01_databricks_fundamentals.py`: core concepts and examples in Databricks notebook export format
- `02_interview_questions.md`: interview answers and concept mapping
- `03_hands_on_exercise.py`: end-to-end Bronze -> Silver -> Gold pipeline exercise

These `.py` files are exported Databricks notebooks. You can import them directly into your Databricks workspace.

## Recommended learning objective

Given your background, focus on these gaps first:

1. Delta Lake operations and table lifecycle
2. Medallion architecture in Databricks terms
3. Databricks workspace usage: notebooks, SQL, compute, catalogs, jobs
4. Databricks-native features: Auto Loader, Workflows, Unity Catalog, DLT
5. Interview positioning: connecting Databricks to your existing PySpark and Iceberg experience

## Prerequisites

- A Databricks Community account
- Access to your Databricks workspace in the browser
- This local project folder cloned or available on your machine

## How to deploy this project to Databricks Community Edition

Use the workspace import flow. That is the simplest option for these files.

### Option 1: Import the files directly into Workspace

1. Open your Databricks Community workspace.
2. In the left sidebar, open `Workspace`.
3. Create a folder such as `Users/<your-user>/databricks-practice`.
4. Use the workspace import action.
5. Import `01_databricks_fundamentals.py`.
6. Import `03_hands_on_exercise.py`.
7. Optionally keep `02_interview_questions.md` locally, or paste it into a Databricks notebook or personal notes.

Databricks should recognize the Python notebook export format because the files start with `# Databricks notebook source`.

### Option 2: Copy notebook content into a new notebook

Use this only if import is unavailable in your Community workspace.

1. Create a new Python notebook in Databricks.
2. Open one of the local `.py` files.
3. Copy all content.
4. Paste it into the Databricks notebook.
5. Save and run cell by cell.

## First-time Databricks workspace setup

After login, do the following once:

1. Create or start a compute resource if your workspace asks for one.
2. Attach the notebook to that compute.
3. Confirm the notebook language is Python.
4. Run a simple validation cell such as:

```python
spark.range(5).show()
```

If that works, your environment is ready.

## Suggested study order

Follow this order so you learn platform concepts before doing the full exercise.

## Learning timeline

Use this as a practical 2-week ramp-up instead of trying to learn the whole platform at once.

### Week 1: Platform and Delta foundations

Day 1

1. Import the notebooks into Databricks Community Edition.
2. Run a simple `spark.range(5).show()` test.
3. Learn the difference between notebook, cluster/compute, table, and view.

Day 2

1. Run the Delta Lake basics section in `01_databricks_fundamentals.py`.
2. Focus on `saveAsTable`, `UPDATE`, `DESCRIBE HISTORY`, and time travel.
3. Compare Delta Lake with Iceberg based on what you already know.

Day 3

1. Run the Bronze -> Silver -> Gold sections.
2. Translate medallion architecture into your current raw/processed/curated mental model.
3. Write down the business reason for each layer.

Day 4

1. Review Databricks SQL, SQL Warehouses, and compute types.
2. Understand when people say "pay per query" and when they really mean warehouse compute billing.
3. Read the FAQ section below before continuing.

Day 5

1. Run the hands-on exercise end to end.
2. Inspect every persisted table after each step.
3. Practice explaining the pipeline out loud.

### Week 2: Incremental patterns and interview depth

Day 6

1. Re-run the Silver logic with modified rules.
2. Add one more validation rule.
3. Explain why some records are filtered before Gold.

Day 7

1. Focus on `MERGE INTO` in the hands-on exercise.
2. Understand source vs target, matched vs not matched, and what is rewritten.
3. Connect `MERGE` to your prior incremental ETL experience.

Day 8

1. Review temporary views versus persisted tables.
2. Practice switching between DataFrame API and SQL.
3. Make sure you can explain why both styles are often mixed in Databricks.

Day 9

1. Review `OPTIMIZE`, `VACUUM`, schema evolution, and table maintenance.
2. Learn what is performance-related versus storage-related.
3. Practice explaining file compaction in plain language.

Day 10

1. Read `02_interview_questions.md`.
2. Rewrite the answers in your own words.
3. Build a 2-minute Databricks story tied to your Python, SQL, and PySpark background.

### Step 1: Fundamentals

Run `01_databricks_fundamentals.py` first.

Focus on understanding:

- Delta Lake basics
- Time travel
- Bronze, Silver, Gold layers
- Auto Loader conceptually
- Databricks SQL
- Unity Catalog terminology

What to compare with your existing background:

- Delta Lake vs Iceberg
- Medallion vs raw/processed/curated layers
- Auto Loader vs S3-triggered ingestion patterns
- Unity Catalog vs Glue Catalog plus IAM-style governance

### Step 2: Hands-on pipeline

Run `03_hands_on_exercise.py` after the fundamentals notebook.

This is the most important file in the project because it gives you an interview-ready pipeline story:

- Bronze ingestion
- Silver validation and deduplication
- Gold aggregations
- Delta history
- `OPTIMIZE`
- schema evolution
- `MERGE INTO`

When running it, stop after each section and inspect the tables with SQL queries.

### Step 3: Interview prep

Read `02_interview_questions.md` after you complete the pipeline.

Do not memorize it word for word. Adapt the answers to your real experience:

- mention PySpark depth
- mention data modeling and ETL ownership
- mention your production knowledge of table formats
- explain Databricks as an extension of patterns you already use

## Daily practice plan

Use this 5-day loop to get useful job-market readiness quickly.

### Day 1

1. Import both notebooks.
2. Run the fundamentals notebook.
3. Write down every Databricks term that is new.

### Day 2

1. Run the hands-on exercise.
2. Re-run the Silver and Gold logic after changing business rules.
3. Practice explaining why records were filtered.

### Day 3

1. Modify the exercise to add a new column.
2. Add a new payment method or currency.
3. Create one more Gold aggregation for a business stakeholder.

### Day 4

1. Practice `MERGE`, `UPDATE`, `DELETE`, and history queries.
2. Explain Delta Lake features out loud as if you were in an interview.
3. Compare each feature to Iceberg or your current AWS stack.

### Day 5

1. Review the interview questions.
2. Build a two-minute summary of your Databricks learning journey.
3. Update your CV and LinkedIn with concrete wording.

## FAQ: concepts that usually cause confusion

### Do we pay for `MERGE INTO`?

Not as a special feature price. You pay for the compute that executes the workload.

- On an all-purpose cluster, the cost is tied to cluster runtime and DBU usage while the cluster is on.
- On a SQL Warehouse, people often describe it as pay per query because the warehouse compute runs the SQL workload.
- `MERGE INTO` is usually more expensive than a simple `SELECT` because it has to read data, match rows, and rewrite affected files in the Delta table.

For Community Edition, treat this as a learning concept, not a billing concern.

### Is data stored as a table or as Parquet?

In Databricks, a Delta table is normally stored as Parquet files plus Delta transaction log metadata.

- The table is the logical object you query.
- Parquet files hold the data.
- The `_delta_log` directory holds the transaction history and metadata.

So when you save a Delta table, you are usually still storing data in Parquet underneath.

### Why does `saveAsTable` not need a bucket path like Iceberg jobs often do?

Because `saveAsTable` is usually creating or writing to a managed table.

- In your Spark plus Iceberg jobs, you often define the storage path explicitly, such as an S3 bucket or object prefix.
- In Databricks, `saveAsTable("silver_financial_transactions")` tells Spark to register and store the data using the metastore and the platform's configured managed storage location.
- That means Databricks can decide the physical storage location for you instead of requiring a manual path in the notebook.

The right mental model is:

- `save("s3://bucket/path")` means you are writing files to an explicit path.
- `saveAsTable("table_name")` means you are writing a table object and the metastore resolves where managed data should live.

This is why the notebook looks simpler than a raw `spark-submit` pattern.

There are still two table styles to know:

- Managed table: Databricks or the metastore manages the storage location.
- External table: you point the table to an existing cloud storage location and keep storage ownership more explicit.

So `saveAsTable` is not magic. It is using metadata and default storage rules that the platform already knows.

### Why does the example use `tempView` instead of only PySpark DataFrame API?

Because Databricks workflows commonly mix both styles.

- `createOrReplaceTempView("updates")` does not persist data as a table.
- It creates a session-scoped SQL name for an in-memory DataFrame.
- That lets you use SQL syntax like `MERGE INTO`, which is often clearer for upserts.

The flow in the hands-on exercise is:

1. Build a DataFrame in PySpark.
2. Register it as a temporary view.
3. Use SQL to merge it into a persisted Delta table.

This is still ETL. It is not a different storage mode.

### When should I think in tables and when should I think in DataFrames?

Use DataFrames for transformation code and use tables for persisted data products.

- DataFrames are your programmatic transformation layer.
- Temporary views are a bridge between DataFrame code and SQL.
- Delta tables are persisted, governed, queryable assets.

That is why the notebook uses all three.

## Recommended video while studying

If you want one video track to keep running while you study, prioritize official Databricks content over generic tutorial channels.

Recommended starting point:

1. Search on YouTube for `Databricks Data Engineer Associate course Databricks` and prioritize recent videos from the official Databricks channel.

Why this is the best fit for you:

- It focuses on the platform vocabulary interviewers expect.
- It covers Delta Lake, medallion architecture, SQL, workflows, and governance.
- It is closer to how Databricks wants you to think than a random Spark tutorial.

How to use video time well:

1. Watch one concept block.
2. Reproduce the same idea in these notebooks.
3. Write one sentence comparing it to your AWS/PySpark/Iceberg experience.

If you want depth after that, your next video topic should be `Delta Lake MERGE INTO Databricks` because that is one of the most interview-relevant patterns in this project.

## Practical milestones to reach

You should consider this folder successful when you can do the following without notes:

1. Explain Bronze, Silver, and Gold clearly.
2. Show a Delta table write and a `MERGE INTO` example.
3. Explain time travel and table history.
4. Describe where Auto Loader fits in ingestion.
5. Explain Unity Catalog at a high level.
6. Tell an interview story that connects Databricks with your existing production experience.

## Resume and interview positioning

Use positioning like this:

> Senior Data Engineer with deep Python, SQL, and PySpark experience, now extending production-grade lakehouse patterns into Databricks. Strong background in data pipelines, table formats, and analytical data layers, with hands-on practice in Delta Lake, medallion architecture, and Databricks-native workflow patterns.

In interviews, avoid saying you are a beginner in distributed data. That is not true. You are mostly learning the Databricks platform surface area and its platform-native vocabulary.

## Common issues

### Notebook imported as plain Python file

Make sure you import the file into Databricks Workspace instead of just uploading it as a generic file. The file header should help Databricks recognize it as a notebook export.

### SQL commands fail

Make sure the notebook is attached to active compute before running SQL or Spark commands.

### Table already exists

This project mostly uses `overwrite` and `CREATE OR REPLACE`, so reruns should be safe. If needed, drop the practice tables and rerun the notebook from the top.

### Some Community Edition screens look different

Databricks changes UI details over time. If labels differ slightly, use the equivalent workspace import, notebook creation, and compute attachment actions.

## Next steps after this folder

Once you finish this project, the next useful additions are:

1. A streaming example with Auto Loader semantics
2. A small SQL Warehouse exercise
3. A Workflow job with task dependencies
4. A Unity Catalog example with catalog.schema.table naming
5. A Delta Live Tables example for data quality expectations

## Local usage

This repository is mainly for study material and notebook source control.

Suggested local workflow:

1. Keep notebooks versioned here.
2. Import to Databricks.
3. Practice in the Databricks UI.
4. Bring useful changes back into this repository.

## Quick start

If you want the shortest possible path:

1. Import `01_databricks_fundamentals.py` and `03_hands_on_exercise.py` into Databricks.
2. Attach compute.
3. Run `01` completely.
4. Run `03` completely.
5. Review `02_interview_questions.md` and adapt the answers to your own experience.