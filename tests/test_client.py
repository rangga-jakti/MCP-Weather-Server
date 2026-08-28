import pytest
import respx
import httpx

from weather.models import AirQuality
from weather.client import OpenWeatherClient
from weather.exceptions import (
    CityNotFoundError,
    InvalidAPIKeyError,
    RateLimitError,
    WeatherServiceUnavailableError,
    WeatherAPIError,
)
from weather.models import CurrentWeather, CoordWeather, WeatherForecast


BASE_URL = "https://api.openweathermap.org/data/2.5"


class TestGetCurrentWeather:
    @respx.mock
    async def test_success(self, weather_client, mock_current_response):
        respx.get(f"{BASE_URL}/weather").mock(
            return_value=httpx.Response(200, json=mock_current_response)
        )

        result = await weather_client.get_current_weather("Jakarta")

        assert isinstance(result, CurrentWeather)
        assert result.city == "Jakarta"
        assert result.country == "ID"
        assert result.temperature == 31.5
        assert result.humidity == 85
        assert result.condition.main == "Rain"

    @respx.mock
    async def test_city_not_found(self, weather_client):
        respx.get(f"{BASE_URL}/weather").mock(
            return_value=httpx.Response(404, json={"message": "city not found"})
        )

        with pytest.raises(CityNotFoundError) as exc_info:
            await weather_client.get_current_weather("InvalidCityXYZ")

        assert exc_info.value.status_code == 404

    @respx.mock
    async def test_invalid_api_key(self, weather_client):
        respx.get(f"{BASE_URL}/weather").mock(
            return_value=httpx.Response(401, json={"message": "Invalid API key"})
        )

        with pytest.raises(InvalidAPIKeyError) as exc_info:
            await weather_client.get_current_weather("Jakarta")

        assert exc_info.value.status_code == 401

    @respx.mock
    async def test_rate_limit(self, weather_client):
        respx.get(f"{BASE_URL}/weather").mock(
            return_value=httpx.Response(429, json={"message": "Too Many Requests"})
        )

        with pytest.raises(RateLimitError) as exc_info:
            await weather_client.get_current_weather("Jakarta")

        assert exc_info.value.status_code == 429

    @respx.mock
    async def test_server_error(self, weather_client):
        respx.get(f"{BASE_URL}/weather").mock(
            return_value=httpx.Response(500, json={"message": "Internal Server Error"})
        )

        with pytest.raises(WeatherServiceUnavailableError) as exc_info:
            await weather_client.get_current_weather("Jakarta")

        assert exc_info.value.status_code == 500

    @respx.mock
    async def test_unknown_error(self, weather_client):
        respx.get(f"{BASE_URL}/weather").mock(
            return_value=httpx.Response(400, json={"message": "Bad request"})
        )

        with pytest.raises(WeatherAPIError):
            await weather_client.get_current_weather("Jakarta")


class TestGetForecast:
    @respx.mock
    async def test_success(self, weather_client, mock_forecast_response):
        respx.get(f"{BASE_URL}/forecast").mock(
            return_value=httpx.Response(200, json=mock_forecast_response)
        )

        result = await weather_client.get_forecast("Jakarta", days=1)

        assert isinstance(result, WeatherForecast)
        assert result.city == "Jakarta"
        assert len(result.forecasts) == 2
        assert result.forecasts[0].temperature == 30.0
        assert result.forecasts[0].rain_probability == 0.1

    async def test_invalid_days_too_low(self, weather_client):
        with pytest.raises(ValueError):
            await weather_client.get_forecast("Jakarta", days=0)

    async def test_invalid_days_too_high(self, weather_client):
        with pytest.raises(ValueError):
            await weather_client.get_forecast("Jakarta", days=6)

    @respx.mock
    async def test_city_not_found(self, weather_client):
        respx.get(f"{BASE_URL}/forecast").mock(
            return_value=httpx.Response(404, json={"message": "city not found"})
        )

        with pytest.raises(CityNotFoundError):
            await weather_client.get_forecast("InvalidCityXYZ")


class TestGetWeatherByCoords:
    @respx.mock
    async def test_success(self, weather_client, mock_current_response):
        respx.get(f"{BASE_URL}/weather").mock(
            return_value=httpx.Response(200, json=mock_current_response)
        )

        result = await weather_client.get_weather_by_coords(-6.2, 106.8)

        assert isinstance(result, CoordWeather)
        assert result.lat == -6.2
        assert result.lon == 106.8
        assert result.city == "Jakarta"

    @respx.mock
    async def test_server_error(self, weather_client):
        respx.get(f"{BASE_URL}/weather").mock(
            return_value=httpx.Response(503, json={"message": "Service Unavailable"})
        )

        with pytest.raises(WeatherServiceUnavailableError):
            await weather_client.get_weather_by_coords(-6.2, 106.8)

MOCK_AIR_QUALITY = {
    "list": [
        {
            "main": {"aqi": 2},
            "components": {
                "co": 201.94,
                "no": 0.0,
                "no2": 0.44,
                "o3": 68.66,
                "so2": 0.64,
                "pm2_5": 0.5,
                "pm10": 0.54,
                "nh3": 0.11,
            },
        }
    ]
}

class TestGetAirQuality:
    @respx.mock
    async def test_success(self, weather_client, mock_current_response):
        respx.get(f"{BASE_URL}/weather").mock(
            return_value=httpx.Response(200, json=mock_current_response)
        )
        respx.get("http://api.openweathermap.org/data/2.5/air_pollution").mock(
            return_value=httpx.Response(200, json=MOCK_AIR_QUALITY)
        )

        result = await weather_client.get_air_quality("Jakarta")

        assert isinstance(result, AirQuality)
        assert result.aqi == 2
        assert result.aqi_label == "Fair"
        assert result.components.co == 201.94

    @respx.mock
    async def test_city_not_found(self, weather_client):
        respx.get(f"{BASE_URL}/weather").mock(
            return_value=httpx.Response(404, json={"message": "city not found"})
        )

        with pytest.raises(CityNotFoundError):
            await weather_client.get_air_quality("InvalidCity")