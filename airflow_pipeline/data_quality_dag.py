import os
import sys
from datetime import datetime

# Ensure the repo root is on PYTHONPATH so `main.py` can be imported
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from airflow import DAG
from airflow.operators.python import PythonOperator
from main import run_pipeline

def run():
    sample_path = os.path.join(ROOT_DIR, "data", "raw", "sample.csv")
    run_pipeline(sample_path)

with DAG(
    "data_quality_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    task = PythonOperator(
        task_id="run_pipeline",
        python_callable=run,
    )