from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, lit, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = SparkSession.builder \
    .appName("TidaLine_ODS_Stream") \
    .master("local[*]") \
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

debezium_schema = StructType([
    StructField("payload", StructType([
        StructField("op", StringType()),
        StructField("after", StructType([
            StructField("unid", StringType()),
            StructField("source_id", StringType()),
            StructField("flynn_region", StringType()),
            StructField("lat", DoubleType()),
            StructField("lon", DoubleType()),
            StructField("depth", DoubleType()),
            StructField("mag", DoubleType()),
            StructField("action", StringType())
        ]))
    ]))
])

kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "cdc.public.earthquakes") \
    .option("startingOffsets", "earliest") \
    .load()

parsed_df = kafka_df.selectExpr("CAST(value AS STRING)", "timestamp AS generated_at") \
    .select(from_json(col("value"), debezium_schema).alias("data"), col("generated_at")) \
    .filter("data.payload.op != 'd'") \
    .select("data.payload.after.*", "generated_at") \
    .withColumn("source_name", lit("Debezium-Kafka-Stream")) \
    .withColumn("ingested_at", current_timestamp())

def write_to_ods(batch_df, batch_id):
    row_count = batch_df.count()
    print(f"==== BATCH {batch_id} | ROWS: {row_count} ====")
    
    if row_count == 0:
        return
        
    batch_df.show(3, False)

    merge_query = """
    MERGE INTO PUBLIC.ODS_EARTHQUAKES target
    USING PUBLIC.ODS_EARTHQUAKES_STAGING source
    ON target.unid = source.unid
    WHEN MATCHED THEN
        UPDATE SET 
            target.source_id = source.source_id,
            target.flynn_region = source.flynn_region,
            target.lat = source.lat,
            target.lon = source.lon,
            target.depth = source.depth,
            target.mag = source.mag,
            target.action = source.action,
            target.generated_at = source.generated_at,
            target.source_name = source.source_name,
            target.ingested_at = source.ingested_at
    WHEN NOT MATCHED THEN
        INSERT (unid, source_id, flynn_region, lat, lon, depth, mag, action, generated_at, source_name, ingested_at)
        VALUES (source.unid, source.source_id, source.flynn_region, source.lat, source.lon, source.depth, source.mag, source.action, source.generated_at, source.source_name, source.ingested_at)
    """

    batch_df.write \
        .format("net.snowflake.spark.snowflake") \
        .options(**sfOptions) \
        .option("dbtable", "ODS_EARTHQUAKES_STAGING") \
        .option("postactions", merge_query) \
        .mode("overwrite") \
        .save() 

query = parsed_df.writeStream \
    .foreachBatch(write_to_ods) \
    .start()

query.awaitTermination()