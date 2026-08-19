# Draw_DB Link:
- Static
https://www.drawdb.app/share/EcxUqhmlu3ZiqKceVulZS278
- Live (editable)
https://www.drawdb.app/editor/diagrams/8971b1f7-84a3-4414-a42d-c60277a4f332

# **Bronze Layer**

## Ports
The ports table is the same as the source with an addition of 2 columns
1. ingested at timestamp
2. source name

## Seismic Events
The Seismic table is the same as the source with an addition of 2 columns
1. generated at timestamp
2. source name
3. ingested at timestamp


## Vessels
TBD

# **Silver Layer**

## Ports
1. Enforce data types
2. Drop the unused columns (refer to the svg) 

IHO S-130 Sea Area
/ Publication Link
/ Standard Nautical Chart
/ IHO S-57 Electronic Navigational Chart
/ IHO S-101 Electronic Navigational Chart
/ Digital Nautical Chart
/ Overhead Limits
/ Underkeel Clearance Management System
/ Good Holding Ground
/ Turning Area
/ Port Security
/ Estimated Time of Arrival Message
/ Quarantine - Pratique
/ Quarantine - Sanitation
/ Quarantine - Other
/ Traffic Separation Scheme
/ Vessel Traffic Service
/ First Port of Entry
/ US Representative
/ Pilotage - Compulsory
/ Pilotage - Available
/ Pilotage - Local Assistance
/ Pilotage - Advisable
/ Tugs - Salvage
/ Tugs - Assistance
/ Search and Rescue
/ NAVAREA
/ Facilities - Wharves
/ Facilities - Anchorage
/ Facilities - Dangerous Cargo Anchorage
/ Facilities - Med Mooring
/ Facilities - Beach Mooring
/ Facilities - Ice Mooring
/ Facilities - Ro-Ro
/ Facilities - Solid Bulk
/ Facilities - Liquid Bulk
/ Facilities - Container
/ Facilities - Breakbulk
/ Facilities - Oil Terminal
/ Facilities - LNG Terminal
/ Facilities - Other
/ Garbage Disposal
/ Chemical Holding Tank Disposal
/ Degaussing
/ Dirty Ballast Disposal
/ Cranes - Fixed
/ Cranes - Mobile
/ Cranes - Floating
/ Cranes Container
/ Lifts - 100+ Tons
/ Lifts - 50-100 Tons
/ Lifts - 25-49 Tons
/ Lifts - 0-24 Tons
/ Services - Longshoremen	
/ Services - Electricity	
/ Services -Steam	
/ Services - Navigation Equipment	
/ Services - Electrical Repair	
/ Services - Ice Breaking	
/ Services -Diving.

3. Drop duplicates

4. modify the flags
for these columns trim and use the first value only i.e. 'Yes' should be 'Y', no should be 'N' and unknown should be 'U'.  
Entrance restriction columns 
/ Communication columns
/ Medical facilities
/ Supplies columns

5. categorical columns to be left as as they are:  
harbor size
/ harbor type 
/ harbor use
/ shelter afforded
/ repairs
/ dry dock
/ railway

6. Add columns   
loaded_to_silver: timestamp

## Seismic Events
1. enforce data types
2. rename columns for clarity

lat -> latitute  
lon -> longitude   
mag -> magnitude   

3. add columns  
loaded_to_silver: timestamp

## Vessels
TBD


# **Gold Layer**

## Date
create date dimension to use with the following columns:
1. date_key:      int
2. full_date:     date
3. day_num_month: int
4. day_name:      varchar
5. day_num_week:  int
6. day_of_week:   varchar
7. day_num_year:  int
8. month_num:     int
9. month_name:    varchar
10. month_short:  char(3)


## Time
create time dimension to use with the following columns:
1. time_key:  int
2. full_time: time
3. hour:      int
4. minute:    int
5. second:    int

## Ports

### dim: dim_Ports
The ports are a dimension  
1. rename columns  
wpi_number: world port index number  
region_name: region name  
port_name: main port name  
alt_port_name: alternate port name  
etc.

2. drop restriction columns (not needed in analysis)  

3. transform the flag columns (Y, N, U) to (1,0) where 1=yes and 0=(no or unknown)
has_communication_telephone  
has_communication_telefax  
has_communication_radio  
has_communication_radiotelephone  
has_communication_airport  
has_communication_rail
has_medical_facilities  
has_supplies_provisions  
has_supplies_potable_water  
has_supplies_fuel_oil  
has_supplies_diesel_oil  
has_supplies_aviation_fuel  
has_supplies_deck  
has_supplies_engine  

4. create has_repairs column which is 0 if the repair category is (null, empty, or unknown)

5. create ranking for for (communications / supplies + repairs)  
communications_index:           int:     this is the sum of these flags only (radio, telephone, airport, telefax)  
communications_index_category:  varchar: 4 is excellent, >=2 is good, 1 is limited, 0 is unavailable  
supplies_index:                 int:     this is the sum of these flags only (provisions, fuel oil, diesel, potable water, has_repairs)  
supplies_index_category:        varchar: 5 is excellent, >=3 is good, 1>=1 is limited, 0 is unavailable  


## Seismic Events
1. add column loaded_to_gold: timestamp
2. Add date column with datekey: integer
3. add time column with time key: integer

## Vessels
TBD


# **Semantic Layer** 

This layer will be constructed in PowerBI because we have 2 separate sources for the data.  
The layer will be implemented using measures, parameters, PowerQuery and DAX.  
For this demonstration we are using SQL.  

The layer will haave the following properties:
1. a fact_ports_seismic_events table
the table cross-joins the ports and earthquakes and calculates the **haversine distance** between the ports and earthquakes and then filters using parameters.

2. the risk categorization of ports  
The risk score is for each earthquake calculate 10^(magnitude) / distance^(2) 
the 10^magnitude is because rechtar is an exponential scale. 
The distance is squared because the destructive power has high decay rate.  
The data is then dynamically partitioned into 3 categories (ntiles)


```SQL
WITH fact_ports_earthquakes_distance AS (
    SELECT
        p.port_id,
        e.earthquake_id,
        e.mag,
        e.depth,
        -- Haversine distance in km
        6371 * 2 * ASIN(
            SQRT(
                POWER(
                    SIN(
                        RADIANS(e.lat - p.lat) / 2
                    ), 2
                )
                +
                COS(RADIANS(p.lat))
                * COS(RADIANS(e.lat))
                * POWER(
                    SIN(
                        RADIANS(e.lon - p.lon) / 2
                    ), 2
                )
            )
        ) AS distance_km
    FROM ports p
    CROSS JOIN earthquakes e
),

ports_risk_scores AS (
    SELECT
        port_id,
        SUM(
            POWER(10, mag)
            / POWER(distance_km + 1, 2)
        ) AS risk_score
    FROM distances
    WHERE distance_km <= 50
    GROUP BY port_id
),

ports_ranked AS (
    SELECT
        port_id,
        risk_score,
        NTILE(3) OVER (
            ORDER BY risk_score
        ) AS risk_group
    FROM port_scores
)

SELECT
    port_id,
    risk_score,
    CASE risk_group
        WHEN 1 THEN 'Low'
        WHEN 2 THEN 'Medium'
        WHEN 3 THEN 'High'
    END AS risk_category
FROM ranked_ports
ORDER BY risk_score;
```

