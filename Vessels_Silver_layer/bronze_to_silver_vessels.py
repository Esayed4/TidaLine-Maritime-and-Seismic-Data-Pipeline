# hi from airflow
import sys
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# ============================================================
# 1. Parse Command Line Arguments
# ============================================================

# Default parameters
DEFAULT_START_DATE = "2026/08/01"
DEFAULT_END_DATE = "2026/08/30"

# Read arguments if provided (Usage: spark-submit script.py <start_date> <end_date>)
if len(sys.argv) >= 3:
    START_DATE = sys.argv[1]
    END_DATE = sys.argv[2]
else:
    print(f"No date arguments provided. Using default dates: {DEFAULT_START_DATE} to {DEFAULT_END_DATE}")
    START_DATE = DEFAULT_START_DATE
    END_DATE = DEFAULT_END_DATE

BASE_DIR = "/bronze/vessels"


# ============================================================
# 2. Spark Session Initialization
# ============================================================

spark = (
    SparkSession.builder.appName("SilverSeismicInsert")
    .master("local[1]")
    .enableHiveSupport()
    .config("hive.metastore.uris", "thrift://hive:9083")
    .config("spark.hadoop.hive.exec.dynamic.partition", "true")
    .config("spark.hadoop.hive.exec.dynamic.partition.mode", "nonstrict")
    .getOrCreate()
)

spark.conf.set("spark.sql.sources.partitionOverwriteMode", "static")

# Fetch initial Hive table for comparison/upsert
hive_df = spark.table("silver.vessels")
print(f"Existing count in Hive table: {hive_df.count()}")


# ============================================================
# 3. Helper Functions for HDFS Reading
# ============================================================

def generate_paths(base_dir, start_date, end_date):
    """Generate HDFS directory paths for every date between start_date and end_date."""
    start = datetime.strptime(start_date, "%Y/%m/%d").date()
    end = datetime.strptime(end_date, "%Y/%m/%d").date()

    if start > end:
        raise ValueError("start_date cannot be greater than end_date")

    paths = []
    current = start

    while current <= end:
        path = f"{base_dir}/{current.year}/{current.month:02d}/{current.day:02d}"
        paths.append(path)
        current += timedelta(days=1)

    return paths


def combine_csv_files(spark, base_dir, start_date, end_date):
    """Find existing HDFS directories in the date range, gather CSV files,
    read them, and force coalescing to 1 partition.
    """
    paths = generate_paths(base_dir, start_date, end_date)

    print("=" * 70)
    print("SPARK CSV READER")
    print("=" * 70)
    print(f"Base directory : {base_dir}")
    print(f"Start date     : {start_date}")
    print(f"End date       : {end_date}")

    hadoop_conf = spark.sparkContext._jsc.hadoopConfiguration()
    fs = spark.sparkContext._jvm.org.apache.hadoop.fs.FileSystem.get(
        hadoop_conf
    )

    existing_csv_paths = []
    print("\nChecking HDFS directories and CSV files:")
    print("-" * 70)

    for path in paths:
        hdfs_path = spark.sparkContext._jvm.org.apache.hadoop.fs.Path(path)

        if not fs.exists(hdfs_path):
            print(f"[NOT FOUND] {path}")
            continue

        print(f"[FOUND]     {path}")

        status = fs.getFileStatus(hdfs_path)
        if not status.isDirectory():
            print(f"[NOT DIR]   {path}")
            continue

        file_statuses = fs.listStatus(hdfs_path)
        csv_files = []

        for file_status in file_statuses:
            if not file_status.isFile():
                continue

            file_path = file_status.getPath().toString()
            if file_path.lower().endswith(".csv"):
                csv_files.append(file_path)

        if csv_files:
            print(f"[FOUND]     {path}/*.csv ({len(csv_files)} file(s))")
            for csv_file in csv_files:
                print(f"             -> {csv_file}")
            existing_csv_paths.extend(csv_files)
        else:
            print(f"[NO CSV]    {path}/*.csv")

    print("-" * 70)

    if not existing_csv_paths:
        raise FileNotFoundError(
            f"No CSV files found between {start_date} and {end_date} in {base_dir}"
        )

    print("\nCSV files that will be read:")
    print("-" * 70)
    for csv_file in existing_csv_paths:
        print(csv_file)
    print("-" * 70)
    print(f"Total CSV files: {len(existing_csv_paths)}")

    # Read CSV
    df = (
        spark.read.option("header", "true")
        .option("inferSchema", "true")
        .csv(existing_csv_paths)
    )

    print("\nCSV files successfully loaded.")

    # Force ONE Partition
    print(f"\nPartitions before coalesce: {df.rdd.getNumPartitions()}")
    df = df.coalesce(1)
    print(f"Partitions after coalesce: {df.rdd.getNumPartitions()}")

    number_of_partitions = df.rdd.getNumPartitions()
    if number_of_partitions != 1:
        raise RuntimeError(
            f"Expected exactly 1 partition, but got {number_of_partitions}"
        )

    print("\n[OK] DataFrame has exactly ONE partition.")
    return df


# ============================================================
# 4. Execution & Data Processing
# ============================================================

df = combine_csv_files(
    spark=spark, base_dir=BASE_DIR, start_date=START_DATE, end_date=END_DATE
)

print("\n" + "=" * 70)
print("RESULT INSPECTION")
print("=" * 70)

print("\nSchema:")
df.printSchema()

print("\nColumns:")
print(df.columns)

print("\nSample Data:")
df.show(20, truncate=False)

print(f"\nNumber of columns: {len(df.columns)}")
print(f"Number of rows: {df.count()}")
print(f"Number of partitions: {df.rdd.getNumPartitions()}")

# Clean data: Replace "-" with NULL across all columns
clean_df = df
for column in df.columns:
    clean_df = clean_df.withColumn(
        column,
        F.when(
            F.trim(F.col(column).cast("string")) == "-", F.lit(None)
        ).otherwise(F.col(column)),
    )

# Transformations to build Silver DataFrame
silver_df = (
    clean_df.withColumnRenamed("length(m)", "length_m")
    .withColumnRenamed("beam(m)", "beam_m")
    .withColumn("year_built", F.col("year_built").cast("int"))
    .withColumn("gross_tonnage", F.col("gross_tonnage").cast("bigint"))
    .withColumn("deadweight", F.col("deadweight").cast("bigint"))
    .withColumn("length_m", F.col("length_m").cast("double"))
    .withColumn("beam_m", F.col("beam_m").cast("double"))
    .withColumn(
        "destination_port_lat",
        F.when(
            F.col("destination_port_lat").endswith("S"),
            -F.regexp_extract(
                "destination_port_lat", r"([\d.]+)", 1
            ).cast("double"),
        ).when(
            F.col("destination_port_lat").endswith("N"),
            F.regexp_extract("destination_port_lat", r"([\d.]+)", 1).cast(
                "double"
            ),
        ),
    )
    .withColumn(
        "destination_port_lon",
        F.when(
            F.col("destination_port_lon").endswith("W"),
            -F.regexp_extract(
                "destination_port_lon", r"([\d.]+)", 1
            ).cast("double"),
        ).when(
            F.col("destination_port_lon").endswith("E"),
            F.regexp_extract("destination_port_lon", r"([\d.]+)", 1).cast(
                "double"
            ),
        ),
    )
    .withColumn("ingestion_year", F.year("ingestion_date"))
    .withColumn("ingestion_month", F.month("ingestion_date"))
)

# ============================================================
# 5. Upsert Logic & Hive Insertion
# ============================================================

existing_df = hive_df.join(
    silver_df.select("name").distinct(), on="name", how="left_anti"
)
upsert_df = existing_df.unionByName(silver_df)




print("\nUpsert Metrics:")
print("Existing rows:", hive_df.count())
print("New rows:", silver_df.count())
print("Upsert rows:", upsert_df.count())

upsert_df.show(20, truncate=False)



# i have to drop and create the table again because i can not upsert normally so this  a work around
spark.sql("""
DROP TABLE IF EXISTS silver.vessels
""")

spark.sql("""
CREATE TABLE silver.vessels (
    name                       STRING,
    type                       STRING,
    year_built                 INT,
    gross_tonnage              BIGINT,
    deadweight                 BIGINT,
    length_m                   DOUBLE,
    beam_m                     DOUBLE,
    detail_link                STRING,

    departure_date             TIMESTAMP,
    last_port_country          STRING,
    last_port_name             STRING,

    arrival_date               TIMESTAMP,

    destination_port_country   STRING,
    destination_port_name      STRING,
    destination_port_lat       STRING,
    destination_port_lon       STRING,

    reported_status            STRING,
    report_date                TIMESTAMP,

    data_source                STRING,
    ingestion_timestamp        TIMESTAMP,
    ingestion_date             DATE
)
PARTITIONED BY (
    ingestion_year             INT,
    ingestion_month            INT
)
STORED AS ORC
""")



# Register as temp view to perform standard Spark SQL insertion into Hive
upsert_df.createOrReplaceTempView("silver_events_source")

spark.sql("""
    INSERT INTO TABLE silver.vessels
    PARTITION (ingestion_year, ingestion_month)
    SELECT
        name,
        type,
        year_built,
        gross_tonnage,
        deadweight,
        length_m,
        beam_m,
        detail_link,
        departure_date,
        last_port_country,
        last_port_name,
        arrival_date,
        destination_port_country,
        destination_port_name,
        destination_port_lat,
        destination_port_lon,
        reported_status,
        report_date,
        data_source,
        ingestion_timestamp,
        ingestion_date,
        ingestion_year,
        ingestion_month
    FROM silver_events_source
""")

print("\nFinal Hive Count:")
spark.sql("SELECT COUNT(*) FROM silver.vessels").show()

# Stop session
spark.stop()