# importing dependencies
from flask import Flask
from flask_restful import Api, Resource, reqparse, fields, abort
from flask_swagger_ui import get_swaggerui_blueprint
import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/openapi.json'  # Local API document

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, 
    API_URL,
    config={  
        'app_name': "Test application"
    },
)

app.register_blueprint(swaggerui_blueprint)
api = Api(app)

# Database Credentials
db_connection_params = {
    'dbname': os.getenv("DBNAME"),
    'user': os.getenv("USER"),
    'password': os.getenv("PASSWORD"),
    'host': os.getenv("HOST"),
}

# Function to establish a connection to the database
def get_db_connection():
    return psycopg2.connect(**db_connection_params)

# Define the parser for query string parameters
parser = reqparse.RequestParser()
parser.add_argument('date', location = 'args', type=str, help='Filter by date in YYYY-MM-DD format')
parser.add_argument('station_id', location = 'args', type=str, help='Filter by station ID')
parser.add_argument('page', location = 'args', type=int, default=1, help='Page number for pagination')

# Weather data fields to be returned in the response
weather_fields = {
    'station': fields.String,
    'date': fields.String,
    'max_temperature_degC': fields.Float,
    'min_temperature_degC': fields.Float,
    'precipitation_mm': fields.Float
}

# Weather statistics fields to be returned in the response
stats_fields = {
    'year': fields.Integer,
    'station': fields.String,
    'average_max_temperature_degC': fields.Float,
    'average_min_temperature_degC': fields.Float,
    'total_precipitation_cm': fields.Float
}

# Resource for the /api/weather endpoint
class WeatherResource(Resource):
    
    def get(self):
        args = parser.parse_args()
        conn = get_db_connection()
        cursor = conn.cursor()

        # Construct the SQL query based on the query string parameters
        query = "SELECT station, date, max_temperature, min_temperature, precipitation FROM weather_data WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM weather_data WHERE 1=1"

        # If a date is provided, use it to filter the query
        if args['date']:
            try:
                date = datetime.strptime(args['date'], '%Y-%m-%d').date()
                query += f" AND date = '{date}'"
                count_query += f" AND date = '{date}'"
            except ValueError:
                abort(400, message="Invalid date format. Please use YYYY-MM-DD.")

        # If a station id is provided, use it to filter the query
        if args['station_id']:
            query += f" AND station = '{args['station_id']}'"
            count_query += f" AND station = '{args['station_id']}'"

        # Pagination
        page = args['page']
        page_size = 10  # Number of records per page
        offset = (page - 1) * page_size
        query += f" ORDER BY date LIMIT {page_size} OFFSET {offset}"

        # Execute the query
        cursor.execute(query)
        weather_data = cursor.fetchall()

        # Execute count query to get total number of pages
        cursor.execute(count_query)
        total_records = cursor.fetchone()[0]
        total_pages = (total_records + page_size - 1) // page_size
        cursor.close()
        conn.close()
        response = []

        # Convert the result to JSON
        for data in weather_data:
            varJson = {
                'station': data[0],
                'date': str(data[1]),
                'max_temperature_degC': data[2],
                'min_temperature_degC': data[3],
                'precipitation_mm': data[4]
            }
            response.append(varJson)
        response.append({'total_pages': total_pages})
        return response

# Resource for the /api/weather/stats endpoint
class WeatherStatsResource(Resource):
    def get(self):
        args = parser.parse_args()
        conn = get_db_connection()
        cursor = conn.cursor()

        # Construct the SQL query based on the query string parameters
        query = """
            SELECT station, year,
                   avg_max_temperature_degC,
                   avg_min_temperature_degC,
                   total_precipitation_cm
            FROM weather_statistics
            WHERE 1=1
                """
        
        count_query = "SELECT COUNT(*) FROM weather_statistics WHERE 1=1"
        # If a date is provided, convert it to year and use it to filter the query
        if args['date']:
            try:
                year = args['date'].split('-')[0]
                query += f" AND year = '{year}'"
                count_query += f" AND year = '{year}'"
            except ValueError:
                abort(400, message="Invalid year")

        # If a station_id is provided, use it to filter the query
        if args['station_id']:
            query += f" AND station = '{args['station_id']}'"
            count_query += f" AND station = '{args['station_id']}'"

        # Pagination
        page = args['page']
        page_size = 10  # Number of records per page
        offset = (page - 1) * page_size
        query += f" ORDER BY year LIMIT {page_size} OFFSET {offset}"

        cursor.execute(query)
        weather_stats = cursor.fetchall()

        # Execute count query to get total number of pages
        cursor.execute(count_query)
        total_records = cursor.fetchone()[0]
        total_pages = (total_records + page_size - 1) // page_size
        cursor.close()
        conn.close()

        response = []
        for data in weather_stats:
            varJson = {
                'station': data[0],
                'year': str(data[1]),
                'avg_max_temperature_degC': data[2],
                'avg_min_temperature_degC': data[3],
                'total_precipitation_cm': data[4]
            }
            response.append(varJson)


        response.append({'total_pages': total_pages})
        return response

# Add the resources to the API
api.add_resource(WeatherResource, '/api/weather')
api.add_resource(WeatherStatsResource, '/api/weather/stats')

if __name__ == '__main__':
    app.run(debug = True)
