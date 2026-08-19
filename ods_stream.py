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

parsed_df = kafka_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), debezium_schema).alias("data")) \
    .select("data.payload.op", "data.payload.after.*") \
    .filter("op != 'd'") \
    .drop("op") \
    .withColumn("ingestion_source", lit("Debezium-Kafka-Stream")) \
    .withColumn("ingestion_timestamp", current_timestamp())


def write_to_ods(batch_df, batch_id):
    batch_df.write \
        .format("net.snowflake.spark.snowflake") \
        .options(**sfOptions) \
        .option("dbtable", "ODS_EARTHQUAKES") \
        .mode("append") \
        .save()

query = parsed_df.writeStream \
    .foreachBatch(write_to_ods) \
    .start()

query.awaitTermination()