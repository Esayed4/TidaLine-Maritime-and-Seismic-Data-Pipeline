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
    dag_id="ports_monthly_silver_ingest",
    default_args=default_args,
    description="Monthly transformation of ports data from bronze to silver layer",
    schedule="@monthly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["ports", "silver", "spark", "hive"],
) as dag:

    wait_for_bronze = ExternalTaskSensor(
        task_id="wait_for_bronze_ingest",
        external_dag_id="ports_monthly_bronze_ingest",
        external_task_id="archive_ports_on_sftp",
        mode="reschedule",
        poke_interval=60,
        timeout=60 * 60 * 24,
        allowed_states=["success"],
        execution_date_fn=lambda dt: dt.replace(day=1),
    )

    restore_hive_jars = SSHOperator(
        task_id="restore_hive_jars",
        ssh_conn_id="ssh_worker4",
        command="""
            hdfs dfs -test -e /user/spark/hive4-jars/hive-common-4.1.0.jar
            if [ $? -ne 0 ]; then
                echo "Restoring hive4 jars to HDFS..."
                hdfs dfs -mkdir -p /user/spark/hive4-jars
                find /opt/hive4-jars/ -name "*.jar" -exec hdfs dfs -put {} /user/spark/hive4-jars/ \\;
                echo "Done."
            else
                echo "Jars already on HDFS, skipping."
            fi
        """,
    )

    silver_ingest = SSHOperator(
        task_id="ports_bronze_to_silver",
        ssh_conn_id="ssh_worker4",
        command="""
            nohup /opt/spark/bin/spark-submit \
                --master yarn \
                --deploy-mode client \
                --name ports_bronze_to_silver \
                --conf spark.sql.sources.partitionOverwriteMode=dynamic \
                /home/user/scripts/ports_silver_ingest.py {{ data_interval_start.strftime('%Y') }} {{ data_interval_start.strftime('%m') }} \
                > /home/user/scripts/silver_ingest.log 2>&1
            echo "Exit code: $?"
        """,
        cmd_timeout=7200,
    )

    wait_for_bronze >> restore_hive_jars >> silver_ingest
