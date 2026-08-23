# TidaLine — Maritime & Seismic Data Pipeline

**📄 This repository includes additional documentation files alongside this README: [PORTS_PIPELINE_RUNBOOK.md](PORTS_PIPELINE_RUNBOOK.md) for full infrastructure setup and operations, and [DataModel.md](DataModel.md) for the complete schema and ERD. Read those alongside this file for the full picture.**

A batch + streaming data pipeline that ingests **World Port Index (WPI) ports data**, **seismic events**, and **vessel AIS data** through a Bronze → Silver → Gold lakehouse architecture, culminating in a Power BI dashboard that overlays port risk scores with real-time earthquake proximity.

---

## Architecture Overview

```
SFTP Server                  Kafka (CDC / Debezium)
     │                                │
     ▼                                ▼
Bronze Layer (HDFS)          ODS — Snowflake
     │                                │
     ▼                                ▼
Silver Layer (Hive ORC)      Silver Layer (Hive ORC)
     │                                │
     └──────────────┬─────────────────┘
                    ▼
             Gold Layer (Hive ORC)
                    │
                    ▼
              Power BI Dashboard
```

**Infrastructure clusters:**

| Cluster | Role |
|---|---|
| BDSS (Hadoop/Spark) | HDFS storage, YARN, Spark execution, Hive metastore |
| Airflow | DAG orchestration, Spark job submission via SSH |
| TidaLine | SFTP server, Kafka, Postgres, stream extractor |

---

## Repository Structure

```
tidaline/
├── airflow/
│   └── dags/
│       ├── BronzeIngestion.py          # Ports: SFTP → HDFS bronze
│       ├── ports_silver_dag.py         # Ports: bronze → silver Hive table
│       └── ports_gold_dag.py           # Ports: silver → gold dim_ports
│
├── Spark_jobs/
│   ├── ports_silver_ingest.py          # PySpark: ports bronze → silver
│   └── ports_gold_ingest.py            # PySpark: ports silver → gold
│
├── Vessels_Silver_layer/
│   ├── bronze_to_silver_vessels.py     # PySpark: vessels bronze → silver
│   └── silver_vessels.sql              # Hive DDL for silver.vessels
│
├── vessels_ingestion_layer/
│   ├── sftp_vessels_client.py          # Download vessel CSVs from SFTP
│   ├── hdfs_vessels_client.py          # Upload vessel CSVs to HDFS via WebHDFS
│   └── cleanAndArchive.py              # Archive processed SFTP files
│
├── vessels_archive/
│   └── vessels_archive.py              # Consolidate bronze vessel CSVs into archive
│
├── logger/
│   └── logger.py                       # Shared logging wrapper
│
├── utils/
│   ├── config.py                       # YAML config loader
│   └── env.yaml                        # SFTP, HDFS, storage config
│
├── vessel_pipeline_dag.py              # Airflow DAG: end-to-end vessel pipeline
├── ods_stream.py                       # PySpark: Kafka stream → Snowflake ODS
├── archive_ods.py                      # PySpark: Snowflake ODS → HDFS archive
│
├── PowerBi/
│   └── TidaLine.pbix                   # Power BI dashboard
│
├── data_model_exports/
│   ├── DataModel.md
│   ├── datamodel_ddl_mysql.sql
│   ├── datamodel_visualized_markdown.md
│   └── datamodel_visualized_mermaid.md
│
├── DataModel.md                        # Full data model documentation
├── PORTS_PIPELINE_RUNBOOK.md           # Ports pipeline ops runbook
├── Dockerfile                          # Airflow image with Spark + Hive jars
├── docker-compose.yml                  # Airflow cluster compose
└── docker-compose.spark.yml            # Spark cluster compose (reference)
```

---

## Data Sources

| Source | Format | Cadence | Ingestion method |
|---|---|---|---|
| World Port Index (WPI) | CSV via SFTP | Monthly | Airflow SFTPSensor → HDFS |
| Vessel AIS data | CSV via SFTP | Daily | Airflow PythonOperator |
| Seismic events | Kafka (Debezium CDC) | Streaming | PySpark Structured Streaming → Snowflake ODS |

---

## Data Layers

### Bronze
Raw data as-is from source, with two metadata columns added to every table:

- `data_source` — origin identifier
- `ingestion_timestamp` — time the record was loaded

Ports and vessel files are stored as partitioned CSV in HDFS (`/lake/bronze/ports/`, `/bronze/vessels/`). Seismic events land in Snowflake ODS via the Kafka stream.

### Silver
Cleaned, typed, normalized ORC tables in Hive.

| Table | Key transformations |
|---|---|
| `silver.ports` | Type enforcement, column drops, flag normalization (Y/N/U), deduplication |
| `silver.vessels` | Type casting, lat/lon direction parsing, column renames (`length(m)` → `length_m`), full-replace upsert by vessel name |
| `silver.seismic_events` | Column renames, MERGE logic (same-day updates overwrite; cross-day updates insert as new record) |

### Gold
Analytics-ready Hive ORC tables used by Power BI.

| Table | Description |
|---|---|
| `gold.dim_ports` | Flag columns cast to 0/1, `has_repairs` derived column, `communications_index` and `supplies_index` with category labels |
| `gold.dim_seismic_events` | Date key and time key foreign keys added |
| `gold.dim_vessels` | Column renames, ingestion date columns |
| `gold.dim_date` | Standard date dimension |
| `gold.dim_time` | Standard time dimension |

### Semantic Layer (Power BI)
Built in Power BI using DAX measures, Power Query (M), and parameters.

Key computed artifacts:

- **`fact_ports_events`** — cross-join of ports and earthquakes with Haversine distance (filtered to ≤ 300 km by a user-controlled parameter)
- **`risk_score`** — per-port earthquake risk: `SUM( 10^magnitude / (distance² × √depth) )`
- **`risk_category`** — dynamic NTILE(3) categorization: Low / Medium / High
- **`Map_Points`** — UNION of ports and earthquakes for a single map layer, with tooltip labels
- **`Show On Map`** — filters earthquake points by a "Days Ago" date parameter while always showing ports

---

## Pipelines

### Ports Pipeline (monthly batch)

Orchestrated by three chained Airflow DAGs:

```
ports_monthly_bronze_ingest
        │  (ExternalTaskSensor)
        ▼
ports_monthly_silver_ingest
        │  (ExternalTaskSensor)
        ▼
ports_monthly_gold_ingest
```

1. **Bronze DAG** — SFTPSensor polls for `ports_YYYY-MM-01.csv`, copies it to `hdfs://bdss/lake/bronze/ports/year=YYYY/month=MM/`, archives the source file.
2. **Silver DAG** — SSHOperator runs `ports_silver_ingest.py` on `worker4` via `spark-submit`. Restores Hive 4.1.0 jars to HDFS if missing.
3. **Gold DAG** — SSHOperator runs `ports_gold_ingest.py` on `worker4`.

### Vessel Pipeline (daily batch)

Single Airflow DAG (`vessel_pipeline_end_to_end`) with five sequential tasks:

```
download_vessel_files
        │
upload_vessels_to_hdfs
        │
cleanup_and_archive_vessel_files
        │
copy_vessels_job_to_worker4
        │
run_vessels_silver_job
```

1. Downloads daily `vessels_YYYY-MM-DD.csv` files from SFTP into a local temp directory, adding ingestion metadata via pandas.
2. Uploads them to HDFS at `/bronze/vessels/YYYY/MM/DD/` using WebHDFS.
3. Deletes local temp files and archives the SFTP source files.
4. Copies `bronze_to_silver_vessels.py` to `worker4`.
5. Submits the PySpark job over SSH to write into `silver.vessels`.

### Seismic Events Pipeline (streaming)

- `ods_stream.py` — PySpark Structured Streaming reads Debezium CDC events from Kafka topic `cdc.public.earthquakes`, applies a MERGE into `ODS_EARTHQUAKES` in Snowflake.
- `archive_ods.py` — Batch job that exports the Snowflake ODS table to HDFS as a CSV archive.

---

## Setup & Operations

For full infrastructure setup, network configuration, SSH key management, Airflow connections, and troubleshooting, refer to the **[Ports Pipeline Runbook](PORTS_PIPELINE_RUNBOOK.md)**.

Quick-start summary:

```bash
# 1. Start all three clusters
docker compose -f docker-compose.yml up -d          # Airflow
cd bdss-cluster && docker compose up -d             # BDSS Hadoop/Spark
cd tidaline && docker compose up -d                 # SFTP + Kafka

# 2. Connect networks
docker network connect maritime-net worker4
docker network connect maritime-net airflow_proj-sleek-airflow-1
docker network connect tidaline-case-study-network airflow_proj-sleek-airflow-1

# 3. Deploy Spark scripts to worker4
docker cp Spark_jobs/ports_silver_ingest.py worker4:/home/user/scripts/
docker cp Spark_jobs/ports_gold_ingest.py worker4:/home/user/scripts/

# 4. Enable DAGs in Airflow UI → http://localhost:8080
```

---

## Configuration

All SFTP, HDFS, and storage paths are centralized in `utils/env.yaml`:

```yaml
sftp:
  host: "sftp"
  port: 22
  username: "batch"
  password: "batchpass"

storage:
  temp_vessel_path: "/opt/airflow/dags/temp/vessel"

hdfs:
  bronze_vessels_base_path: /bronze/vessels
```

---

## Data Model

The full schema with ERD links is documented in [DataModel.md](DataModel.md).

Interactive diagram: [DrawDB (live)](https://www.drawdb.app/editor/diagrams/8971b1f7-84a3-4414-a42d-c60277a4f332)

---

## Power BI Dashboard

The dashboard (`PowerBi/TidaLine.pbix`) contains:

- **World map** — ports and seismic events plotted together, filterable by date and proximity radius
- **Port risk panel** — risk score and category per port based on nearby earthquake history
- **Seismic summary** — total events, average magnitude, max magnitude, strongest region for the selected day
- **Port infrastructure view** — communications index, supplies index, and harbor metadata per port

---

## Tech Stack

| Layer | Technology |
|---|---|
| Distributed storage | Apache Hadoop HDFS 3.x (HA) |
| Batch processing | Apache Spark 4.1.1 / PySpark |
| Table catalog | Apache Hive 4.1.0 |
| Orchestration | Apache Airflow 3.x |
| Streaming ingest | Apache Kafka + Debezium CDC |
| ODS / streaming sink | Snowflake |
| Containerization | Docker / Docker Compose |
| BI & semantic layer | Microsoft Power BI (DAX, Power Query M) |
| Scripting | Python 3.12 |
