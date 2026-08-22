from pyspark.sql import SparkSession
from pyspark.sql.functions import current_date, lit, current_timestamp

spark = SparkSession.builder \
    .appName("TidaLine_Archive_ODS") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

sfOptions = {
    "sfURL": "odaycog-ge22071.snowflakecomputing.com",
    "sfUser": "AYMAN",
    "sfPassword": "ayman@Snowflake1",
    "sfDatabase": "TIDALINE_DB",
    "sfSchema": "PUBLIC",
    "sfWarehouse": "TIDALINE_WH",
    "sfRole": "ACCOUNTADMIN"
}

print("Extracting data from Snowflake ODS...")
ods_df = spark.read \
    .format("net.snowflake.spark.snowflake") \
    .options(**sfOptions) \
    .option("dbtable", "ODS_EARTHQUAKES") \
    .load()

archive_df = ods_df.withColumn("archive_date", current_date()) \
    .withColumn("loaded_to_silver", current_timestamp())

output_path = "/data/my_data"
print(f"Archiving data to {output_path}...")

archive_df.coalesce(1).write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv("hdfs:///data/my_data")
print("Archive job completed successfully!")

spark.stop()