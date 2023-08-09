# colaberry-data-engineering-assessment
This is a Git repository to store the solutions and files for the Data Engineering Consultant assessment for Colaberry Inc. 

### Problem 1 - Data Modeling
I will use PostgreSQL database to design a table to hold weather data. The SQL DDL command use to create the table named 'weather_data' is as follows:

```sql
CREATE TABLE IF NOT EXISTS weather_data (
        station VARCHAR NOT NULL,
        date DATE NOT NULL,
        max_temperature INTEGER,
        min_temperature INTEGER,
        precipitation INTEGER,
        PRIMARY KEY(station, date)
    )
```
The table's primary key consists of two columns station and date. Also, there are columns for max_temperature, min_temperature and precipitation.

### Problem 2 - Ingestion
The script for data ingestion is located in the scripts directory. To run the script, use the following commands:

```bash
$ git clone repo
$ pip install -r requirements.txt
$ cd scripts
$ python ingestion.py
```

**Note:** A PostgreSQL database should be set up first to run the ingestion.py script as the script requires connection to the database where the weather_data table would be stored. After setting up the database, modify the ``` conn_str ``` variable in line 12 of the ingestion.py script to provide the script with credentials of the database.


### Problem 3 - Data Analysis

The model definiton as well as the full code used to calculate weather statistics is located in ``` extract_stats.py ``` in the scripts folder. The DDL statement for storing the newly calculated fields is as follows: 

```sql
CREATE TABLE IF NOT EXISTS weather_statistics (
        station TEXT NOT NULL,
        year INTEGER NOT NULL,
        avg_max_temperature_degC REAL,
        avg_min_temperature_degC REAL,
        total_precipitation_cm REAL, 
        PRIMARY KEY(station, year)
    )
```
The station and year(extracted from date) are used as a primary key for the table 'weather_statistics'. The code used to calculate the new variables can be found in the ```extract_stats.py``` file inside the scripts directory. A snapshot of the code is available below:

```
for station in stations:
        station_id = station[0]
        for year in years:
            year_id = year[0]

            # query to calculated average max_temperature excluding missing values
            avg_max_temp_query = """
            SELECT AVG(max_temperature) FROM weather_data
            WHERE EXTRACT(YEAR FROM date) = {} AND station = '{}' AND max_temperature != -9999
            """.format(year_id, station_id)
            cursor.execute(avg_max_temp_query)
            avg_max_temp = cursor.fetchone()[0]
            
            # # query to calculated average min_temperature excluding missing values
            avg_min_temp_query = """
            SELECT AVG(min_temperature) FROM weather_data
            WHERE EXTRACT(YEAR FROM date) = {} AND station = '{}' AND min_temperature != -9999
            """.format(year_id, station_id)
            cursor.execute(avg_min_temp_query)
            avg_min_temp = cursor.fetchone()[0]

            # query to calculate total accumulated precipitation in centimeters excluding missing values
            total_precip_query = """
            SELECT SUM(precipitation) FROM weather_data
            WHERE EXTRACT(YEAR FROM date) = {} AND station = '{}' AND precipitation != -9999
            """.format(year_id, station_id)
            cursor.execute(total_precip_query)
            total_precip = cursor.fetchone()[0]
```

### Problem 4 - REST API
The code to create the two API endpoints is located in the ```app.py``` file inside the scripts folder. Assuming, the database is populated with the ```sql weather_data``` and ```sql weather_stats``` tables, and the ```requirements.txt``` file is installed, the steps to run the API locally from the root directory are as follows:

```bash
$ cd scripts
$ python app.py
```
The two api endpoints along with Swagger docs are as follows:

```
http://127.0.0.1:5000/api/weather
http://127.0.0.1:5000/api/weather/stats
http://127.0.0.1:5000/api/docs
```
The two api endpoints have optional filters of date and station_id that can be passed along with the request to filter out the results. The user can also specify the page number to look at a specific section of the results.
