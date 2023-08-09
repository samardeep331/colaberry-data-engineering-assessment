# import dependencies
import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Getting a list of files to read
file_list = os.listdir(os.path.join('code-challenge-template', 'wx_data'))

# PostgreSQL connection string
conn_string = "host={} dbname={} user={} password={}".format(os.getenv("HOST"), os.getenv("DBNAME"), os.getenv("USER"), os.getenv("PASSWORD"))

def ingest_weather_data(file_lst, conn_str):
    '''
    A function to ingest the raw weather data from text files to PostgreSQL structured table

            Parameters:
                    file_lst (list): A list of txt files to read the data from
                    conn_str (string): Connection String to establish a connection to PostgreSQL

    '''
    total_records = 0
    start = datetime.now()
    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()
    
    # DDL statement to create a table in database if it does not exist for ingestion
    create_table_query = """
    CREATE TABLE IF NOT EXISTS weather_data (
        station VARCHAR NOT NULL,
        date DATE NOT NULL,
        max_temperature INTEGER,
        min_temperature INTEGER,
        precipitation INTEGER,
        PRIMARY KEY(station, date)
    )
    """
    cursor.execute(create_table_query)
    conn.commit()
    
    i = 1
    for file in file_lst:
        # Generate a stataion id for each txt file
        station = 'Station_' + str(i)

        # Reading the txt file
        with open(os.path.join('code-challenge-template', 'wx_data', file), 'r') as f:
            # Define a set to only store unique data
            data_to_insert = set()

            # Extracting the 4 pieces of data from each row of the text file
            for line in f:
                date_str, max_temp, min_temp, precipitation = line.strip().split('\t')
                date = datetime.strptime(date_str, "%Y%m%d").date()
                data_to_check = (date, max_temp, min_temp, precipitation)
                
                # Check for duplicates
                if data_to_check not in data_to_insert:
                    data_to_insert.add(data_to_check)
            
            try:
                # Quert to ingest the data from the txt file to the database
                insert_query = """
                            INSERT INTO weather_data (station, date, max_temperature, min_temperature, precipitation)
                            VALUES (%s, %s, %s, %s, %s)
                           """
                # Execute the query with data
                for data in data_to_insert:
                    cursor.execute(insert_query, (station, data[0], data[1], data[2], data[3]))
                    total_records += 1 # Log of number of records

                conn.commit()
            except:
                continue
        i += 1
    cursor.close()
    conn.close()

    end = datetime.now()

    # Print logs
    print(f"Data ingestion completed. Total records ingested: {total_records}")
    print(f"Start Time: {start}")
    print(f"End Time: {end}")
    
ingest_weather_data(file_list, conn_string)
