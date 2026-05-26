"""
Job Metadata Tracker — DynamoDB (or local JSON fallback).

Production pattern:
  Every Glue job writes metadata to DynamoDB:
  - job_name, run_id, status, start/end times
  - row counts (input, output, quarantined)
  - quality check results
  - error messages if failed

Why DynamoDB:
  - Serverless — no infra to manage
  - Fast writes — sub-millisecond
  - Airflow can query it to check job status
  - Dashboard/alerting reads from it

In real AWS:
  import boto3
  dynamo = boto3.resource('dynamodb')
  table = dynamo.Table('glue_job_tracking')
"""
import json
import os
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path


class JobTracker:
    """
    Track job execution metadata.

    In production: DynamoDB writes.
    Locally: JSON file for testing.

    Usage:
        tracker = JobTracker("process_claims", run_id="2024-01-01-001")
        tracker.start()
        tracker.update_metrics({"input_rows": 100, "output_rows": 95})
        tracker.add_quality_results(checker.get_results())
        tracker.complete()  # or tracker.fail("error message")
    """

    def __init__(self, job_name: str, run_id: Optional[str] = None,
                 use_dynamo: bool = False, local_path: str = "data/tracking"):
        self.job_name = job_name
        self.run_id = run_id or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.use_dynamo = use_dynamo
        self.local_path = local_path

        self.record = {
            "job_name": self.job_name,
            "run_id": self.run_id,
            "status": "initialized",
            "start_time": None,
            "end_time": None,
            "duration_seconds": None,
            "metrics": {},
            "quality_results": [],
            "quality_passed": None,
            "error_message": None,
            "created_at": datetime.utcnow().isoformat(),
        }

    def start(self):
        """Mark job started."""
        self.record["status"] = "running"
        self.record["start_time"] = datetime.utcnow().isoformat()
        self._save()
        print(f"[TRACKER] Job {self.job_name} started (run_id: {self.run_id})")

    def update_metrics(self, metrics: Dict):
        """Add/update metrics (row counts, etc)."""
        self.record["metrics"].update(metrics)
        self._save()

    def add_quality_results(self, results: list):
        """Store quality check results."""
        self.record["quality_results"] = results
        self.record["quality_passed"] = all(r.get("passed", False) for r in results)
        self._save()

    def complete(self):
        """Mark job completed successfully."""
        self.record["status"] = "completed"
        self.record["end_time"] = datetime.utcnow().isoformat()
        self._calc_duration()
        self._save()
        print(f"[TRACKER] Job {self.job_name} completed "
              f"(duration: {self.record['duration_seconds']}s)")

    def fail(self, error_message: str):
        """Mark job failed with error."""
        self.record["status"] = "failed"
        self.record["end_time"] = datetime.utcnow().isoformat()
        self.record["error_message"] = error_message
        self._calc_duration()
        self._save()
        print(f"[TRACKER] Job {self.job_name} FAILED: {error_message}")

    def get_record(self) -> Dict:
        """Return full tracking record."""
        return self.record

    # ============================================================
    # PERSISTENCE
    # ============================================================

    def _calc_duration(self):
        """Calculate duration in seconds."""
        if self.record["start_time"] and self.record["end_time"]:
            start = datetime.fromisoformat(self.record["start_time"])
            end = datetime.fromisoformat(self.record["end_time"])
            self.record["duration_seconds"] = (end - start).total_seconds()

    def _save(self):
        """Save to DynamoDB or local JSON."""
        if self.use_dynamo:
            self._save_to_dynamo()
        else:
            self._save_to_local()

    def _save_to_local(self):
        """Save tracking record as JSON file."""
        Path(self.local_path).mkdir(parents=True, exist_ok=True)
        filepath = os.path.join(
            self.local_path, f"{self.job_name}_{self.run_id}.json"
        )
        with open(filepath, "w") as f:
            json.dump(self.record, f, indent=2, default=str)

    def _save_to_dynamo(self):
        """
        Save to DynamoDB.

        In production:
            import boto3
            dynamo = boto3.resource('dynamodb')
            table = dynamo.Table('glue_job_tracking')
            table.put_item(Item=self.record)

        DynamoDB table design:
            Partition Key: job_name (String)
            Sort Key: run_id (String)
            GSI: status-index on status field (for querying failed jobs)
        """
        # Simulated — would be boto3 call
        print(f"[TRACKER] Would write to DynamoDB: {self.job_name}/{self.run_id}")
        # Fallback to local so we can verify
        self._save_to_local()
