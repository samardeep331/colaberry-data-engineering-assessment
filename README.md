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
$ git clone git@github.com:samardeep331/colaberry-data-engineering-assessment.git
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
The code to create the two API endpoints is located in the ```app.py``` file inside the scripts folder. Assuming, the database is populated with the ```weather_data``` and ```weather_stats``` tables, and the ```requirements.txt``` file is installed, the steps to run the API locally from the root directory are as follows:

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

The unit tests for the API are located inside the ```test_api.py``` file in the tests folder. The unit tests can be run after setting up the database and installing requirements with the following steps:

```bash
cd tests
pytest
```
### Problem 5 - Deployment
To deploy the API on AWS, I would follow the following steps:

**1. Setting up PostgreSQL database and configuring environment variables:** Set up PostgreSQL database using Amazon RDS or Amazon Aurora and configure environment variables for the containerized API and Lambda function, allowing them to connect to the PostgreSQL database.

**2. Scheduled ingestion script using AWS Lambda:** Create an AWS Lambda function that executes the ```ingestion.py``` script to populate the database. A Lambda function can be used to run the script at specific intervals using Amazon CloudWatch Events.

**3. Containerize API code:** Create a Dockerfile that defines the environment and dependencies required for the API. Build a Docker image containing the API code, and push it to a container registry like Amazon Elastic Container Registry (ECR).

**4. Create ECS cluster and deploy API using ECS:** Create an ECS cluster where the container will run. Define a task definition that uses the Docker image from ECR and specifies how many containers to run. Then, create a service using this task definition to ensure that the API containers are always running.
