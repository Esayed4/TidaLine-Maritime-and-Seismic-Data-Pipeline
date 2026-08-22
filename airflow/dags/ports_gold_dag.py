from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.providers.standard.sensors.external_task import ExternalTaskSensor

default_args = {
    "owner": "maritime_data_eng",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="ports_monthly_gold_ingest",
    default_args=default_args,
    description="Monthly transformation of ports data from silver to gold layer",
    schedule="@monthly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["ports", "gold", "spark", "hive"],
) as dag:

    wait_for_silver = ExternalTaskSensor(
        task_id="wait_for_silver_ingest",
        external_dag_id="ports_monthly_silver_ingest",
        external_task_id="ports_bronze_to_silver",
        mode="reschedule",
        poke_interval=60,
        timeout=60 * 60 * 24,
        allowed_states=["success"],
        execution_date_fn=lambda dt: dt.replace(day=1),
    )

    gold_ingest = SSHOperator(
        task_id="ports_silver_to_gold",
        ssh_conn_id="ssh_worker4",
        command="""
            nohup /opt/spark/bin/spark-submit \
                --master yarn \
                --deploy-mode client \
                --name ports_silver_to_gold \
                --conf spark.sql.sources.partitionOverwriteMode=dynamic \
                --conf spark.driver.memory=512m \
                --conf spark.executor.memory=512m \
                --conf spark.executor.cores=1 \
                --num-executors 2 \
                /home/user/scripts/ports_gold_ingest.py {{ data_interval_start.strftime('%Y') }} {{ data_interval_start.strftime('%m') }} \
                > /home/user/scripts/gold_ingest.log 2>&1
            echo "Exit code: $?"
        """,
        cmd_timeout=7200,
    )

    wait_for_silver >> gold_ingest
