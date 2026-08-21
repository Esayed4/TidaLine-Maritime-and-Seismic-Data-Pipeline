CREATE DATABASE IF NOT EXISTS silver;

CREATE TABLE IF NOT EXISTS silver.vessels (
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
    destination_port_name     STRING,
    destination_port_lat      STRING,
    destination_port_lon      STRING,

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
STORED AS ORC;
