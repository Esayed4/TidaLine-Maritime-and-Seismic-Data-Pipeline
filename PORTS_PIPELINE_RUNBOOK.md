# Ports Batch Pipeline - Runbook

## 1. Overview

This runbook documents the setup and operation of the Ports Batch Pipeline — a monthly batch ingestion pipeline that processes World Port Index (WPI) data from an SFTP server through a Bronze → Silver → Gold lakehouse architecture.

The pipeline uses:
- **Apache Hadoop HDFS** for distributed storage
- **Apache Spark** for distributed data processing
- **Apache Hive** for the managed table catalog
- **Apache Airflow** for orchestration

Data flows through three layers:
- **Bronze** — raw CSV ingested from SFTP with metadata columns added
- **Silver** — cleaned, typed, normalized ORC table in Hive
- **Gold** — analytics-ready dimensional table (`dim_ports`) with derived metrics

---

## 2. Prerequisites

This pipeline runs across three pre-existing containerized environments from ITI courses and the Tidaline project:

- **BDSS Hadoop/Spark Cluster** — from the ITI Big Data & Spark course. Provides HDFS, YARN, and Spark workers.
- **Airflow Cluster** — from the ITI Airflow course. The Dockerfile was modified to include Apache Spark client and Hive 4.1.0 jars. See section 6 for details.
- **Tidaline Cluster** — project-specific cluster containing the SFTP server, Kafka, Postgres, and stream extractor containers.

Before running the pipeline, ensure all three clusters are up and running:

```bash
# Verify BDSS cluster
docker ps --filter "name=master"
docker ps --filter "name=worker"
docker ps --filter "name=journalnode"

# Verify Airflow
docker ps --filter "name=airflow"

# Verify Tidaline
docker ps --filter "name=sftp"
```

---

## 3. Network Setup

The pipeline requires three Docker networks to be connected properly so all containers can communicate:

- **`bdss-cluster_bd_ss_nw`** — internal network of the BDSS Hadoop/Spark cluster
- **`maritime-net`** — shared network between Airflow and `worker4`
- **`tidaline-case-study-network`** — network of the Tidaline cluster (SFTP, Kafka, Postgres)

### 3.1 Create maritime-net (if it doesn't exist)

```bash
docker network create maritime-net
```

### 3.2 Connect containers to networks

After every Docker Desktop restart or container recreation, run the following to ensure all containers are connected to the correct networks:

```bash
# Connect worker4 to maritime-net
docker network connect maritime-net worker4

# Connect Airflow to maritime-net
docker network connect maritime-net airflow_proj-sleek-airflow-1

# Connect Airflow to tidaline network (for SFTP access)
docker network connect tidaline-case-study-network airflow_proj-sleek-airflow-1
```

### 3.3 Verify connections

```bash
# Verify worker4 networks
docker inspect worker4 --format "{{json .NetworkSettings.Networks}}"

# Verify Airflow networks
docker inspect airflow_proj-sleek-airflow-1 --format "{{json .NetworkSettings.Networks}}"
```

Expected networks for `worker4`:
- `bdss-cluster_bd_ss_nw`
- `maritime-net`

Expected networks for Airflow:
- `airflow_proj_default`
- `bdss-cluster_bd_ss_nw`
- `maritime-net`
- `tidaline-case-study-network`

> **Note:** The `docker-compose.yml` for the Airflow cluster has been updated to auto-connect to these networks on startup. However, `worker4` must be manually reconnected to `maritime-net` after each restart.

---

## 4. BDSS Hadoop/Spark Cluster Setup

The BDSS cluster provides HDFS storage, YARN resource management, and Spark execution. It consists of:

- 2 NameNodes (`master1`, `master2`) in HA mode
- 3 JournalNodes (`journalnode1`, `journalnode2`, `journalnode3`)
- 3 Spark/Hadoop DataNodes (`worker1`, `worker2`, `worker3`)
- 1 Jupyter/Spark node (`worker4`) — used for script development and job submission
- 1 Hive metastore (`hive`) backed by Postgres (`metastore-db`)

### 4.1 Start the cluster

```bash
cd /path/to/bdss-cluster
docker compose up -d
```

### 4.2 Verify cluster health

```bash
# Check all containers are healthy
docker ps --filter "name=master"
docker ps --filter "name=journalnode"
docker ps --filter "name=worker"
docker ps --filter "name=hive"

# Check HDFS status
docker exec worker4 bash -c "hdfs dfsadmin -report"

# Check YARN status
docker exec worker4 bash -c "yarn rmadmin -getServiceState rm1"
docker exec worker4 bash -c "yarn rmadmin -getServiceState rm2"
```

### 4.3 Create required HDFS directories

```bash
docker exec worker4 bash -c "hdfs dfs -mkdir -p /lake/bronze/ports"
docker exec worker4 bash -c "hdfs dfs -mkdir -p /user/hive/warehouse"
docker exec worker4 bash -c "hdfs dfs -mkdir -p /user/hive/external"
docker exec worker4 bash -c "hdfs dfs -mkdir -p /user/spark/hive4-jars"
```

### 4.4 Troubleshooting

**NameNode not starting:**
The most common cause is JournalNodes being down. Ensure all three are running:

```bash
docker ps --filter "name=journalnode"
docker restart journalnode1 journalnode2 journalnode3
docker restart master1 master2
```

**YARN ResourceManager connection refused:**
```bash
docker exec worker4 bash -c "yarn rmadmin -getServiceState rm1"
```

If both RMs are down, restart the masters:
```bash
docker restart master1 master2
```

### 4.5 Hive 4.1.0 Jars

The BDSS workers ship with Hive 2.3.10 jars which are incompatible with the Hive 4.1.0 metastore. The correct jars must be copied to **all worker nodes** and uploaded to HDFS.

> **Important:** This step must be repeated if worker containers are recreated (not just restarted). The jars are lost on container recreation.

**Get jars from the hive container (first time only):**

```powershell
# Copy from hive container to local machine
docker cp hive:/opt/hive/lib C:\Users\<your-user>\hive4-jars
```

**Copy jars from your local machine to all workers:**

```powershell
docker cp C:\Users\<your-user>\hive4-jars worker1:/opt/hive4-jars
docker cp C:\Users\<your-user>\hive4-jars worker2:/opt/hive4-jars
docker cp C:\Users\<your-user>\hive4-jars worker3:/opt/hive4-jars
docker cp C:\Users\<your-user>\hive4-jars worker4:/opt/hive4-jars
```

**Upload jars to HDFS (run on worker4):**

```bash
hdfs dfs -mkdir -p /user/spark/hive4-jars
find /opt/hive4-jars/ -name "*.jar" -exec hdfs dfs -put {} /user/spark/hive4-jars/ \;
```

> **Note:** The silver DAG includes a `restore_hive_jars` task that automatically checks and restores the jars to HDFS if they are missing. However, the jars must exist on the worker nodes locally for this task to work.

---

## 5. SFTP Setup

The SFTP server is part of the Tidaline cluster and serves as the source for the monthly ports CSV files.

### 5.1 SFTP Container Details

- **Container name:** `sftp`
- **Image:** `atmoz/sftp:debian`
- **Host:** `sftp` (resolvable within `tidaline-case-study-network`)
- **Port:** `22`
- **Credentials:** `batch` / `batchpass`
- **Inbound directory:** `/data/ports/`
- **Archive directory:** `/data/PortsDataArchive/`

### 5.2 Expected file format

The source file follows this naming convention:

###### ports_YYYY-MM-01.csv

For example: `ports_2026-08-01.csv`

The file must be present in `/data/ports/` before the bronze DAG is triggered. The sensor will poll for it every 60 seconds for up to 3 days.

### 5.3 Verify SFTP connectivity

From inside the Airflow container:

```bash
docker exec -it airflow_proj-sleek-airflow-1 bash
sftp -P 22 batch@sftp
# password: batchpass
```

### 5.4 Manually place a file on SFTP

If testing, connect to the SFTP server directly and place the file:

```bash
# Connect to SFTP container
docker exec -it sftp bash

# Verify file is in place
ls /data/ports/
```

### 5.5 Archive directory

After successful bronze ingestion, the DAG moves the file to the archive directory:


###### /data/PortsDataArchive/ports_YYYY-MM-01.csv


If rerunning the pipeline for the same month, restore the file:

```bash
docker exec sftp bash -c "mv /data/PortsDataArchive/ports_2026-08-01.csv /data/ports/ports_2026-08-01.csv"
```

---

## 6. Airflow Setup

The Airflow cluster is based on the ITI Airflow course environment. The `Dockerfile` and `docker-compose.yml` were modified to support the ports batch pipeline.

### 6.1 Dockerfile Changes

The original Dockerfile was modified to:
- Install Java 17 (required for Spark)
- Install Apache Spark 4.1.1 client
- Copy Hive 4.1.0 jars into the image
- Install additional Python providers

```dockerfile
FROM apache/airflow:latest
USER root

RUN apt-get update && \
    apt-get -y install git curl wget openjdk-17-jdk && \
    apt-get clean

# Install Spark 4.1.1
RUN wget -q https://archive.apache.org/dist/spark/spark-4.1.1/spark-4.1.1-bin-hadoop3.tgz && \
    tar -xzf spark-4.1.1-bin-hadoop3.tgz -C /opt/ && \
    mv /opt/spark-4.1.1-bin-hadoop3 /opt/spark && \
    rm spark-4.1.1-bin-hadoop3.tgz

ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Copy Hive 4.1.0 jars
COPY hive4-jars/ /opt/hive4-jars/

USER airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt \
    apache-airflow-providers-postgres \
    psycopg2-binary \
    apache-airflow-providers-apache-spark
```

> **Note:** The `hive4-jars/` directory must be present in the same directory as the Dockerfile before building the image. See section 4.5 for how to obtain the jars.

**Build the image:**

```powershell
cd C:\Users\<your-user>\Downloads\airflow\airflow_proj
docker build --no-cache -t airflowdm:latest .
```

### 6.2 docker-compose.yml Changes

The `docker-compose.yml` was modified to:
- Auto-connect Airflow to all required networks on startup
- Mount the SSH keys directory as a volume for persistence

```yaml
sleek-airflow:
  build: .
  image: airflowdm:latest
  volumes:
    - ./airflow/dags:/opt/airflow/dags
    - ./airflow/logs:/opt/airflow/logs
    - ./airflow/plugins:/opt/airflow/plugins
    - ./ssh_keys:/home/airflow/.ssh
  networks:
    - default
    - maritime-net
    - bdss-cluster_bd_ss_nw
    - tidaline-case-study-network

networks:
  default:
    name: airflow_proj_default
  maritime-net:
    external: true
  bdss-cluster_bd_ss_nw:
    external: true
  tidaline-case-study-network:
    external: true
```

### 6.3 Start Airflow

```powershell
cd C:\Users\<your-user>\Downloads\airflow\airflow_proj
docker compose up -d
```

### 6.4 Get Airflow UI password

```bash
docker exec airflow_proj-sleek-airflow-1 bash -c "cat /opt/airflow/simple_auth_manager_passwords.json.generated"
```

Access the UI at `http://localhost:8080`.

> **Note:** The Airflow password is regenerated every time the container is recreated. Always check the file above after a fresh start.

---

## 7. SSH Key Setup

Airflow uses SSH key-based authentication to connect to `worker4` for running `spark-submit` commands. The keys are stored in `./ssh_keys/` and mounted into the Airflow container via the docker-compose volume.

### 7.1 Generate SSH keys (first time only)

Run inside the Airflow container:

```bash
docker exec -it airflow_proj-sleek-airflow-1 bash
mkdir -p /home/airflow/.ssh
ssh-keygen -t ed25519 -f /home/airflow/.ssh/id_ed25519 -N ''
cat /home/airflow/.ssh/id_ed25519.pub
```

Copy the public key output.

### 7.2 Add public key to worker4

```bash
docker exec -u root worker4 bash -c "echo 'PASTE_PUBLIC_KEY_HERE' >> /home/user/.ssh/authorized_keys"
```

### 7.3 Enable public key authentication on worker4

```bash
docker exec -u root worker4 bash -c "sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config"
docker exec -u root worker4 bash -c "sed -i 's/#AuthorizedKeysFile/AuthorizedKeysFile/' /etc/ssh/sshd_config"
docker exec -u root worker4 bash -c "service ssh restart"
```

### 7.4 Copy keys to ssh_keys directory for persistence

```powershell
docker cp airflow_proj-sleek-airflow-1:/home/airflow/.ssh/id_ed25519 C:\Users\<your-user>\Downloads\airflow\airflow_proj\ssh_keys\id_ed25519
docker cp airflow_proj-sleek-airflow-1:/home/airflow/.ssh/id_ed25519.pub C:\Users\<your-user>\Downloads\airflow\airflow_proj\ssh_keys\id_ed25519.pub
```

### 7.5 Test SSH connection

```bash
docker exec airflow_proj-sleek-airflow-1 bash -c "ssh -i /home/airflow/.ssh/id_ed25519 -o StrictHostKeyChecking=no user@172.25.0.3 'echo connected'"
```

Expected output: `connected`

> **Note:** The IP address of `worker4` on `maritime-net` may change after container recreation. Always verify the current IP before updating the Airflow SSH connection:
> ```powershell
> docker inspect worker4 --format "{{json .NetworkSettings.Networks}}"
> ```

---

## 8. Airflow Connections

Three connections are required for the pipeline. Since Airflow 3.x has known issues with connection visibility in the UI, all connections should be created via the CLI.

> **Important:** If the Airflow container is recreated (not just restarted), the Fernet key changes and existing encrypted connections become invalid. In this case, delete all connections from the database and recreate them:
>
> ```powershell
> docker exec airflow_proj-postgres-1 psql -U airflow -d airflow -c "DELETE FROM connection;"
> ```

### 8.1 Create connections via CLI

Enter the Airflow container:

```bash
docker exec -it airflow_proj-sleek-airflow-1 bash
```

Then run:

```bash
# SSH connection to worker4
airflow connections add ssh_worker4 \
    --conn-type ssh \
    --conn-host 172.25.0.3 \
    --conn-login user \
    --conn-port 22 \
    --conn-extra '{"private_key_file": "/home/airflow/.ssh/id_ed25519"}'

# SFTP connection to the ports source server
airflow connections add sftp_ports_file \
    --conn-type sftp \
    --conn-host sftp \
    --conn-login batch \
    --conn-password batchpass \
    --conn-port 22

# Spark connection
airflow connections add spark_worker4 \
    --conn-type spark \
    --conn-host yarn \
    --conn-port 8088
```

### 8.2 Verify connections

```bash
airflow connections get ssh_worker4
airflow connections get sftp_ports_file
airflow connections get spark_worker4
```

### 8.3 Update SSH connection IP

If `worker4`'s IP changes after a restart, get the new IP:

```powershell
docker inspect worker4 --format "{{json .NetworkSettings.Networks}}"
```

Then delete and recreate the SSH connection with the new IP:

```bash
airflow connections delete ssh_worker4
airflow connections add ssh_worker4 \
    --conn-type ssh \
    --conn-host <new-ip> \
    --conn-login user \
    --conn-port 22 \
    --conn-extra '{"private_key_file": "/home/airflow/.ssh/id_ed25519"}'
```

---

## 9. Scripts Deployment

Two PySpark scripts handle the silver and gold transformations. They must be present on `worker4` before the DAGs are triggered.

### 9.1 Create scripts directory on worker4

```bash
docker exec worker4 bash -c "mkdir -p /home/user/scripts"
```

### 9.2 Copy scripts to worker4

```powershell
docker cp ports_silver_ingest.py worker4:/home/user/scripts/ports_silver_ingest.py
docker cp ports_gold_ingest.py worker4:/home/user/scripts/ports_gold_ingest.py
```

### 9.3 Verify scripts are in place

```bash
docker exec worker4 bash -c "ls /home/user/scripts/"
```

Expected output:

###### ports_gold_ingest.py
###### ports_silver_ingest.py



### 9.4 Script details

**`ports_silver_ingest.py`**
- Reads from `hdfs://bdss/lake/bronze/ports/year=<year>/month=<month>/`
- Drops unused columns
- Enforces data types
- Normalizes flag columns (Y/N/U → Y/N/U single char)
- Drops full duplicates
- Adds `ingested_to_silver_at` timestamp
- Writes to `silver.ports` Hive managed ORC table

**`ports_gold_ingest.py`**
- Reads from `silver.ports`
- Renames columns to snake_case
- Drops entrance restriction columns
- Transforms flag columns (Y → 1, N/U/null → 0)
- Derives `has_repairs` column
- Computes `communications_index` and `supplies_index` with categories
- Adds `ingested_to_gold_at` timestamp and `ingestion_date`
- Writes to `gold.dim_ports` Hive managed ORC table

### 9.5 Script arguments

Both scripts accept `year` and `month` as command line arguments:

```bash
/opt/spark/bin/spark-submit ports_silver_ingest.py 2026 08
/opt/spark/bin/spark-submit ports_gold_ingest.py 2026 08
```

These are passed automatically by Airflow at runtime via the SSHOperator command.

> **Note:** Scripts must be re-copied to `worker4` if the container is recreated, as the `/home/user/scripts/` directory is not persisted via a volume.

---

## 10. DAG Deployment

Three DAGs orchestrate the pipeline. They are stored in the Airflow DAGs folder which is mounted as a volume and persists across container restarts.

### 10.1 DAG files

| DAG file | DAG ID | Description |
|----------|--------|-------------|
| `BronzeIngestion.py` | `ports_monthly_bronze_ingest` | Ingests raw CSV from SFTP to HDFS bronze layer |
| `ports_silver_dag.py` | `ports_monthly_silver_ingest` | Transforms bronze to silver Hive table |
| `ports_gold_dag.py` | `ports_monthly_gold_ingest` | Transforms silver to gold Hive dimension table |

### 10.2 DAGs folder location

###### C:\Users<your-user>\Downloads\airflow\airflow_proj\airflow\dags\


All three DAG files must be placed in this directory. They are automatically picked up by Airflow.

### 10.3 DAG pipeline chain

ports_monthly_bronze_ingest
↓ (ExternalTaskSensor)
ports_monthly_silver_ingest
↓ (ExternalTaskSensor)
ports_monthly_gold_ingest



Each DAG waits for the previous one to complete successfully before running.

### 10.4 DAG schedule

All three DAGs run on a `@monthly` schedule. The bronze DAG triggers on the 1st of each month after the source file arrives on the SFTP server.

### 10.5 Enable DAGs

After deployment, enable all three DAGs in the Airflow UI by clicking the toggle next to each DAG name.

### 10.6 Verify DAGs are loaded

```bash
docker exec airflow_proj-sleek-airflow-1 bash -c "airflow dags list | grep ports"
```

Expected output:

ports_monthly_bronze_ingest
ports_monthly_silver_ingest
ports_monthly_gold_ingest



---

## 11. Running the Pipeline

### 11.1 Pre-flight checklist

Before triggering the pipeline, verify the following:

- [ ] All BDSS cluster containers are healthy
- [ ] All journalnodes are running (`journalnode1`, `journalnode2`, `journalnode3`)
- [ ] HDFS is accessible (`hdfs dfs -ls /`)
- [ ] YARN ResourceManager is active (`yarn rmadmin -getServiceState rm1`)
- [ ] Hive jars are on all workers (`ls /opt/hive4-jars/` on each worker)
- [ ] Hive jars are on HDFS (`hdfs dfs -ls /user/spark/hive4-jars/`)
- [ ] Scripts are on `worker4` (`ls /home/user/scripts/`)
- [ ] All Airflow connections are configured (`airflow connections list`)
- [ ] `worker4` is connected to `maritime-net`
- [ ] Airflow is connected to `maritime-net` and `tidaline-case-study-network`
- [ ] Source file is present on SFTP (`/data/ports/ports_YYYY-MM-01.csv`)
- [ ] All three DAGs are enabled in the Airflow UI

### 11.2 Trigger the pipeline

The pipeline can be triggered automatically on schedule or manually from the Airflow UI.

**Manual trigger (recommended for testing):**

Trigger the DAGs in order:

1. Trigger `ports_monthly_bronze_ingest`
2. Wait for it to complete successfully
3. Trigger `ports_monthly_silver_ingest`
4. Wait for it to complete successfully
5. Trigger `ports_monthly_gold_ingest`

> **Note:** In production, only the bronze DAG needs to be triggered. The silver and gold DAGs will fire automatically via the `ExternalTaskSensor` once the previous DAG succeeds.

### 11.3 Monitor the pipeline

- **Airflow UI:** `http://localhost:8080`
- **YARN UI:** `http://localhost:18088`
- **Spark UI:** `http://localhost:4040` (only available during job execution)

### 11.4 Verify data at each layer

**Bronze:**
```bash
docker exec worker4 bash -c "hdfs dfs -ls /lake/bronze/ports/year=2026/month=08/"
docker exec worker4 bash -c "hdfs dfs -cat /lake/bronze/ports/year=2026/month=08/ports_2026-08-01.csv | head -2"
```

**Silver:**
```python
spark.sql("SELECT COUNT(*) FROM silver.ports WHERE year='2026' AND month='08'").show()
```

**Gold:**
```python
spark.sql("SELECT COUNT(*) FROM gold.dim_ports WHERE year='2026' AND month='08'").show()
```

### 11.5 Check Spark job logs

Silver job log:
```bash
docker exec worker4 bash -c "cat /home/user/scripts/silver_ingest.log"
```

Gold job log:
```bash
docker exec worker4 bash -c "cat /home/user/scripts/gold_ingest.log"
```

### 11.6 Re-running the pipeline

To rerun the pipeline for the same month:

1. Restore the source file on SFTP:
```bash
docker exec sftp bash -c "mv /data/PortsDataArchive/ports_2026-08-01.csv /data/ports/ports_2026-08-01.csv"
```

2. Clear the bronze HDFS partition:
```bash
docker exec worker4 bash -c "hdfs dfs -rm -r /lake/bronze/ports/year=2026/month=08/"
```

3. Trigger the pipeline again from the Airflow UI.

> **Note:** The silver and gold tables use dynamic partition overwrite — rerunning will safely replace only the affected partition without touching other months' data.

---

## 12. Troubleshooting

### 12.1 JournalNodes down — NameNode won't start

**Symptom:** NameNode fails to start with `java.net.UnknownHostException: journalnode1:8485`

**Fix:**
```bash
docker ps --filter "name=journalnode"
docker restart journalnode1 journalnode2 journalnode3
docker restart master1 master2
```

---

### 12.2 HDFS port 8020 connection refused

**Symptom:** `java.net.ConnectException: Call From worker4 to master1:8020 failed`

**Fix:**
```bash
# Check namenode process is running
docker exec master1 bash -c "ps aux | grep java | grep namenode"

# Start namenode manually if not running
docker exec master1 bash -c "hdfs --daemon start namenode"
docker exec master2 bash -c "hdfs --daemon start namenode"
```

---

### 12.3 YARN ResourceManager connection refused

**Symptom:** Spark job fails with `Call From worker4 to master1:8032 failed`

**Fix:**
```bash
docker exec worker4 bash -c "yarn rmadmin -getServiceState rm1"
docker restart master1 master2
```

---

### 12.4 Hive jars not found

**Symptom:** `PATH_NOT_FOUND: Path does not exist: hdfs://bdss/user/spark/hive4-jars/*`

**Fix:**
```bash
# Verify jars exist on worker4
docker exec worker4 bash -c "ls /opt/hive4-jars/ | grep hive-common"

# Re-upload to HDFS
docker exec worker4 bash -c "find /opt/hive4-jars/ -name '*.jar' -exec hdfs dfs -put {} /user/spark/hive4-jars/ \;"
```

> **Note:** If jars don't exist on `worker4` either, re-copy from local machine. See section 4.5.

---

### 12.5 SSH connection refused or timed out

**Symptom:** `SSH operator error: exit status 127` or `Connection timed out`

**Fix:**
```bash
# Check worker4 is on maritime-net
docker inspect worker4 --format "{{json .NetworkSettings.Networks}}"

# Reconnect if missing
docker network connect maritime-net worker4

# Get current IP of worker4
docker inspect worker4 --format "{{json .NetworkSettings.Networks}}"

# Update Airflow SSH connection if IP changed
airflow connections delete ssh_worker4
airflow connections add ssh_worker4 \
    --conn-type ssh \
    --conn-host <new-ip> \
    --conn-login user \
    --conn-port 22 \
    --conn-extra '{"private_key_file": "/home/airflow/.ssh/id_ed25519"}'
```

---

### 12.6 Airflow connections invalid after container recreation

**Symptom:** `InvalidToken` error or connections not found

**Cause:** Airflow generates a new Fernet key on every container recreation, invalidating previously encrypted connections.

**Fix:**
```powershell
# Delete all old connections
docker exec airflow_proj-postgres-1 psql -U airflow -d airflow -c "DELETE FROM connection;"
```

Then recreate all connections. See section 8.1.

---

### 12.7 SFTP authentication failed

**Symptom:** `Authentication failed` on bronze DAG sensor

**Fix:**
```bash
# Verify SFTP container is running
docker ps --filter "name=sftp"

# Verify Airflow is on tidaline network
docker inspect airflow_proj-sleek-airflow-1 --format "{{json .NetworkSettings.Networks}}"

# Reconnect if missing
docker network connect tidaline-case-study-network airflow_proj-sleek-airflow-1
```

---

### 12.8 Spark job killed (exit code 137)

**Symptom:** `Killed` in spark-submit log, exit code 137

**Cause:** Out of memory — Spark driver or executor exceeded available memory.

**Fix:** Add memory constraints to the spark-submit command:
```bash
--conf spark.driver.memory=512m \
--conf spark.executor.memory=512m \
--conf spark.executor.cores=1 \
--num-executors 2
```

---

### 12.9 Gold table location conflict

**Symptom:** `LOCATION_ALREADY_EXISTS` error when creating `gold.dim_ports`

**Fix:**
```bash
# Delete stale HDFS path
docker exec worker4 bash -c "hdfs dfs -rm -r /user/hive/external/gold.db/"
docker exec worker4 bash -c "hdfs dfs -rm -r /user/hive/warehouse/gold.db/"
```

Then drop the table from metastore via Spark:
```python
spark.sql("DROP TABLE IF EXISTS gold.dim_ports")
spark.sql("DROP DATABASE IF EXISTS gold")
```

---

### 12.10 Scripts not found on worker4

**Symptom:** `python3: can't open file '/home/user/scripts/ports_silver_ingest.py'`

**Cause:** Scripts are lost when the `worker4` container is recreated.

**Fix:**
```powershell
docker exec worker4 bash -c "mkdir -p /home/user/scripts"
docker cp ports_silver_ingest.py worker4:/home/user/scripts/ports_silver_ingest.py
docker cp ports_gold_ingest.py worker4:/home/user/scripts/ports_gold_ingest.py
```
