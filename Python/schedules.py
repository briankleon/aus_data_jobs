from dagster import schedule
from jobs_pipeline import job_pipeline
from datetime import datetime, timedelta

@schedule(
    cron_schedule="0 18 */3 * *",  # Runs every 3rd day at 6 PM
    job=job_pipeline,
    execution_timezone="Australia/Melbourne",
)
def job_schedule():
    """Schedule the job every 3 days at 6 PM."""
    return {}
