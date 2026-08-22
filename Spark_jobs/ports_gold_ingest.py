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
    .appName("ports_silver_to_gold") \
    .enableHiveSupport() \
    .config("spark.sql.sources.partitionOverwriteMode", "dynamic") \
    .config("spark.sql.warehouse.dir", "hdfs://bdss/user/hive/warehouse") \
    .config("spark.hadoop.hive.metastore.uris", "thrift://hive:9083") \
    .config("spark.sql.hive.metastore.version", "4.1.0") \
    .config("spark.sql.hive.metastore.jars", "path") \
    .config("spark.sql.hive.metastore.jars.path", "hdfs://bdss/user/spark/hive4-jars/*") \
    .getOrCreate()

# ──────────────────────────────────────────────
# READ FROM SILVER
# ──────────────────────────────────────────────
df_silver = spark.sql(f"SELECT * FROM silver.ports WHERE year='{year}' AND month='{month}'")

# ──────────────────────────────────────────────
# RENAME COLUMNS + DROP RESTRICTION COLUMNS
# ──────────────────────────────────────────────
df_renamed = df_silver \
    .withColumnRenamed("OID_", "port_id") \
    .withColumnRenamed("World Port Index Number", "wpi_number") \
    .withColumnRenamed("Region Name", "region_name") \
    .withColumnRenamed("Main Port Name", "port_name") \
    .withColumnRenamed("Alternate Port Name", "alt_port_name") \
    .withColumnRenamed("UN/LOCODE", "un_locode") \
    .withColumnRenamed("Country Code", "country_code") \
    .withColumnRenamed("World Water Body", "water_body") \
    .withColumnRenamed("Sailing Direction or Publication", "sailing_direction") \
    .withColumnRenamed("Tidal Range (m)", "tidal_range_m") \
    .withColumnRenamed("Entrance Width (m)", "entrance_width_m") \
    .withColumnRenamed("Channel Depth (m)", "channel_depth_m") \
    .withColumnRenamed("Anchorage Depth (m)", "anchorage_depth_m") \
    .withColumnRenamed("Cargo Pier Depth (m)", "cargo_pier_depth_m") \
    .withColumnRenamed("Oil Terminal Depth (m)", "oil_terminal_depth_m") \
    .withColumnRenamed("Liquified Natural Gas Terminal Depth (m)", "lng_terminal_depth_m") \
    .withColumnRenamed("Maximum Vessel Length (m)", "max_vessel_length_m") \
    .withColumnRenamed("Maximum Vessel Beam (m)", "max_vessel_beam_m") \
    .withColumnRenamed("Maximum Vessel Draft (m)", "max_vessel_draft_m") \
    .withColumnRenamed("Offshore Maximum Vessel Length (m)", "offshore_max_vessel_length_m") \
    .withColumnRenamed("Offshore Maximum Vessel Beam (m)", "offshore_max_vessel_beam_m") \
    .withColumnRenamed("Offshore Maximum Vessel Draft (m)", "offshore_max_vessel_draft_m") \
    .withColumnRenamed("Harbor Size", "harbor_size") \
    .withColumnRenamed("Harbor Type", "harbor_type") \
    .withColumnRenamed("Harbor Use", "harbor_use") \
    .withColumnRenamed("Shelter Afforded", "shelter_afforded") \
    .withColumnRenamed("Communications - Telephone", "has_communication_telephone") \
    .withColumnRenamed("Communications - Telefax", "has_communication_telefax") \
    .withColumnRenamed("Communications - Radio", "has_communication_radio") \
    .withColumnRenamed("Communications - Radiotelephone", "has_communication_radiotelephone") \
    .withColumnRenamed("Communications - Airport", "has_communication_airport") \
    .withColumnRenamed("Communications - Rail", "has_communication_rail") \
    .withColumnRenamed("Medical Facilities", "has_medical_facilities") \
    .withColumnRenamed("Supplies - Provisions", "has_supplies_provisions") \
    .withColumnRenamed("Supplies - Potable Water", "has_supplies_potable_water") \
    .withColumnRenamed("Supplies - Fuel Oil", "has_supplies_fuel_oil") \
    .withColumnRenamed("Supplies - Diesel Oil", "has_supplies_diesel_oil") \
    .withColumnRenamed("Supplies - Aviation Fuel", "has_supplies_aviation_fuel") \
    .withColumnRenamed("Supplies - Deck", "has_supplies_deck") \
    .withColumnRenamed("Supplies - Engine", "has_supplies_engine") \
    .withColumnRenamed("Latitude", "latitude") \
    .withColumnRenamed("Longitude", "longitude") \
    .drop("Entrance Restriction - Tide") \
    .drop("Entrance Restriction - Heavy Swell") \
    .drop("Entrance Restriction - Ice") \
    .drop("Entrance Restriction - Other")

# ──────────────────────────────────────────────
# FLAG TRANSFORMATION
# ──────────────────────────────────────────────
flag_cols = [
    "has_communication_telephone", "has_communication_telefax",
    "has_communication_radio", "has_communication_radiotelephone",
    "has_communication_airport", "has_communication_rail",
    "has_medical_facilities", "has_supplies_provisions",
    "has_supplies_potable_water", "has_supplies_fuel_oil",
    "has_supplies_diesel_oil", "has_supplies_aviation_fuel",
    "has_supplies_deck", "has_supplies_engine"
]

df_flags = df_renamed

for col in flag_cols:
    df_flags = df_flags.withColumn(
        col,
        F.when(F.col(col) == "Y", 1).otherwise(0)
    )

df_flags = df_flags.withColumn(
    "has_repairs",
    F.when(
        F.col("Repairs").isNull() |
        (F.trim(F.col("Repairs")) == "") |
        (F.upper(F.trim(F.col("Repairs"))) == "UNKNOWN"),
        0
    ).otherwise(1)
).drop("Repairs")

# ──────────────────────────────────────────────
# INDEXES
# ──────────────────────────────────────────────
df_indexed = df_flags \
    .withColumn(
        "communications_index",
        F.col("has_communication_radio") +
        F.col("has_communication_telephone") +
        F.col("has_communication_airport") +
        F.col("has_communication_telefax")
    ) \
    .withColumn(
        "communications_index_category",
        F.when(F.col("communications_index") == 4, "Excellent")
         .when(F.col("communications_index") >= 2, "Good")
         .when(F.col("communications_index") == 1, "Limited")
         .otherwise("Unavailable")
    ) \
    .withColumn(
        "supplies_index",
        F.col("has_supplies_provisions") +
        F.col("has_supplies_fuel_oil") +
        F.col("has_supplies_diesel_oil") +
        F.col("has_supplies_potable_water") +
        F.col("has_repairs")
    ) \
    .withColumn(
        "supplies_index_category",
        F.when(F.col("supplies_index") == 5, "Excellent")
         .when(F.col("supplies_index") >= 3, "Good")
         .when(F.col("supplies_index") >= 1, "Limited")
         .otherwise("Unavailable")
    )

# ──────────────────────────────────────────────
# METADATA
# ──────────────────────────────────────────────
df_final = df_indexed \
    .withColumn("ingestion_date", F.to_date(F.lit(f"{year}-{month}-01"))) \
    .withColumn("ingested_to_gold_at", F.current_timestamp()) \
    .withColumn("year", F.lit(year)) \
    .withColumn("month", F.lit(month))

# ──────────────────────────────────────────────
# HIVE DATABASE + TABLE
# ──────────────────────────────────────────────
spark.sql("CREATE DATABASE IF NOT EXISTS gold")

spark.sql("""
    CREATE TABLE IF NOT EXISTS gold.dim_ports (
        port_id INT,
        wpi_number INT,
        region_name STRING,
        port_name STRING,
        alt_port_name STRING,
        un_locode STRING,
        country_code STRING,
        water_body STRING,
        sailing_direction STRING,
        tidal_range_m DOUBLE,
        entrance_width_m DOUBLE,
        channel_depth_m DOUBLE,
        anchorage_depth_m DOUBLE,
        cargo_pier_depth_m DOUBLE,
        oil_terminal_depth_m DOUBLE,
        lng_terminal_depth_m DOUBLE,
        max_vessel_length_m DOUBLE,
        max_vessel_beam_m DOUBLE,
        max_vessel_draft_m DOUBLE,
        offshore_max_vessel_length_m DOUBLE,
        offshore_max_vessel_beam_m DOUBLE,
        offshore_max_vessel_draft_m DOUBLE,
        harbor_size STRING,
        harbor_type STRING,
        harbor_use STRING,
        shelter_afforded STRING,
        has_communication_telephone INT,
        has_communication_telefax INT,
        has_communication_radio INT,
        has_communication_radiotelephone INT,
        has_communication_airport INT,
        has_communication_rail INT,
        has_medical_facilities INT,
        has_supplies_provisions INT,
        has_supplies_potable_water INT,
        has_supplies_fuel_oil INT,
        has_supplies_diesel_oil INT,
        has_supplies_aviation_fuel INT,
        has_supplies_deck INT,
        has_supplies_engine INT,
        has_repairs INT,
        communications_index INT,
        communications_index_category STRING,
        supplies_index INT,
        supplies_index_category STRING,
        latitude DOUBLE,
        longitude DOUBLE,
        ingested_at TIMESTAMP,
        source_name STRING,
        ingested_to_silver_at TIMESTAMP,
        ingestion_date DATE,
        ingested_to_gold_at TIMESTAMP
    )
    PARTITIONED BY (year STRING, month STRING)
    STORED AS ORC

""")

# ──────────────────────────────────────────────
# WRITE TO GOLD
# ──────────────────────────────────────────────
df_final.write \
    .mode("overwrite") \
    .format("orc") \
    .partitionBy("year", "month") \
    .saveAsTable("gold.dim_ports")

spark.stop()
