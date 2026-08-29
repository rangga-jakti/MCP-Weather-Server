from unittest.mock import AsyncMock, patch

from weather import server
from weather.exceptions import CityNotFoundError, InvalidAPIKeyError, RateLimitError
from weather.models import (
    CoordWeather,
    CurrentWeather,
    ForecastItem,
    WeatherCondition,
    WeatherForecast,
)


def make_current_weather(**kwargs) -> CurrentWeather:
    defaults = dict(
        city="Jakarta",
        country="ID",
        temperature=31.5,
        feels_like=36.2,
        temp_min=29.0,
        temp_max=33.0,
        humidity=85,
        pressure=1010,
        wind_speed=4.2,
        wind_deg=180,
        visibility=10000,
        condition=WeatherCondition(id=502, main="Rain", description="heavy intensity rain", icon="10d"),
        sunrise=1700000000,
        sunset=1700043600,
    )
    defaults.update(kwargs)
    return CurrentWeather(**defaults)


def make_forecast(**kwargs) -> WeatherForecast:
    return WeatherForecast(
        city=kwargs.get("city", "Jakarta"),
        country=kwargs.get("country", "ID"),
        forecasts=[
            ForecastItem(
                dt=1700010000,
                datetime_str="2024-11-15 06:00",
                temperature=30.0,
                feels_like=34.0,
                temp_min=28.0,
                temp_max=32.0,
                humidity=80,
                wind_speed=3.5,
                condition=WeatherCondition(id=800, main="Clear", description="clear sky", icon="01d"),
                rain_probability=0.1,
            )
        ],
    )


class TestGetCurrentWeatherTool:
    async def test_success(self):
        mock_weather = make_current_weather()
        with patch.object(server.client, "get_current_weather", new=AsyncMock(return_value=mock_weather)):
            result = await server.get_current_weather("Jakarta")

        assert result["city"] == "Jakarta"
        assert result["temperature"] == 31.5
        assert "error" not in result

    async def test_city_not_found(self):
        with patch.object(
            server.client,
            "get_current_weather",
            new=AsyncMock(side_effect=CityNotFoundError("city not found", 404)),
        ):
            result = await server.get_current_weather("InvalidCityXYZ")

        assert "error" in result
        assert result["status_code"] == 404

    async def test_invalid_api_key(self):
        with patch.object(
            server.client,
            "get_current_weather",
            new=AsyncMock(side_effect=InvalidAPIKeyError("Invalid API key", 401)),
        ):
            result = await server.get_current_weather("Jakarta")

        assert "error" in result
        assert result["status_code"] == 401

    async def test_rate_limit(self):
        with patch.object(
            server.client,
            "get_current_weather",
            new=AsyncMock(side_effect=RateLimitError("Too many requests", 429)),
        ):
            result = await server.get_current_weather("Jakarta")

        assert "error" in result
        assert result["status_code"] == 429


class TestGetForecastTool:
    async def test_success(self):
        mock_forecast = make_forecast()
        with patch.object(server.client, "get_forecast", new=AsyncMock(return_value=mock_forecast)):
            result = await server.get_forecast("Jakarta", days=1)

        assert result["city"] == "Jakarta"
        assert len(result["forecasts"]) == 1
        assert "error" not in result

    async def test_invalid_days(self):
        with patch.object(
            server.client,
            "get_forecast",
            new=AsyncMock(side_effect=ValueError("days must be between 1 and 5")),
        ):
            result = await server.get_forecast("Jakarta", days=10)

        assert "error" in result

    async def test_city_not_found(self):
        with patch.object(
            server.client,
            "get_forecast",
            new=AsyncMock(side_effect=CityNotFoundError("city not found", 404)),
        ):
            result = await server.get_forecast("InvalidCity")

        assert "error" in result
        assert result["status_code"] == 404


class TestGetWeatherByCoordsTool:
    async def test_success(self):
        mock_weather = CoordWeather(
            **make_current_weather().__dict__,
            lat=-6.2,
            lon=106.8,
        )
        with patch.object(server.client, "get_weather_by_coords", new=AsyncMock(return_value=mock_weather)):
            result = await server.get_weather_by_coords(-6.2, 106.8)

        assert result["city"] == "Jakarta"
        assert result["lat"] == -6.2
        assert result["lon"] == 106.8
        assert "error" not in result

    async def test_invalid_latitude(self):
        result = await server.get_weather_by_coords(lat=91.0, lon=106.8)
        assert "error" in result
        assert "Latitude" in result["error"]

    async def test_invalid_longitude(self):
        result = await server.get_weather_by_coords(lat=-6.2, lon=200.0)
        assert "error" in result
        assert "Longitude" in result["error"]

    async def test_boundary_coords(self):
        mock_weather = CoordWeather(
            **make_current_weather().__dict__,
            lat=90.0,
            lon=180.0,
        )
        with patch.object(server.client, "get_weather_by_coords", new=AsyncMock(return_value=mock_weather)):
            result = await server.get_weather_by_coords(90.0, 180.0)

        assert "error" not in result
