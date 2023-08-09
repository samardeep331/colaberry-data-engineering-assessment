# import dependencies
import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Connection String for PostgreSQL
conn_string = "host={} dbname={} user={} password={}".format(os.getenv("HOST"), os.getenv("DBNAME"), os.getenv("USER"), os.getenv("PASSWORD"))

def extract_weather_statistics(conn_str):
    '''
    Returns the sum of two decimal numbers in binary digits.

            Parameters:
                    conn_str (string): Connection String to establish a connection to PostgreSQL
    '''

    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()

    # DDL statement to create the weather stats table which will store the calculated weather statistics
    create_table_query = """
    CREATE TABLE IF NOT EXISTS weather_statistics (
        station TEXT NOT NULL,
        year INTEGER NOT NULL,
        avg_max_temperature_degC REAL,
        avg_min_temperature_degC REAL,
        total_precipitation_cm REAL, 
        PRIMARY KEY(station, year)
    )
    """
    cursor.execute(create_table_query)
    conn.commit()

    # Extract unique years from weather data
    distinct_years_query = "SELECT DISTINCT(EXTRACT(YEAR FROM date)) FROM weather_data"

    # Extract unique stations from weather data
    distinct_stations_query = "SELECT DISTINCT(station) FROM weather_data"
    cursor.execute(distinct_years_query)
    years = cursor.fetchall()
    cursor.execute(distinct_stations_query)
    stations = cursor.fetchall()

    # Loog through all the stations and years
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

            if total_precip is not None:
                total_precip /= 10
            
            # if the result is none for any statistics, replace it with -99999999
            if avg_max_temp is None:
                avg_max_temp = -99999999
            if avg_min_temp is None:
                avg_min_temp = -99999999
            if total_precip is None:
                total_precip = -99999999
        
            # Insert calculated statistics into the weather_statistics table
            try:
                insert_query = """
                INSERT INTO weather_statistics (station, year, avg_max_temperature_degC, avg_min_temperature_degC, total_precipitation_cm)
                VALUES ('{}', {}, NULLIF({}, -99999999), NULLIF({}, -99999999), NULLIF({}, -99999999))
                """.format(station_id, year_id, avg_max_temp, avg_min_temp, total_precip)
                cursor.execute(insert_query)
            except:
                cursor.execute("ROLLBACK")
            conn.commit()
            
    cursor.close()
    conn.close()
    print("Successfully extracted weather stats for all stations and years.")
    
extract_weather_statistics(conn_string)