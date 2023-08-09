# import dependencies
import pytest
import sys
sys.path.append("..")
from scripts.app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_get_weather_data(client):
    # Test case for GET /api/weather
    response = client.get('/api/weather')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_weather_stats(client):
    # Test case for GET /api/weather/stats
    response = client.get('/api/weather/stats')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_weather_data_with_date_filter(client):
    # Test case for GET /api/weather with date filter
    response = client.get('/api/weather?date=2023-07-29')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_weather_data_with_invalid_date_format(client):
    # Test case for GET /api/weather with invalid date format
    response = client.get('/api/weather?date=2011/07/29')
    assert response.status_code == 400

def test_get_weather_data_with_station_id_filter(client):
    # Test case for GET /api/weather with station ID filter
    response = client.get('/api/weather?station_id="Station_1"')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_weather_stats_with_date_filter(client):
    # Test case for GET /api/weather/stats with date filter
    response = client.get('/api/weather/stats?date=2023-07-29')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_weather_data_pagination(client):
    # Test case for GET /api/weather with pagination
    response = client.get('/api/weather?page=2')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0

def test_get_weather_stats_pagination(client):
    # Test case for GET /api/weather/stats with pagination
    response = client.get('/api/weather/stats?page=2')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0

def test_get_weather_data_with_invalid_page(client):
    # Test case for GET /api/weather with invalid page number
    response = client.get('/api/weather?page=invalid_page')
    assert response.status_code == 400

def test_get_weather_stats_with_invalid_page(client):
    # Test case for GET /api/weather/stats with invalid page number
    response = client.get('/api/weather/stats?page=invalid_page')
    assert response.status_code == 400

def test_get_weather_data_with_invalid_station_id(client):
    # Test case for GET /api/weather with invalid station ID
    response = client.get('/api/weather?station_id=InvalidStationID')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 1

def test_get_weather_stats_with_invalid_station_id(client):
    # Test case for GET /api/weather/stats with invalid station ID
    response = client.get('/api/weather/stats?station_id=InvalidStationID')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 1
