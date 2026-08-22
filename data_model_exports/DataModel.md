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
The Vessels are fully loaded every day without history tracking.  
The Vessels table is the same as the source with an addition of 2 columns:  
1. source name  
2. ingested at timestamp  


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

4. implement MERGE logic  
a. if the record receives an update within the same day -> update the value  
b. if the record received an update another day -> create new UNID and insert as a new record  
    since the dashboard is viewed daily and we filter by day then we will only view the latest status and preserve history

## Vessels
The vessels require minimal transformation and only minor column are added such as   

1. Enforce data types  
a. Integer:   
year_built / gross_tonnage / dead_weight / length(m) / beam(m) /  
b. Decimal:
destination_port_lat / destination_port_lon / 
c. timestamp  
departure_date / arrival_date / report_date / ingested_at 

2. add columns  
loaded_to_silver: timestamp



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
a. renaming columns:  
length(m) -> length_m  
beam(m) -> beam_m  
b. added columns: 
ingested_timestamp  
ingested_date   


# **Semantic Layer** 

This layer will be constructed in PowerBI because we have 2 separate sources for the data.  
The layer will be implemented using measures, parameters, PowerQuery and DAX.  
For this demonstration we are using SQL.  

The layer will haave the following properties:
1. a fact_ports_seismic_events table
the table cross-joins the ports and earthquakes and calculates the **haversine distance** between the ports and earthquakes and then filters using parameters.

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
```
The actual code in M-Language is:

```SQL
let
    Source = Dim_Port,
    // attach the ENTIRE Dim_Earthquake table as one nested value on every port row
    AddEvents = Table.AddColumn(Source, "EventsNested", each Dim_Earthquake),
    Expanded = Table.ExpandTableColumn(
        AddEvents,
        "EventsNested",
        {"UNID", "LAT", "LON", "MAG", "DEPTH", "GENERATED_AT"},
        {"earthquake_id", "e_lat", "e_lon", "magnitude", "event_depth_km", "event_time"}
    ),
    // Haversine distance, in km
    AddDistance = Table.AddColumn(Expanded, "distance_km", each
        let
            lat1 = [latitude] * Number.PI / 180,
            lat2 = [e_lat] * Number.PI / 180,
            dLat = lat2 - lat1,
            dLon = ([e_lon] - [longitude]) * Number.PI / 180,
            a = Number.Sin(dLat/2) * Number.Sin(dLat/2)
              + Number.Cos(lat1) * Number.Cos(lat2) * Number.Sin(dLon/2) * Number.Sin(dLon/2),
            c = 2 * Number.Asin(Number.Sqrt(a))
        in
            6371 * c,
        type number
    ),
    // keep the table from exploding: cutoff generous enough to cover any threshold you'll expose to the user
    FilterCutoff = Table.SelectRows(AddDistance, each [distance_km] <= 300),
    SelectCols = Table.SelectColumns(FilterCutoff,
        {"port_id", "earthquake_id", "event_time", "magnitude", "event_depth_km", "distance_km"})
in
    SelectCols
```

2. the risk categorization of ports  
The risk score is for each earthquake calculate 10^(magnitude) / ( distance^(2) * SQRT(depth) ) 
the 10^magnitude is because rechtar is an exponential scale. 
The distance is squared because the destructive power has high decay rate.  
The depth is decaying but at a slower rate than the distance -> a wave at level 0 is extremely destructive ! 
The data is then dynamically partitioned into 3 categories (ntiles)

The ports risk score in SQL is:

```SQL
ports_risk_scores AS (
    SELECT
        port_id,
        SUM(
            POWER(10, mag)
            / (POWER(distance_km + 1, 2) * POWER(depth_km + 1, 0.5))
        ) AS risk_score
    FROM distances
    WHERE distance_km <= 300 --This is a fixed number for the ranking
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
The actual code in M-Language is:

a. create a parameter to set the max_distance
```SQL
Max Distance (km) Value = SELECTEDVALUE('Max Distance (km)'[Max Distance (km)], 300)
```
b. create a custom columns risk_score for the dim_port
```SQL
    risk_score =
    COALESCE(
        CALCULATE(
            SUMX(
                fact_ports_events,
                POWER(10, fact_ports_events[magnitude])
                / POWER(fact_ports_events[distance_km] + 1, 2)
                / POWER(fact_ports_events[event_depth_km] + 1, 0.5)
            ),
            fact_ports_events[distance_km] <= 300
        ),
        0
    )
```
c. rank this columns
```SQL
    risk_rank =
    RANKX(ALL(Dim_Port), Dim_Port[risk_score], , ASC, Skip)
```
d. categorize
```SQL
    risk_category =
    VAR TotalPorts = COUNTROWS(ALL(Dim_Port))
    VAR Bucket = ROUNDUP(Dim_Port[risk_rank] * 3 / TotalPorts, 0)
    RETURN
        SWITCH(
            TRUE(),
            Bucket <= 1, "Low",
            Bucket = 2, "Medium",
            "High"
        )
``` 


## Other Tables:
A union of the ports and earthquakes tables is created in order to plot them together on one map, the code in DAX in PowerBI is 
```SQL
    Map_Points =
    UNION(
        SELECTCOLUMNS(
            Dim_Earthquake,
            "lat",           Dim_Earthquake[LAT],
            "lon",           Dim_Earthquake[LON],
            "point_type",    "Earthquake",
            "point_date",    DATE(YEAR(Dim_Earthquake[GENERATED_AT]), MONTH(Dim_Earthquake[GENERATED_AT]), DAY(Dim_Earthquake[GENERATED_AT])),
            "label",
                "Mag " & FORMAT(Dim_Earthquake[MAG], "0.0")
                & " — " & Dim_Earthquake[FLYNN_REGION]
                & UNICHAR(10) & "Depth: " & FORMAT(Dim_Earthquake[DEPTH], "0.0") & " km"
                & UNICHAR(10) & FORMAT(Dim_Earthquake[GENERATED_AT], "mmm dd, yyyy hh:mm AM/PM"),
            "size_value",    Dim_Earthquake[MAG],
            "earthquake_id", Dim_Earthquake[UNID],
            "port_id",       BLANK()
        ),
        SELECTCOLUMNS(
            Dim_Port,
            "lat",           Dim_Port[latitude],
            "lon",           Dim_Port[longitude],
            "point_type",    "Port",
            "point_date",    BLANK(),
            "label",
                "Port ID: " & Dim_Port[port_id]
                & UNICHAR(10) & "Port Name: " & Dim_Port[port_name]
                & UNICHAR(10) & "Country: " & COALESCE(Dim_Port[country_code], "Unknown")
                & UNICHAR(10) & "Harbor size: " & COALESCE(Dim_Port[harbor_size], "Unknown")
                & UNICHAR(10) & "Harbor type: " & COALESCE(Dim_Port[harbor_type], "Unknown")
                & UNICHAR(10) & "Communications Index: " & Dim_Port[communications_index]
                & UNICHAR(10) & "Communications Category: " & Dim_Port[communications_index_category]
                & UNICHAR(10) & "Supplies Index: " & Dim_Port[supplies_index]
                & UNICHAR(10) & "Supplies Category: " & Dim_Port[supplies_index_category],
            "size_value",    4,
            "earthquake_id", BLANK(),
            "port_id",       Dim_Port[port_id]
        )
    )
```
The following measures and parameters were used to filter by the date:  
1. Days ago: a Data date parameter  
2. Days ago: a data date measure  
```SQL
    Days Ago Value = SELECTEDVALUE('Days Ago'[Days Ago], 1)
```
3. Show on map: a measure that uses the parameter to filter out seismic events but keep ports
```SQL
    Show On Map =
    VAR TargetDate = TODAY() - [Days Ago Value]
    RETURN
        IF(
            SELECTEDVALUE(Map_Points[point_type]) = "Port",
            1,
            IF(SELECTEDVALUE(Map_Points[point_date]) = TargetDate, 1, 0)
        )
```
### Applied Measures:
```SQL
    Total Earthquakes Shown =
    CALCULATE(
        COUNTROWS(Dim_Earthquake),
        FILTER(Dim_Earthquake, [Is Selected Day] = 1)
    )
```  
```SQL  
    Average Magnitude =
    CALCULATE(
        AVERAGE(Dim_Earthquake[MAG]),
        FILTER(Dim_Earthquake, [Is Selected Day] = 1)
    )
```
```SQL
    Max Magnitude =
    CALCULATE(
        MAX(Dim_Earthquake[MAG]),
        FILTER(Dim_Earthquake, [Is Selected Day] = 1)
    )
```
```SQL
    Strongest Region =
    VAR MaxMag = [Max Magnitude]
    RETURN
        CALCULATE(
            SELECTEDVALUE(Dim_Earthquake[FLYNN_REGION]),
            FILTER(Dim_Earthquake, [Is Selected Day] = 1),
            Dim_Earthquake[MAG] = MaxMag
    )
````
