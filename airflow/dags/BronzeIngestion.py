import csv
import io
import hashlib
import json
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.sftp.hooks.sftp import SFTPHook
from airflow.providers.sftp.sensors.sftp import SFTPSensor
import requests

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
SFTP_CONN_ID = "sftp_ports_file"
SFTP_INBOUND_DIR = "/data/ports"
SFTP_ARCHIVE_DIR = "/data/PortsDataArchive"

WEBHDFS_BASE_URL = "http://master2:9870/webhdfs/v1"
HDFS_USER = "user"

default_args = {
    "owner": "maritime_data_eng",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

# -----------------------------------------------------------------------------
# Callables (defined outside DAG block)
# -----------------------------------------------------------------------------
def transfer_to_bronze(file_name, hdfs_dir, **context):
    sftp_hook = SFTPHook(ssh_conn_id=SFTP_CONN_ID)
    sftp_client = sftp_hook.get_conn()

    remote_path = f"{SFTP_INBOUND_DIR}/{file_name}"
    hdfs_target_file = f"{hdfs_dir}/{file_name}"
    manifest_path = f"{hdfs_dir}/_ingest_manifest.json"
    success_marker_path = f"{hdfs_dir}/_SUCCESS"

    sha256 = hashlib.sha256()
    ingested_at = datetime.utcnow().isoformat()
    source_name = f"sftp://SFTP_Ports_file{remote_path}"

    logging.info(f"Reading {remote_path} from SFTP server...")
    with sftp_client.open(remote_path, "rb") as sftp_file:
        raw_content = sftp_file.read()
        if not raw_content:
            raise ValueError(f"File {file_name} is empty (0 bytes).")

    # Parse CSV and add columns
    decoded = raw_content.decode("utf-8")
    reader = csv.reader(io.StringIO(decoded))
    output = io.StringIO()
    writer = csv.writer(output)

    for i, row in enumerate(reader):
        if i == 0:
            writer.writerow(row + ["ingested_at", "source_name"])
        else:
            writer.writerow(row + [ingested_at, source_name])

    content = output.getvalue().encode("utf-8")
    sha256.update(content)
    file_size = len(content)

    logging.info(f"Uploading {file_size} bytes to Hadoop Bronze: {hdfs_target_file}...")

    # Step A: Request upload URL from NameNode
    nn_url = f"{WEBHDFS_BASE_URL}{hdfs_target_file}?op=CREATE&overwrite=true&user.name={HDFS_USER}"
    res = requests.put(nn_url, allow_redirects=False)
    if res.status_code != 307:
        raise RuntimeError(f"WebHDFS CREATE on NameNode failed: {res.status_code} - {res.text}")

    # Step B: Write to DataNode
    datanode_url = res.headers["Location"]
    res_dn = requests.put(datanode_url, data=content, headers={"Content-Type": "application/octet-stream"})
    if res_dn.status_code != 201:
        raise RuntimeError(f"DataNode write failed: {res_dn.status_code} - {res_dn.text}")

    # Step C: Write Ingestion Manifest
    manifest = {
        "dataset": "ports",
        "source_file": remote_path,
        "hdfs_bronze_file": hdfs_target_file,
        "file_size_bytes": file_size,
        "sha256_checksum": sha256.hexdigest(),
        "ingestion_timestamp_utc": ingested_at,
        "source_name": source_name,
        "dag_run_id": context["run_id"],
        "data_interval_start": str(context["data_interval_start"]),
    }
    manifest_bytes = json.dumps(manifest, indent=2).encode("utf-8")

    res_m = requests.put(
        f"{WEBHDFS_BASE_URL}{manifest_path}?op=CREATE&overwrite=true&user.name={HDFS_USER}",
        allow_redirects=False
    )
    if res_m.status_code == 307:
        requests.put(res_m.headers["Location"], data=manifest_bytes, headers={"Content-Type": "application/json"})

    # Step D: Write _SUCCESS marker
    res_s = requests.put(
        f"{WEBHDFS_BASE_URL}{success_marker_path}?op=CREATE&overwrite=true&user.name={HDFS_USER}",
        allow_redirects=False
    )
    if res_s.status_code == 307:
        requests.put(res_s.headers["Location"], data=b"", headers={"Content-Type": "application/octet-stream"})

    logging.info("Bronze layer upload complete with manifest and _SUCCESS markers.")


def archive_sftp_file(file_name, **context):
    sftp_hook = SFTPHook(ssh_conn_id=SFTP_CONN_ID)
    sftp_client = sftp_hook.get_conn()

    src = f"{SFTP_INBOUND_DIR}/{file_name}"
    dst = f"{SFTP_ARCHIVE_DIR}/{file_name}"

    try:
        sftp_client.mkdir(SFTP_ARCHIVE_DIR)
    except IOError:
        pass

    logging.info(f"Archiving SFTP file: {src} -> {dst}")
    sftp_client.rename(src, dst)


# -----------------------------------------------------------------------------
# DAG Definition
# -----------------------------------------------------------------------------
with DAG(
    dag_id="ports_monthly_bronze_ingest",
    default_args=default_args,
    description="Monthly ingest of ports_YYYY-MM-01.csv from SFTP to Hadoop Bronze layer",
    schedule="@monthly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["ports", "bronze", "hadoop", "sftp"],
) as dag:

    PORTS_FILE_NAME = "ports_{{ data_interval_start.strftime('%Y-%m-01') }}.csv"
    SFTP_FILE_PATH = f"{SFTP_INBOUND_DIR}/{PORTS_FILE_NAME}"

    HDFS_BRONZE_PARTITION = (
        "/lake/bronze/ports/year={{ data_interval_start.strftime('%Y') }}/"
        "month={{ data_interval_start.strftime('%m') }}"
    )

    wait_for_ports_csv = SFTPSensor(
        task_id="wait_for_ports_csv",
        sftp_conn_id=SFTP_CONN_ID,
        path=SFTP_FILE_PATH,
        mode="reschedule",
        poke_interval=60,
        timeout=60 * 60 * 24 * 3,
    )

    ingest_task = PythonOperator(
        task_id="stream_ports_to_bronze",
        python_callable=transfer_to_bronze,
        op_kwargs={
            "file_name": PORTS_FILE_NAME,
            "hdfs_dir": HDFS_BRONZE_PARTITION,
        },
    )

    archive_task = PythonOperator(
        task_id="archive_ports_on_sftp",
        python_callable=archive_sftp_file,
        op_kwargs={
            "file_name": PORTS_FILE_NAME,
        },
    )

    wait_for_ports_csv >> ingest_task >> archive_task
