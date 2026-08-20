from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


SOURCE_FILE = "/opt/airflow/dags/Vessels_Silver_layer/bronze_to_silver_vessels.py"

REMOTE_USER = "user"
REMOTE_HOST = "worker4"
REMOTE_DIR = "/home/user/notebooks/SILVER"
REMOTE_FILE = f"{REMOTE_DIR}/silver_vessels.py"

START_DATE = "2026/08/01"
END_DATE = "2026/08/30"


with DAG(
    dag_id="vessels_bronze_to_silver",
    start_date=datetime(2026, 8, 20),
    schedule=None,
    catchup=False,
    tags=["vessels", "silver"],
) as dag:

    copy_vessels_job = BashOperator(
        task_id="copy_vessels_job_to_worker4",
        bash_command=f"""
            set -e

            echo "Creating remote directory..."
            ssh {REMOTE_USER}@{REMOTE_HOST} \
                "mkdir -p {REMOTE_DIR}"

            echo "Copying Silver vessels job..."
            scp {SOURCE_FILE} \
                {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_FILE}

            echo "Copy completed successfully."
        """,
    )

    run_vessels_job = BashOperator(
        task_id="run_vessels_silver_job",
        bash_command=f"""
            set -e

            echo "Running Silver vessels Spark job..."

            ssh {REMOTE_USER}@{REMOTE_HOST} \
                "cd {REMOTE_DIR} && \
                 spark-submit silver_vessels.py \
                 {START_DATE} \
                 {END_DATE}"

            echo "Silver vessels job completed successfully."
        """,
    )

    copy_vessels_job >> run_vessels_job