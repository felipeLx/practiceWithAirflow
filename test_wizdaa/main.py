"""
1. Incremental & Idempotent Upsert (Python)
Input
existing_table = [
{"id": 1, "value": 10, "updated_at": "2024-01-01T10:00:00"},
{"id": 2, "value": 20, "updated_at": "2024-01-02T10:00:00"},
]
incoming_batch = [
{"id": 2, "value": 25, "updated_at": "2024-01-03T09:00:00"},
{"id": 3, "value": 30, "updated_at": "2024-01-03T09:05:00"},
]
Description
Implement a Python function that merges the incoming batch into the existing dataset.
Requirements:
● Use id as the primary key
● Keep only the most recent record per id using updated_at
● The function must be idempotent
Return the updated dataset as a list of dictionaries
"""
from spark.sql import Window
from spark.functions import row_number, col


def merge_batchs(income_batch: dict, existing_df: dict) -> dict:

    registers = {r["id"]: r for r in existing_df}

    for register in income_batch:
        existing = registers.get(register["id"])
        if not existing or register["updated_at"] > existing["updated_at"]:
            registers[register["id"]] = register
    
    
    return sorted(registers.values(), key=lambda x: x["id"])

