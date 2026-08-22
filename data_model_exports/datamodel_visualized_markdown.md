# Untitled Diagram documentation
## Summary

- [Introduction](#introduction)
- [Database Type](#database-type)
- [Table Structure](#table-structure)
	- [Bronze_Ports](#bronze_ports)
	- [Bronze_Vessels](#bronze_vessels)
	- [Bronze_Seismic](#bronze_seismic)
	- [Silver_Ports](#silver_ports)
	- [Silver_Vessels](#silver_vessels)
	- [Silver_Seismic](#silver_seismic)
	- [Dim_Date](#dim_date)
	- [Dim_Time](#dim_time)
	- [Dim_Ports](#dim_ports)
	- [Gold_Vessels](#gold_vessels)
	- [Gold_Seismic](#gold_seismic)
- [Relationships](#relationships)
- [Database Diagram](#database-diagram)

## Introduction

## Database type

- **Database system:** MySQL
## Table structure

### Bronze_Ports

| Name                                         | Type         | Settings                       | References | Note |
| -------------------------------------------- | ------------ | ------------------------------ | ---------- | ---- |
| **OID_**                                     | INTEGER      | 🔑 PK, not null, autoincrement |            |      |
| **World Port Index Number**                  | INTEGER      | not null, unique               |            |      |
| **Region Name**                              | VARCHAR(255) | null                           |            |      |
| **Main Port Name**                           | VARCHAR(255) | not null                       |            |      |
| **Alternate Port Name**                      | VARCHAR(255) | null                           |            |      |
| **UN/LOCODE**                                | VARCHAR(255) | null                           |            |      |
| **Country Code**                             | VARCHAR(255) | not null                       |            |      |
| **World Water Body**                         | VARCHAR(255) | not null                       |            |      |
| **IHO S-130 Sea Area**                       | VARCHAR(255) | null                           |            |      |
| **Sailing Direction or Publication**         | VARCHAR(255) | not null                       |            |      |
| **Publication Link**                         | VARCHAR(255) | null                           |            |      |
| **Standard Nautical Chart**                  | VARCHAR(255) | null                           |            |      |
| **IHO S-57 Electronic Navigational Chart**   | VARCHAR(255) | null                           |            |      |
| **IHO S-101 Electronic Navigational Chart**  | VARCHAR(255) | null                           |            |      |
| **Digital Nautical Chart**                   | VARCHAR(255) | null                           |            |      |
| **Tidal Range (m)**                          | DECIMAL      | null                           |            |      |
| **Entrance Width (m)**                       | DECIMAL      | null                           |            |      |
| **Channel Depth (m)**                        | DECIMAL      | null                           |            |      |
| **Anchorage Depth (m)**                      | DECIMAL      | null                           |            |      |
| **Cargo Pier Depth (m)**                     | DECIMAL      | null                           |            |      |
| **Oil Terminal Depth (m)**                   | DECIMAL      | not null                       |            |      |
| **Liquified Natural Gas Terminal Depth (m)** | DECIMAL      | null                           |            |      |
| **Maximum Vessel Length (m)**                | DECIMAL      | null                           |            |      |
| **Maximum Vessel Beam (m)**                  | DECIMAL      | null                           |            |      |
| **Maximum Vessel Draft (m)**                 | DECIMAL      | null                           |            |      |
| **Offshore Maximum Vessel Length (m)**       | DECIMAL      | null                           |            |      |
| **Offshore Maximum Vessel Beam (m)**         | DECIMAL      | null                           |            |      |
| **Offshore Maximum Vessel Draft (m)**        | DECIMAL      | null                           |            |      |
| **Harbor Size**                              | VARCHAR(255) | null                           |            |      |
| **Harbor Type**                              | VARCHAR(255) | null                           |            |      |
| **Harbor Use**                               | VARCHAR(255) | null                           |            |      |
| **Shelter Afforded**                         | VARCHAR(255) | null                           |            |      |
| **Entrance Restriction - Tide**              | VARCHAR(255) | null                           |            |      |
| **Entrance Restriction - Heavy Swell**       | VARCHAR(255) | null                           |            |      |
| **Entrance Restriction - Ice**               | VARCHAR(255) | null                           |            |      |
| **Entrance Restriction - Other**             | VARCHAR(255) | null                           |            |      |
| **Overhead Limits**                          | VARCHAR(255) | null                           |            |      |
| **Underkeel Clearance Management System**    | VARCHAR(255) | null                           |            |      |
| **Good Holding Ground**                      | VARCHAR(255) | null                           |            |      |
| **Turning Area**                             | VARCHAR(255) | null                           |            |      |
| **Port Security**                            | VARCHAR(255) | null                           |            |      |
| **Estimated Time of Arrival Message**        | VARCHAR(255) | null                           |            |      |
| **Quarantine - Pratique**                    | VARCHAR(255) | null                           |            |      |
| **Quarantine - Sanitation**                  | VARCHAR(255) | null                           |            |      |
| **Quarantine - Other**                       | VARCHAR(255) | null                           |            |      |
| **Traffic Separation Scheme**                | VARCHAR(255) | null                           |            |      |
| **Vessel Traffic Service**                   | VARCHAR(255) | null                           |            |      |
| **First Port of Entry**                      | VARCHAR(255) | null                           |            |      |
| **US Representative**                        | VARCHAR(255) | null                           |            |      |
| **Pilotage - Compulsory**                    | VARCHAR(255) | null                           |            |      |
| **Pilotage - Available**                     | VARCHAR(255) | null                           |            |      |
| **Pilotage - Local Assistance**              | VARCHAR(255) | null                           |            |      |
| **Pilotage - Advisable**                     | VARCHAR(255) | null                           |            |      |
| **Tugs - Salvage**                           | VARCHAR(255) | null                           |            |      |
| **Tugs - Assistance**                        | VARCHAR(255) | null                           |            |      |
| **Communications - Telephone**               | VARCHAR(255) | null                           |            |      |
| **Communications - Telefax**                 | VARCHAR(255) | null                           |            |      |
| **Communications - Radio**                   | VARCHAR(255) | null                           |            |      |
| **Communications - Radiotelephone**          | VARCHAR(255) | null                           |            |      |
| **Communications - Airport**                 | VARCHAR(255) | null                           |            |      |
| **Communications - Rail**                    | VARCHAR(255) | null                           |            |      |
| **Search and Rescue**                        | VARCHAR(255) | null                           |            |      |
| **NAVAREA**                                  | VARCHAR(255) | null                           |            |      |
| **Facilities - Wharves**                     | VARCHAR(255) | null                           |            |      |
| **Facilities - Anchorage**                   | VARCHAR(255) | null                           |            |      |
| **Facilities - Dangerous Cargo Anchorage**   | VARCHAR(255) | null                           |            |      |
| **Facilities - Med Mooring**                 | VARCHAR(255) | null                           |            |      |
| **Facilities - Beach Mooring**               | VARCHAR(255) | null                           |            |      |
| **Facilities - Ice Mooring**                 | VARCHAR(255) | null                           |            |      |
| **Facilities - Ro-Ro**                       | VARCHAR(255) | null                           |            |      |
| **Facilities - Solid Bulk**                  | VARCHAR(255) | null                           |            |      |
| **Facilities - Liquid Bulk**                 | VARCHAR(255) | null                           |            |      |
| **Facilities - Container**                   | VARCHAR(255) | null                           |            |      |
| **Facilities - Breakbulk**                   | VARCHAR(255) | null                           |            |      |
| **Facilities - Oil Terminal**                | VARCHAR(255) | null                           |            |      |
| **Facilities - LNG Terminal**                | VARCHAR(255) | null                           |            |      |
| **Facilities - Other**                       | VARCHAR(255) | null                           |            |      |
| **Medical Facilities**                       | VARCHAR(255) | null                           |            |      |
| **Garbage Disposal**                         | VARCHAR(255) | null                           |            |      |
| **Chemical Holding Tank Disposal**           | VARCHAR(255) | null                           |            |      |
| **Degaussing**                               | VARCHAR(255) | null                           |            |      |
| **Dirty Ballast Disposal**                   | VARCHAR(255) | null                           |            |      |
| **Cranes - Fixed**                           | VARCHAR(255) | null                           |            |      |
| **Cranes - Mobile**                          | VARCHAR(255) | null                           |            |      |
| **Cranes - Floating**                        | VARCHAR(255) | null                           |            |      |
| **Cranes Container**                         | VARCHAR(255) | null                           |            |      |
| **Lifts - 100+ Tons**                        | VARCHAR(255) | null                           |            |      |
| **Lifts - 50-100 Tons**                      | VARCHAR(255) | null                           |            |      |
| **Lifts - 25-49 Tons**                       | VARCHAR(255) | null                           |            |      |
| **Lifts - 0-24 Tons**                        | VARCHAR(255) | null                           |            |      |
| **Services - Longshoremen**                  | VARCHAR(255) | null                           |            |      |
| **Services - Electricity**                   | VARCHAR(255) | null                           |            |      |
| **Services -Steam**                          | VARCHAR(255) | null                           |            |      |
| **Services - Navigation Equipment**          | VARCHAR(255) | null                           |            |      |
| **Services - Electrical Repair**             | VARCHAR(255) | null                           |            |      |
| **Services - Ice Breaking**                  | VARCHAR(255) | null                           |            |      |
| **Services -Diving**                         | VARCHAR(255) | null                           |            |      |
| **Supplies - Provisions**                    | VARCHAR(255) | null                           |            |      |
| **Supplies - Potable Water**                 | VARCHAR(255) | null                           |            |      |
| **Supplies - Fuel Oil**                      | VARCHAR(255) | null                           |            |      |
| **Supplies - Diesel Oil**                    | VARCHAR(255) | null                           |            |      |
| **Supplies - Aviation Fuel**                 | VARCHAR(255) | null                           |            |      |
| **Supplies - Deck**                          | VARCHAR(255) | null                           |            |      |
| **Supplies - Engine**                        | VARCHAR(255) | null                           |            |      |
| **Repairs**                                  | VARCHAR(255) | null                           |            |      |
| **Dry Dock**                                 | VARCHAR(255) | null                           |            |      |
| **Railway**                                  | VARCHAR(255) | null                           |            |      |
| **Latitude**                                 | DECIMAL      | null                           |            |      |
| **Longitude**                                | DECIMAL      | null                           |            |      |
| **source name**                              | VARCHAR(255) | null                           |            |      |
| **Ingested at**                              | TIMESTAMP    | null                           |            |      | 


### Bronze_Vessels

| Name                         | Type         | Settings        | References | Note |
| ---------------------------- | ------------ | --------------- | ---------- | ---- |
| **name**                     | VARCHAR(255) | 🔑 PK, not null |            |      |
| **type**                     | VARCHAR(255) | null            |            |      |
| **year_built**               | VARCHAR(255) | null            |            |      |
| **gross_tonnage**            | VARCHAR(255) | null            |            |      |
| **dead_weight**              | VARCHAR(255) | null            |            |      |
| **length(m)**                | VARCHAR(255) | null            |            |      |
| **beam(m)**                  | VARCHAR(255) | null            |            |      |
| **detail_link**              | VARCHAR(255) | null            |            |      |
| **departure_date**           | TIMESTAMP    | null            |            |      |
| **last_port_country**        | VARCHAR(255) | null            |            |      |
| **last__port_name**          | VARCHAR(255) | null            |            |      |
| **arrival_date**             | TIMESTAMP    | null            |            |      |
| **destination_port_country** | VARCHAR(255) | null            |            |      |
| **destination_port_name**    | VARCHAR(255) | null            |            |      |
| **destination_port_lat**     | DECIMAL      | null            |            |      |
| **destination_port_lon**     | DECIMAL      | null            |            |      |
| **reported_status**          | VARCHAR(255) | null            |            |      |
| **report_date**              | TIMESTAMP    | null            |            |      |
| **source_name**              | VARCHAR(255) | null            |            |      |
| **ingested_at**              | TIMESTAMP    | null            |            |      | 


### Bronze_Seismic

| Name             | Type         | Settings        | References | Note |
| ---------------- | ------------ | --------------- | ---------- | ---- |
| **unid**         | VARCHAR(255) | 🔑 PK, not null |            |      |
| **source_id**    | INTEGER      | null            |            |      |
| **flynn_region** | VARCHAR(255) | null            |            |      |
| **lat**          | DECIMAL      | not null        |            |      |
| **lon**          | DECIMAL      | not null        |            |      |
| **depth**        | DECIMAL      | not null        |            |      |
| **mag**          | DECIMAL      | not null        |            |      |
| **action**       | VARCHAR(255) | null            |            |      |
| **generated_at** | TIMESTAMP    | not null        |            |      |
| **source_name**  | VARCHAR(255) | not null        |            |      |
| **ingested_at**  | TIMESTAMP    | not null        |            |      | 


### Silver_Ports

| Name                                         | Type         | Settings                       | References | Note |
| -------------------------------------------- | ------------ | ------------------------------ | ---------- | ---- |
| **OID_**                                     | INTEGER      | 🔑 PK, not null, autoincrement |            |      |
| **World Port Index Number**                  | INTEGER      | not null, unique               |            |      |
| **Region Name**                              | VARCHAR(255) | null                           |            |      |
| **Main Port Name**                           | VARCHAR(255) | not null                       |            |      |
| **Alternate Port Name**                      | VARCHAR(255) | null                           |            |      |
| **UN/LOCODE**                                | VARCHAR(255) | null                           |            |      |
| **Country Code**                             | VARCHAR(255) | not null                       |            |      |
| **World Water Body**                         | VARCHAR(255) | not null                       |            |      |
| **Sailing Direction or Publication**         | VARCHAR(255) | not null                       |            |      |
| **Tidal Range (m)**                          | DECIMAL      | null                           |            |      |
| **Entrance Width (m)**                       | DECIMAL      | null                           |            |      |
| **Channel Depth (m)**                        | DECIMAL      | null                           |            |      |
| **Anchorage Depth (m)**                      | DECIMAL      | null                           |            |      |
| **Cargo Pier Depth (m)**                     | DECIMAL      | null                           |            |      |
| **Oil Terminal Depth (m)**                   | DECIMAL      | not null                       |            |      |
| **Liquified Natural Gas Terminal Depth (m)** | DECIMAL      | null                           |            |      |
| **Maximum Vessel Length (m)**                | DECIMAL      | null                           |            |      |
| **Maximum Vessel Beam (m)**                  | DECIMAL      | null                           |            |      |
| **Maximum Vessel Draft (m)**                 | DECIMAL      | null                           |            |      |
| **Offshore Maximum Vessel Length (m)**       | DECIMAL      | null                           |            |      |
| **Offshore Maximum Vessel Beam (m)**         | DECIMAL      | null                           |            |      |
| **Offshore Maximum Vessel Draft (m)**        | DECIMAL      | null                           |            |      |
| **Harbor Size**                              | VARCHAR(255) | null                           |            |      |
| **Harbor Type**                              | VARCHAR(255) | null                           |            |      |
| **Harbor Use**                               | VARCHAR(255) | null                           |            |      |
| **Shelter Afforded**                         | VARCHAR(255) | null                           |            |      |
| **Entrance Restriction - Tide**              | CHAR(1)      | null                           |            |      |
| **Entrance Restriction - Heavy Swell**       | CHAR(1)      | null                           |            |      |
| **Entrance Restriction - Ice**               | CHAR(1)      | null                           |            |      |
| **Entrance Restriction - Other**             | CHAR(1)      | null                           |            |      |
| **Communications - Telephone**               | CHAR(1)      | null                           |            |      |
| **Communications - Telefax**                 | CHAR(1)      | null                           |            |      |
| **Communications - Radio**                   | CHAR(1)      | null                           |            |      |
| **Communications - Radiotelephone**          | CHAR(1)      | null                           |            |      |
| **Communications - Airport**                 | CHAR(1)      | null                           |            |      |
| **Communications - Rail**                    | CHAR(1)      | null                           |            |      |
| **Medical Facilities**                       | CHAR(1)      | null                           |            |      |
| **Supplies - Provisions**                    | CHAR(1)      | null                           |            |      |
| **Supplies - Potable Water**                 | CHAR(1)      | null                           |            |      |
| **Supplies - Fuel Oil**                      | CHAR(1)      | null                           |            |      |
| **Supplies - Diesel Oil**                    | CHAR(1)      | null                           |            |      |
| **Supplies - Aviation Fuel**                 | CHAR(1)      | null                           |            |      |
| **Supplies - Deck**                          | CHAR(1)      | null                           |            |      |
| **Supplies - Engine**                        | CHAR(1)      | null                           |            |      |
| **Repairs**                                  | VARCHAR(255) | null                           |            |      |
| **Dry Dock**                                 | VARCHAR(255) | null                           |            |      |
| **Railway**                                  | VARCHAR(255) | null                           |            |      |
| **Latitude**                                 | DECIMAL      | null                           |            |      |
| **Longitude**                                | DECIMAL      | null                           |            |      |
| **source name**                              | VARCHAR(255) | null                           |            |      |
| **ingested at**                              | TIMESTAMP    | null                           |            |      |
| **loaded_to_silver**                         | TIMESTAMP    | null                           |            |      | 


### Silver_Vessels

| Name                         | Type         | Settings        | References | Note |
| ---------------------------- | ------------ | --------------- | ---------- | ---- |
| **name**                     | VARCHAR(255) | 🔑 PK, not null |            |      |
| **type**                     | VARCHAR(255) | null            |            |      |
| **year_built**               | INTEGER      | null            |            |      |
| **gross_tonnage**            | INTEGER      | null            |            |      |
| **dead_weight**              | INTEGER      | null            |            |      |
| **length(m)**                | INTEGER      | null            |            |      |
| **beam(m)**                  | INTEGER      | null            |            |      |
| **detail_link**              | VARCHAR(255) | null            |            |      |
| **departure_date**           | TIMESTAMP    | null            |            |      |
| **last_port_country**        | VARCHAR(255) | null            |            |      |
| **last__port_name**          | VARCHAR(255) | null            |            |      |
| **arrival_date**             | TIMESTAMP    | null            |            |      |
| **destination_port_country** | VARCHAR(255) | null            |            |      |
| **destination_port_name**    | VARCHAR(255) | null            |            |      |
| **destination_port_lat**     | DECIMAL      | null            |            |      |
| **destination_port_lon**     | DECIMAL      | null            |            |      |
| **reported_status**          | VARCHAR(255) | null            |            |      |
| **report_date**              | TIMESTAMP    | null            |            |      |
| **source_name**              | VARCHAR(255) | null            |            |      |
| **ingested_at**              | TIMESTAMP    | null            |            |      |
| **ingested_to_silver**       | TIMESTAMP    | null            |            |      | 


### Silver_Seismic

| Name                 | Type         | Settings        | References | Note |
| -------------------- | ------------ | --------------- | ---------- | ---- |
| **unid**             | VARCHAR(255) | 🔑 PK, not null |            |      |
| **source_id**        | INTEGER      | null            |            |      |
| **flynn_region**     | VARCHAR(255) | null            |            |      |
| **latitude**         | DECIMAL      | not null        |            |      |
| **longitude**        | DECIMAL      | not null        |            |      |
| **depth**            | DECIMAL      | not null        |            |      |
| **magnitude**        | DECIMAL      | not null        |            |      |
| **action**           | VARCHAR(255) | null            |            |      |
| **generated_at**     | TIMESTAMP    | not null        |            |      |
| **source_name**      | VARCHAR(255) | not null        |            |      |
| **ingested_at**      | TIMESTAMP    | not null        |            |      |
| **loaded_to_silver** | TIMESTAMP    | not null        |            |      | 


### Dim_Date

| Name              | Type         | Settings                       | References                                                                                           | Note |
| ----------------- | ------------ | ------------------------------ | ---------------------------------------------------------------------------------------------------- | ---- |
| **date_key**      | INTEGER      | 🔑 PK, not null, autoincrement | fk_Dim_Date_date_key_Gold_Seismic, fk_Dim_Date_date_key_Dim_Ports, fk_Dim_Date_date_key_Gold_Vessels |      |
| **full_date**     | DATE         | null                           |                                                                                                      |      |
| **day_num_month** | TINYINT      | null                           |                                                                                                      |      |
| **day_name**      | VARCHAR(255) | null                           |                                                                                                      |      |
| **day_num_week**  | TINYINT      | null                           |                                                                                                      |      |
| **day_of_week**   | VARCHAR(255) | null                           |                                                                                                      |      |
| **day_num_year**  | TINYINT      | null                           |                                                                                                      |      |
| **month_num**     | TINYINT      | null                           |                                                                                                      |      |
| **month_name**    | VARCHAR(255) | null                           |                                                                                                      |      |
| **month_short**   | VARCHAR(255) | null                           |                                                                                                      |      | 


### Dim_Time

| Name          | Type    | Settings                       | References                                                                                           | Note |
| ------------- | ------- | ------------------------------ | ---------------------------------------------------------------------------------------------------- | ---- |
| **time_key**  | INTEGER | 🔑 PK, not null, autoincrement | fk_Dim_Time_time_key_Gold_Seismic, fk_Dim_Time_time_key_Dim_Ports, fk_Dim_Time_time_key_Gold_Vessels |      |
| **full_time** | TIME    | null                           |                                                                                                      |      |
| **hour**      | TINYINT | null                           |                                                                                                      |      |
| **minute**    | TINYINT | null                           |                                                                                                      |      |
| **second**    | TINYINT | null                           |                                                                                                      |      | 


### Dim_Ports

| Name                                 | Type         | Settings                       | References | Note |
| ------------------------------------ | ------------ | ------------------------------ | ---------- | ---- |
| **OID_**                             | INTEGER      | 🔑 PK, not null, autoincrement |            |      |
| **wpi_number**                       | INTEGER      | not null, unique               |            |      |
| **region_name**                      | VARCHAR(255) | null                           |            |      |
| **port_name**                        | VARCHAR(255) | not null                       |            |      |
| **alt_port_name**                    | VARCHAR(255) | null                           |            |      |
| **un_locode**                        | VARCHAR(255) | null                           |            |      |
| **country_code**                     | VARCHAR(255) | not null                       |            |      |
| **water_body**                       | VARCHAR(255) | not null                       |            |      |
| **sailing_direction**                | VARCHAR(255) | not null                       |            |      |
| **tidal_range_m**                    | DECIMAL      | null                           |            |      |
| **entrance_width_m**                 | DECIMAL      | null                           |            |      |
| **channel_depth_m**                  | DECIMAL      | null                           |            |      |
| **anchorage_depth_m**                | DECIMAL      | null                           |            |      |
| **cargo_pier_depth_m**               | DECIMAL      | null                           |            |      |
| **oil_terminal_depth_m**             | DECIMAL      | not null                       |            |      |
| **lpg_terminal_depth_m**             | DECIMAL      | null                           |            |      |
| **max_vessel_length_m**              | DECIMAL      | null                           |            |      |
| **max_vessel_beam_m**                | DECIMAL      | null                           |            |      |
| **max_vessel_draft_m**               | DECIMAL      | null                           |            |      |
| **offshore_max_vessel_length_m**     | DECIMAL      | null                           |            |      |
| **offshore_max_vessel_beam_m**       | DECIMAL      | null                           |            |      |
| **offshore_max_vessel_draft_m**      | DECIMAL      | null                           |            |      |
| **harbor_size**                      | VARCHAR(255) | null                           |            |      |
| **harbor_type**                      | VARCHAR(255) | null                           |            |      |
| **harbor_use**                       | VARCHAR(255) | null                           |            |      |
| **has_shelter**                      | VARCHAR(255) | null                           |            |      |
| **has_communication_telephone**      | CHAR(1)      | null                           |            |      |
| **has_communication_telefax**        | CHAR(1)      | null                           |            |      |
| **has_communication_radio**          | CHAR(1)      | null                           |            |      |
| **has_communication_radiotelephone** | CHAR(1)      | null                           |            |      |
| **has_communication_airport**        | CHAR(1)      | null                           |            |      |
| **has_communication_rail**           | CHAR(1)      | null                           |            |      |
| **communications_index**             | TINYINT      | null                           |            |      |
| **communications_index_category**    | VARCHAR(255) | null                           |            |      |
| **has_medical_facilities**           | CHAR(1)      | null                           |            |      |
| **has_supplies_provisions**          | CHAR(1)      | null                           |            |      |
| **has_supplies_potable_water**       | CHAR(1)      | null                           |            |      |
| **has_supplies_fuel_oil**            | CHAR(1)      | null                           |            |      |
| **has_supplies_diesel_oil**          | CHAR(1)      | null                           |            |      |
| **has_supplies_aviation_fuel**       | CHAR(1)      | null                           |            |      |
| **has_supplies_deck**                | CHAR(1)      | null                           |            |      |
| **has_supplies_engine**              | CHAR(1)      | null                           |            |      |
| **repairs**                          | VARCHAR(255) | null                           |            |      |
| **has_repairts**                     | CHAR(1)      | null                           |            |      |
| **supplies_index**                   | TINYINT      | null                           |            |      |
| **supplies_index_category**          | VARCHAR(255) | null                           |            |      |
| **dry_dock**                         | VARCHAR(255) | null                           |            |      |
| **railway**                          | VARCHAR(255) | null                           |            |      |
| **latitude**                         | DECIMAL      | null                           |            |      |
| **longitude**                        | DECIMAL      | null                           |            |      |
| **source_name**                      | VARCHAR(255) | null                           |            |      |
| **ingested_at**                      | TIMESTAMP    | null                           |            |      |
| **loaded_to_silver**                 | TIMESTAMP    | null                           |            |      |
| **loaded_to_gold**                   | TIMESTAMP    | null                           |            |      |
| **date_key**                         | INTEGER      | null                           |            |      |
| **time_key**                         | INTEGER      | null                           |            |      | 


### Gold_Seismic

| Name                 | Type         | Settings        | References | Note |
| -------------------- | ------------ | --------------- | ---------- | ---- |
| **unid**             | VARCHAR(255) | 🔑 PK, not null |            |      |
| **source_id**        | INTEGER      | null            |            |      |
| **flynn_region**     | VARCHAR(255) | null            |            |      |
| **latitude**         | DECIMAL      | not null        |            |      |
| **longitude**        | DECIMAL      | not null        |            |      |
| **depth**            | DECIMAL      | not null        |            |      |
| **magnitude**        | DECIMAL      | not null        |            |      |
| **action**           | VARCHAR(255) | null            |            |      |
| **generated_at**     | TIMESTAMP    | not null        |            |      |
| **source_name**      | VARCHAR(255) | not null        |            |      |
| **ingested_at**      | TIMESTAMP    | not null        |            |      |
| **loaded_to_silver** | TIMESTAMP    | not null        |            |      |
| **loaded_to_gold**   | TIMESTAMP    | not null        |            |      |
| **date_key**         | INTEGER      | not null        |            |      |
| **time_key**         | INTEGER      | not null        |            |      | 


### Gold_Vessels

| Name                         | Type         | Settings        | References | Note |
| ---------------------------- | ------------ | --------------- | ---------- | ---- |
| **name**                     | VARCHAR(255) | 🔑 PK, not null |            |      |
| **type**                     | VARCHAR(255) | null            |            |      |
| **year_built**               | INTEGER      | null            |            |      |
| **gross_tonnage**            | INTEGER      | null            |            |      |
| **dead_weight**              | INTEGER      | null            |            |      |
| **length(m)**                | INTEGER      | null            |            |      |
| **beam(m)**                  | INTEGER      | null            |            |      |
| **detail_link**              | VARCHAR(255) | null            |            |      |
| **departure_date**           | TIMESTAMP    | null            |            |      |
| **last_port_country**        | VARCHAR(255) | null            |            |      |
| **last__port_name**          | VARCHAR(255) | null            |            |      |
| **arrival_date**             | TIMESTAMP    | null            |            |      |
| **destination_port_country** | VARCHAR(255) | null            |            |      |
| **destination_port_name**    | VARCHAR(255) | null            |            |      |
| **destination_port_lat**     | DECIMAL      | null            |            |      |
| **destination_port_lon**     | DECIMAL      | null            |            |      |
| **reported_status**          | VARCHAR(255) | null            |            |      |
| **report_date**              | TIMESTAMP    | null            |            |      |
| **source_name**              | VARCHAR(255) | null            |            |      |
| **ingested_at**              | TIMESTAMP    | null            |            |      |
| **ingested_to_silver**       | TIMESTAMP    | null            |            |      |
| **ingested_to_gold**         | TIMESTAMP    | null            |            |      |
| **data_time**                | INTEGER      | null            |            |      |
| **data_date**                | INTEGER      | null            |            |      | 


## Relationships

- **Dim_Date to Gold_Seismic**: one_to_many
- **Dim_Time to Gold_Seismic**: one_to_many
- **Dim_Date to Dim_Ports**: one_to_many
- **Dim_Time to Dim_Ports**: one_to_many
- **Dim_Time to Gold_Vessels**: one_to_many
- **Dim_Date to Gold_Vessels**: one_to_many

## Database Diagram

```mermaid
erDiagram
	Dim_Date ||--o{ Gold_Seismic : references
	Dim_Time ||--o{ Gold_Seismic : references
	Dim_Date ||--o{ Dim_Ports : references
	Dim_Time ||--o{ Dim_Ports : references
	Dim_Time ||--o{ Gold_Vessels : references
	Dim_Date ||--o{ Gold_Vessels : references

	Bronze_Ports {
		INTEGER OID_
		INTEGER World Port Index Number
		VARCHAR(255) Region Name
		VARCHAR(255) Main Port Name
		VARCHAR(255) Alternate Port Name
		VARCHAR(255) UN/LOCODE
		VARCHAR(255) Country Code
		VARCHAR(255) World Water Body
		VARCHAR(255) IHO S-130 Sea Area
		VARCHAR(255) Sailing Direction or Publication
		VARCHAR(255) Publication Link
		VARCHAR(255) Standard Nautical Chart
		VARCHAR(255) IHO S-57 Electronic Navigational Chart
		VARCHAR(255) IHO S-101 Electronic Navigational Chart
		VARCHAR(255) Digital Nautical Chart
		DECIMAL Tidal Range (m)
		DECIMAL Entrance Width (m)
		DECIMAL Channel Depth (m)
		DECIMAL Anchorage Depth (m)
		DECIMAL Cargo Pier Depth (m)
		DECIMAL Oil Terminal Depth (m)
		DECIMAL Liquified Natural Gas Terminal Depth (m)
		DECIMAL Maximum Vessel Length (m)
		DECIMAL Maximum Vessel Beam (m)
		DECIMAL Maximum Vessel Draft (m)
		DECIMAL Offshore Maximum Vessel Length (m)
		DECIMAL Offshore Maximum Vessel Beam (m)
		DECIMAL Offshore Maximum Vessel Draft (m)
		VARCHAR(255) Harbor Size
		VARCHAR(255) Harbor Type
		VARCHAR(255) Harbor Use
		VARCHAR(255) Shelter Afforded
		VARCHAR(255) Entrance Restriction - Tide
		VARCHAR(255) Entrance Restriction - Heavy Swell
		VARCHAR(255) Entrance Restriction - Ice
		VARCHAR(255) Entrance Restriction - Other
		VARCHAR(255) Overhead Limits
		VARCHAR(255) Underkeel Clearance Management System
		VARCHAR(255) Good Holding Ground
		VARCHAR(255) Turning Area
		VARCHAR(255) Port Security
		VARCHAR(255) Estimated Time of Arrival Message
		VARCHAR(255) Quarantine - Pratique
		VARCHAR(255) Quarantine - Sanitation
		VARCHAR(255) Quarantine - Other
		VARCHAR(255) Traffic Separation Scheme
		VARCHAR(255) Vessel Traffic Service
		VARCHAR(255) First Port of Entry
		VARCHAR(255) US Representative
		VARCHAR(255) Pilotage - Compulsory
		VARCHAR(255) Pilotage - Available
		VARCHAR(255) Pilotage - Local Assistance
		VARCHAR(255) Pilotage - Advisable
		VARCHAR(255) Tugs - Salvage
		VARCHAR(255) Tugs - Assistance
		VARCHAR(255) Communications - Telephone
		VARCHAR(255) Communications - Telefax
		VARCHAR(255) Communications - Radio
		VARCHAR(255) Communications - Radiotelephone
		VARCHAR(255) Communications - Airport
		VARCHAR(255) Communications - Rail
		VARCHAR(255) Search and Rescue
		VARCHAR(255) NAVAREA
		VARCHAR(255) Facilities - Wharves
		VARCHAR(255) Facilities - Anchorage
		VARCHAR(255) Facilities - Dangerous Cargo Anchorage
		VARCHAR(255) Facilities - Med Mooring
		VARCHAR(255) Facilities - Beach Mooring
		VARCHAR(255) Facilities - Ice Mooring
		VARCHAR(255) Facilities - Ro-Ro
		VARCHAR(255) Facilities - Solid Bulk
		VARCHAR(255) Facilities - Liquid Bulk
		VARCHAR(255) Facilities - Container
		VARCHAR(255) Facilities - Breakbulk
		VARCHAR(255) Facilities - Oil Terminal
		VARCHAR(255) Facilities - LNG Terminal
		VARCHAR(255) Facilities - Other
		VARCHAR(255) Medical Facilities
		VARCHAR(255) Garbage Disposal
		VARCHAR(255) Chemical Holding Tank Disposal
		VARCHAR(255) Degaussing
		VARCHAR(255) Dirty Ballast Disposal
		VARCHAR(255) Cranes - Fixed
		VARCHAR(255) Cranes - Mobile
		VARCHAR(255) Cranes - Floating
		VARCHAR(255) Cranes Container
		VARCHAR(255) Lifts - 100+ Tons
		VARCHAR(255) Lifts - 50-100 Tons
		VARCHAR(255) Lifts - 25-49 Tons
		VARCHAR(255) Lifts - 0-24 Tons
		VARCHAR(255) Services - Longshoremen
		VARCHAR(255) Services - Electricity
		VARCHAR(255) Services -Steam
		VARCHAR(255) Services - Navigation Equipment
		VARCHAR(255) Services - Electrical Repair
		VARCHAR(255) Services - Ice Breaking
		VARCHAR(255) Services -Diving
		VARCHAR(255) Supplies - Provisions
		VARCHAR(255) Supplies - Potable Water
		VARCHAR(255) Supplies - Fuel Oil
		VARCHAR(255) Supplies - Diesel Oil
		VARCHAR(255) Supplies - Aviation Fuel
		VARCHAR(255) Supplies - Deck
		VARCHAR(255) Supplies - Engine
		VARCHAR(255) Repairs
		VARCHAR(255) Dry Dock
		VARCHAR(255) Railway
		DECIMAL Latitude
		DECIMAL Longitude
		VARCHAR(255) source name
		TIMESTAMP Ingested at
	}

	Silver_Ports {
		INTEGER OID_
		INTEGER World Port Index Number
		VARCHAR(255) Region Name
		VARCHAR(255) Main Port Name
		VARCHAR(255) Alternate Port Name
		VARCHAR(255) UN/LOCODE
		VARCHAR(255) Country Code
		VARCHAR(255) World Water Body
		VARCHAR(255) Sailing Direction or Publication
		DECIMAL Tidal Range (m)
		DECIMAL Entrance Width (m)
		DECIMAL Channel Depth (m)
		DECIMAL Anchorage Depth (m)
		DECIMAL Cargo Pier Depth (m)
		DECIMAL Oil Terminal Depth (m)
		DECIMAL Liquified Natural Gas Terminal Depth (m)
		DECIMAL Maximum Vessel Length (m)
		DECIMAL Maximum Vessel Beam (m)
		DECIMAL Maximum Vessel Draft (m)
		DECIMAL Offshore Maximum Vessel Length (m)
		DECIMAL Offshore Maximum Vessel Beam (m)
		DECIMAL Offshore Maximum Vessel Draft (m)
		VARCHAR(255) Harbor Size
		VARCHAR(255) Harbor Type
		VARCHAR(255) Harbor Use
		VARCHAR(255) Shelter Afforded
		CHAR(1) Entrance Restriction - Tide
		CHAR(1) Entrance Restriction - Heavy Swell
		CHAR(1) Entrance Restriction - Ice
		CHAR(1) Entrance Restriction - Other
		CHAR(1) Communications - Telephone
		CHAR(1) Communications - Telefax
		CHAR(1) Communications - Radio
		CHAR(1) Communications - Radiotelephone
		CHAR(1) Communications - Airport
		CHAR(1) Communications - Rail
		CHAR(1) Medical Facilities
		CHAR(1) Supplies - Provisions
		CHAR(1) Supplies - Potable Water
		CHAR(1) Supplies - Fuel Oil
		CHAR(1) Supplies - Diesel Oil
		CHAR(1) Supplies - Aviation Fuel
		CHAR(1) Supplies - Deck
		CHAR(1) Supplies - Engine
		VARCHAR(255) Repairs
		VARCHAR(255) Dry Dock
		VARCHAR(255) Railway
		DECIMAL Latitude
		DECIMAL Longitude
		VARCHAR(255) source name
		TIMESTAMP ingested at
		TIMESTAMP loaded_to_silver
	}

	Bronze_Seismic {
		VARCHAR(255) unid
		INTEGER source_id
		VARCHAR(255) flynn_region
		DECIMAL lat
		DECIMAL lon
		DECIMAL depth
		DECIMAL mag
		VARCHAR(255) action
		TIMESTAMP generated_at
		VARCHAR(255) source_name
		TIMESTAMP ingested_at
	}

	Silver_Seismic {
		VARCHAR(255) unid
		INTEGER source_id
		VARCHAR(255) flynn_region
		DECIMAL latitude
		DECIMAL longitude
		DECIMAL depth
		DECIMAL magnitude
		VARCHAR(255) action
		TIMESTAMP generated_at
		VARCHAR(255) source_name
		TIMESTAMP ingested_at
		TIMESTAMP loaded_to_silver
	}

	Gold_Seismic {
		VARCHAR(255) unid
		INTEGER source_id
		VARCHAR(255) flynn_region
		DECIMAL latitude
		DECIMAL longitude
		DECIMAL depth
		DECIMAL magnitude
		VARCHAR(255) action
		TIMESTAMP generated_at
		VARCHAR(255) source_name
		TIMESTAMP ingested_at
		TIMESTAMP loaded_to_silver
		TIMESTAMP loaded_to_gold
		INTEGER date_key
		INTEGER time_key
	}

	Dim_Date {
		INTEGER date_key
		DATE full_date
		TINYINT day_num_month
		VARCHAR(255) day_name
		TINYINT day_num_week
		VARCHAR(255) day_of_week
		TINYINT day_num_year
		TINYINT month_num
		VARCHAR(255) month_name
		VARCHAR(255) month_short
	}

	Dim_Time {
		INTEGER time_key
		TIME full_time
		TINYINT hour
		TINYINT minute
		TINYINT second
	}

	Dim_Ports {
		INTEGER OID_
		INTEGER wpi_number
		VARCHAR(255) region_name
		VARCHAR(255) port_name
		VARCHAR(255) alt_port_name
		VARCHAR(255) un_locode
		VARCHAR(255) country_code
		VARCHAR(255) water_body
		VARCHAR(255) sailing_direction
		DECIMAL tidal_range_m
		DECIMAL entrance_width_m
		DECIMAL channel_depth_m
		DECIMAL anchorage_depth_m
		DECIMAL cargo_pier_depth_m
		DECIMAL oil_terminal_depth_m
		DECIMAL lpg_terminal_depth_m
		DECIMAL max_vessel_length_m
		DECIMAL max_vessel_beam_m
		DECIMAL max_vessel_draft_m
		DECIMAL offshore_max_vessel_length_m
		DECIMAL offshore_max_vessel_beam_m
		DECIMAL offshore_max_vessel_draft_m
		VARCHAR(255) harbor_size
		VARCHAR(255) harbor_type
		VARCHAR(255) harbor_use
		VARCHAR(255) has_shelter
		CHAR(1) has_communication_telephone
		CHAR(1) has_communication_telefax
		CHAR(1) has_communication_radio
		CHAR(1) has_communication_radiotelephone
		CHAR(1) has_communication_airport
		CHAR(1) has_communication_rail
		TINYINT communications_index
		VARCHAR(255) communications_index_category
		CHAR(1) has_medical_facilities
		CHAR(1) has_supplies_provisions
		CHAR(1) has_supplies_potable_water
		CHAR(1) has_supplies_fuel_oil
		CHAR(1) has_supplies_diesel_oil
		CHAR(1) has_supplies_aviation_fuel
		CHAR(1) has_supplies_deck
		CHAR(1) has_supplies_engine
		VARCHAR(255) repairs
		CHAR(1) has_repairts
		TINYINT supplies_index
		VARCHAR(255) supplies_index_category
		VARCHAR(255) dry_dock
		VARCHAR(255) railway
		DECIMAL latitude
		DECIMAL longitude
		VARCHAR(255) source_name
		TIMESTAMP ingested_at
		TIMESTAMP loaded_to_silver
		TIMESTAMP loaded_to_gold
		INTEGER date_key
		INTEGER time_key
	}

	Bronze_Vessels {
		VARCHAR(255) name
		VARCHAR(255) type
		VARCHAR(255) year_built
		VARCHAR(255) gross_tonnage
		VARCHAR(255) dead_weight
		VARCHAR(255) length(m)
		VARCHAR(255) beam(m)
		VARCHAR(255) detail_link
		TIMESTAMP departure_date
		VARCHAR(255) last_port_country
		VARCHAR(255) last__port_name
		TIMESTAMP arrival_date
		VARCHAR(255) destination_port_country
		VARCHAR(255) destination_port_name
		DECIMAL destination_port_lat
		DECIMAL destination_port_lon
		VARCHAR(255) reported_status
		TIMESTAMP report_date
		VARCHAR(255) source_name
		TIMESTAMP ingested_at
	}

	Silver_Vessels {
		VARCHAR(255) name
		VARCHAR(255) type
		INTEGER year_built
		INTEGER gross_tonnage
		INTEGER dead_weight
		INTEGER length(m)
		INTEGER beam(m)
		VARCHAR(255) detail_link
		TIMESTAMP departure_date
		VARCHAR(255) last_port_country
		VARCHAR(255) last__port_name
		TIMESTAMP arrival_date
		VARCHAR(255) destination_port_country
		VARCHAR(255) destination_port_name
		DECIMAL destination_port_lat
		DECIMAL destination_port_lon
		VARCHAR(255) reported_status
		TIMESTAMP report_date
		VARCHAR(255) source_name
		TIMESTAMP ingested_at
		TIMESTAMP ingested_to_silver
	}

	Gold_Vessels {
		VARCHAR(255) name
		VARCHAR(255) type
		INTEGER year_built
		INTEGER gross_tonnage
		INTEGER dead_weight
		INTEGER length(m)
		INTEGER beam(m)
		VARCHAR(255) detail_link
		TIMESTAMP departure_date
		VARCHAR(255) last_port_country
		VARCHAR(255) last__port_name
		TIMESTAMP arrival_date
		VARCHAR(255) destination_port_country
		VARCHAR(255) destination_port_name
		DECIMAL destination_port_lat
		DECIMAL destination_port_lon
		VARCHAR(255) reported_status
		TIMESTAMP report_date
		VARCHAR(255) source_name
		TIMESTAMP ingested_at
		TIMESTAMP ingested_to_silver
		TIMESTAMP ingested_to_gold
		INTEGER data_time
		INTEGER data_date
	}
```