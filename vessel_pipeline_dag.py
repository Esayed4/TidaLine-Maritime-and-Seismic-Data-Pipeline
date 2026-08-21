from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from vessels_ingestion_layer.sftp_vessels_client import main
from vessels_ingestion_layer.hdfs_vessels_client import upload_vessels_to_hdfs
from vessels_ingestion_layer.cleanAndArchive import cleanup_and_archive

# ============================================================
# Configuration & Variables
# ============================================================
START_DATE = datetime(2026, 8, 1).date()
END_DATE = datetime(2026, 8, 30).date()

START_DATE_STR = START_DATE.strftime("%Y/%m/%d")
END_DATE_STR = END_DATE.strftime("%Y/%m/%d")

SOURCE_FILE = "/opt/airflow/dags/Vessels_Silver_layer/bronze_to_silver_vessels.py"
REMOTE_USER = "user"
REMOTE_HOST = "worker4"
REMOTE_DIR = "/home/user/notebooks/SILVER"
REMOTE_FILE = f"{REMOTE_DIR}/silver_vessels.py"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

# ============================================================
# Python Callables
# ============================================================
def run_vessel_ingestion():
    main(START_DATE, END_DATE)

def upload_vessels():
    uploaded_files = upload_vessels_to_hdfs(START_DATE, END_DATE)
    print(f"Uploaded {len(uploaded_files)} files to HDFS.")

def run_vessel_cleanup():
    cleanup_and_archive(START_DATE, END_DATE)

# ============================================================
# DAG Definition
# ============================================================
with DAG(
    dag_id="vessel_pipeline_end_to_end",
    default_args=default_args,
    start_date=datetime(2026, 8, 1),
    schedule="@daily",
    catchup=False,
    tags=["vessels", "pipeline"],
) as dag:

    # Task 1: Download files via SFTP
    ingest_vessels = PythonOperator(
        task_id="download_vessel_files",
        python_callable=run_vessel_ingestion,
    )

    # Task 2: Upload downloaded files to HDFS
    upload_vessels_to_hdfs = PythonOperator(
        task_id="upload_vessels_to_hdfs",
        python_callable=upload_vessels,
    )

    # Task 3: Cleanup and Archive local temp files
    cleanup_vessels = PythonOperator(
        task_id="cleanup_and_archive_vessel_files",
        python_callable=run_vessel_cleanup,
    )

    # Task 4a: Copy script to remote worker
    copy_vessels_job = BashOperator(
        task_id="copy_vessels_job_to_worker4",
        bash_command=f"""
            set -e
            echo "Creating remote directory..."
            ssh {REMOTE_USER}@{REMOTE_HOST} "mkdir -p {REMOTE_DIR}"
            echo "Copying Silver vessels job..."
            scp {SOURCE_FILE} {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_FILE}
            echo "Copy completed successfully."
        """,
    )

    # Task 4b: Execute Spark job on remote worker using the date variables
    run_vessels_silver_job = BashOperator(
        task_id="run_vessels_silver_job",
        bash_command=f"""
            set -e
            echo "Running Silver vessels Spark job..."

            ssh {REMOTE_USER}@{REMOTE_HOST} "
                cd {REMOTE_DIR} &&
                /opt/spark/bin/spark-submit silver_vessels.py {START_DATE_STR} {END_DATE_STR}
            "

            echo "Silver vessels job completed successfully."
        """,
    )

    # Execution Sequence
    ingest_vessels >> upload_vessels_to_hdfs >> cleanup_vessels >> copy_vessels_job >> run_vessels_silver_job