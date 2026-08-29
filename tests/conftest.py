import pytest

from weather.client import OpenWeatherClient

MOCK_CURRENT_WEATHER = {
    "name": "Jakarta",
    "sys": {"country": "ID", "sunrise": 1700000000, "sunset": 1700043600},
    "main": {
        "temp": 31.5,
        "feels_like": 36.2,
        "temp_min": 29.0,
        "temp_max": 33.0,
        "humidity": 85,
        "pressure": 1010,
    },
    "wind": {"speed": 4.2, "deg": 180},
    "visibility": 10000,
    "weather": [{"id": 502, "main": "Rain", "description": "heavy intensity rain", "icon": "10d"}],
    "coord": {"lat": -6.2, "lon": 106.8},
}

MOCK_FORECAST = {
    "city": {"name": "Jakarta", "country": "ID"},
    "list": [
        {
            "dt": 1700010000,
            "main": {
                "temp": 30.0,
                "feels_like": 34.0,
                "temp_min": 28.0,
                "temp_max": 32.0,
                "humidity": 80,
            },
            "wind": {"speed": 3.5},
            "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
            "pop": 0.1,
        },
        {
            "dt": 1700020800,
            "main": {
                "temp": 29.0,
                "feels_like": 33.0,
                "temp_min": 27.0,
                "temp_max": 31.0,
                "humidity": 82,
            },
            "wind": {"speed": 3.0},
            "weather": [{"id": 801, "main": "Clouds", "description": "few clouds", "icon": "02d"}],
            "pop": 0.2,
        },
    ],
}


@pytest.fixture
def weather_client():
    return OpenWeatherClient(
        api_key="test_api_key",
        base_url="https://api.openweathermap.org/data/2.5",
        units="metric",
    )


@pytest.fixture
def mock_current_response():
    return MOCK_CURRENT_WEATHER.copy()


@pytest.fixture
def mock_forecast_response():
    return MOCK_FORECAST.copy()
