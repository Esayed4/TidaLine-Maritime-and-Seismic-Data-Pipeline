# Draw_DB Link:
https://www.drawdb.app/share/EcxUqhmlu3ZiqKceVulZS278

# **Bronze Layer**

## Ports
The ports table is the same as the source with an addition of 2 columns
1. ingested at timestamp
2. source name

## Seismic Events
The Seismic table is the same as the source with an addition of 2 columns
1. generated at timestamp
2. ingested at timestamp
3. source name

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

## Seismic Events
1. enforce data types
2. rename columns for clarity

lat -> Latitute
lon -> Longitude 
mag -> magnitude 


## Vessels
TBD


# **Gold Layer**

## Date
create date dimension to use

## Time
create time dimension to use

## Ports

### Fact: Ports
1. create ranking for for (restriction / communications / supplies + repairs)
2. create keys for (ports_restriction, ports_communication, ports_supplies).  
- the key might be in the form of a bitmap key i.e. 110110 (i'm still thinking about what to do with unknown, should it be status 2?)
### dim: Ports_restriction 
### dim: Ports_communication 
### dim: Ports_supplies 

## Seismic Events
1. Add date column with datekey
2. add time column with time key

## Vessels
TBD

