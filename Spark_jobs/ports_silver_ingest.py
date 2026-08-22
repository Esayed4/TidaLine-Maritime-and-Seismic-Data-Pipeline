import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# ──────────────────────────────────────────────
# ARGS
# ──────────────────────────────────────────────
year = sys.argv[1]
month = sys.argv[2]

# ──────────────────────────────────────────────
# SPARK SESSION
# ──────────────────────────────────────────────
spark = SparkSession.builder \
    .appName("ports_bronze_to_silver") \
    .enableHiveSupport() \
    .config("spark.sql.sources.partitionOverwriteMode", "dynamic") \
    .config("spark.sql.warehouse.dir", "hdfs://bdss/user/hive/warehouse") \
    .config("spark.hadoop.hive.metastore.uris", "thrift://hive:9083") \
    .config("spark.sql.hive.metastore.version", "4.1.0") \
    .config("spark.sql.hive.metastore.jars", "path") \
    .config("spark.sql.hive.metastore.jars.path", "hdfs://bdss/user/spark/hive4-jars/*") \
    .getOrCreate()

# ──────────────────────────────────────────────
# READ BRONZE
# ──────────────────────────────────────────────
bronze_path = f"hdfs://bdss/lake/bronze/ports/year={year}/month={month}/"

df_bronze = spark.read \
    .option("header", True) \
    .option("inferSchema", False) \
    .csv(bronze_path)

# ──────────────────────────────────────────────
# SELECT COLUMNS
# ──────────────────────────────────────────────
cols_to_keep = [
    "OID_",
    "World Port Index Number",
    "Region Name",
    "Main Port Name",
    "Alternate Port Name",
    "UN/LOCODE",
    "Country Code",
    "World Water Body",
    "Sailing Direction or Publication",
    "Tidal Range (m)",
    "Entrance Width (m)",
    "Channel Depth (m)",
    "Anchorage Depth (m)",
    "Cargo Pier Depth (m)",
    "Oil Terminal Depth (m)",
    "Liquified Natural Gas Terminal Depth (m)",
    "Maximum Vessel Length (m)",
    "Maximum Vessel Beam (m)",
    "Maximum Vessel Draft (m)",
    "Offshore Maximum Vessel Length (m)",
    "Offshore Maximum Vessel Beam (m)",
    "Offshore Maximum Vessel Draft (m)",
    "Harbor Size",
    "Harbor Type",
    "Harbor Use",
    "Shelter Afforded",
    "Entrance Restriction - Tide",
    "Entrance Restriction - Heavy Swell",
    "Entrance Restriction - Ice",
    "Entrance Restriction - Other",
    "Communications - Telephone",
    "Communications - Telefax",
    "Communications - Radio",
    "Communications - Radiotelephone",
    "Communications - Airport",
    "Communications - Rail",
    "Medical Facilities",
    "Supplies - Provisions",
    "Supplies - Potable Water",
    "Supplies - Fuel Oil",
    "Supplies - Diesel Oil",
    "Supplies - Aviation Fuel",
    "Supplies - Deck",
    "Supplies - Engine",
    "Repairs",
    "Dry Dock",
    "Railway",
    "Latitude",
    "Longitude",
    "ingested_at",
    "source_name"
]

df_selected = df_bronze.select(cols_to_keep)

# ──────────────────────────────────────────────
# ENFORCE DATA TYPES
# ──────────────────────────────────────────────
integer_cols = [
    "OID_",
    "World Port Index Number"
]

numeric_cols = [
    "Tidal Range (m)", "Entrance Width (m)", "Channel Depth (m)",
    "Anchorage Depth (m)", "Cargo Pier Depth (m)", "Oil Terminal Depth (m)",
    "Liquified Natural Gas Terminal Depth (m)", "Maximum Vessel Length (m)",
    "Maximum Vessel Beam (m)", "Maximum Vessel Draft (m)",
    "Offshore Maximum Vessel Length (m)", "Offshore Maximum Vessel Beam (m)",
    "Offshore Maximum Vessel Draft (m)", "Latitude", "Longitude"
]

df_typed = df_selected

for col in integer_cols:
    df_typed = df_typed.withColumn(col, F.col(col).cast("double").cast("int"))

for col in numeric_cols:
    df_typed = df_typed.withColumn(col, F.col(col).cast("double"))

df_typed = df_typed.withColumn("ingested_at", F.col("ingested_at").cast("timestamp"))

# ──────────────────────────────────────────────
# FLAG NORMALIZATION
# ──────────────────────────────────────────────
flag_cols = [
    "Entrance Restriction - Tide", "Entrance Restriction - Heavy Swell",
    "Entrance Restriction - Ice", "Entrance Restriction - Other",
    "Communications - Telephone", "Communications - Telefax",
    "Communications - Radio", "Communications - Radiotelephone",
    "Communications - Airport", "Communications - Rail",
    "Medical Facilities",
    "Supplies - Provisions", "Supplies - Potable Water", "Supplies - Fuel Oil",
    "Supplies - Diesel Oil", "Supplies - Aviation Fuel", "Supplies - Deck",
    "Supplies - Engine"
]

df_flagged = df_typed

for col in flag_cols:
    df_flagged = df_flagged.withColumn(
        col,
        F.when(F.col(col).isNull(), None)
         .otherwise(F.upper(F.substring(F.trim(F.col(col)), 1, 1)))
    )

# ──────────────────────────────────────────────
# DEDUP + METADATA
# ──────────────────────────────────────────────
df_deduped = df_flagged.dropDuplicates()

df_final = df_deduped \
    .withColumn("ingested_to_silver_at", F.current_timestamp()) \
    .withColumn("year", F.lit(year)) \
    .withColumn("month", F.lit(month))

# ──────────────────────────────────────────────
# HIVE DATABASE + TABLE
# ──────────────────────────────────────────────
spark.sql("CREATE DATABASE IF NOT EXISTS silver")

spark.sql("""
    CREATE TABLE IF NOT EXISTS silver.ports (
        `OID_` INT,
        `World Port Index Number` INT,
        `Region Name` STRING,
        `Main Port Name` STRING,
        `Alternate Port Name` STRING,
        `UN/LOCODE` STRING,
        `Country Code` STRING,
        `World Water Body` STRING,
        `Sailing Direction or Publication` STRING,
        `Tidal Range (m)` DOUBLE,
        `Entrance Width (m)` DOUBLE,
        `Channel Depth (m)` DOUBLE,
        `Anchorage Depth (m)` DOUBLE,
        `Cargo Pier Depth (m)` DOUBLE,
        `Oil Terminal Depth (m)` DOUBLE,
        `Liquified Natural Gas Terminal Depth (m)` DOUBLE,
        `Maximum Vessel Length (m)` DOUBLE,
        `Maximum Vessel Beam (m)` DOUBLE,
        `Maximum Vessel Draft (m)` DOUBLE,
        `Offshore Maximum Vessel Length (m)` DOUBLE,
        `Offshore Maximum Vessel Beam (m)` DOUBLE,
        `Offshore Maximum Vessel Draft (m)` DOUBLE,
        `Harbor Size` STRING,
        `Harbor Type` STRING,
        `Harbor Use` STRING,
        `Shelter Afforded` STRING,
        `Entrance Restriction - Tide` STRING,
        `Entrance Restriction - Heavy Swell` STRING,
        `Entrance Restriction - Ice` STRING,
        `Entrance Restriction - Other` STRING,
        `Communications - Telephone` STRING,
        `Communications - Telefax` STRING,
        `Communications - Radio` STRING,
        `Communications - Radiotelephone` STRING,
        `Communications - Airport` STRING,
        `Communications - Rail` STRING,
        `Medical Facilities` STRING,
        `Supplies - Provisions` STRING,
        `Supplies - Potable Water` STRING,
        `Supplies - Fuel Oil` STRING,
        `Supplies - Diesel Oil` STRING,
        `Supplies - Aviation Fuel` STRING,
        `Supplies - Deck` STRING,
        `Supplies - Engine` STRING,
        `Repairs` STRING,
        `Dry Dock` STRING,
        `Railway` STRING,
        `Latitude` DOUBLE,
        `Longitude` DOUBLE,
        `ingested_at` TIMESTAMP,
        `source_name` STRING,
        `ingested_to_silver_at` TIMESTAMP
    )
    PARTITIONED BY (year STRING, month STRING)
    STORED AS ORC
""")

# ──────────────────────────────────────────────
# WRITE TO SILVER
# ──────────────────────────────────────────────
df_final.write \
    .mode("overwrite") \
    .format("orc") \
    .partitionBy("year", "month") \
    .saveAsTable("silver.ports")

spark.stop()
