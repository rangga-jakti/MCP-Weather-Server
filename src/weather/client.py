from datetime import datetime

import httpx

from .config import settings
from .exceptions import (
    CityNotFoundError,
    InvalidAPIKeyError,
    RateLimitError,
    WeatherAPIError,
    WeatherServiceUnavailableError,
)
from .models import (
    CoordWeather,
    CurrentWeather,
    ForecastItem,
    WeatherCondition,
    WeatherForecast,
)


class OpenWeatherClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        units: str | None = None,
    ):
        self.api_key = api_key or settings.openweather_api_key
        self.base_url = base_url or settings.openweather_base_url
        self.units = units or settings.default_units

    def _handle_error(self, status_code: int, message: str) -> None:
        if status_code == 401:
            raise InvalidAPIKeyError(message, status_code)
        elif status_code == 404:
            raise CityNotFoundError(message, status_code)
        elif status_code == 429:
            raise RateLimitError(message, status_code)
        elif status_code >= 500:
            raise WeatherServiceUnavailableError(message, status_code)
        else:
            raise WeatherAPIError(message, status_code)

    def _parse_current(self, data: dict, lat: float | None = None, lon: float | None = None) -> CurrentWeather:
        condition = WeatherCondition(**data["weather"][0])
        base = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "temp_min": data["main"]["temp_min"],
            "temp_max": data["main"]["temp_max"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "wind_deg": data["wind"].get("deg", 0),
            "visibility": data.get("visibility", 0),
            "condition": condition,
            "sunrise": data["sys"]["sunrise"],
            "sunset": data["sys"]["sunset"],
        }
        if lat is not None and lon is not None:
            return CoordWeather(**base, lat=lat, lon=lon)
        return CurrentWeather(**base)

    async def get_current_weather(self, city: str) -> CurrentWeather:
        params = {
            "q": city,
            "appid": self.api_key,
            "units": self.units,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/weather", params=params)
            if response.status_code != 200:
                data = response.json()
                self._handle_error(response.status_code, data.get("message", "Unknown error"))
            return self._parse_current(response.json())

    async def get_forecast(self, city: str, days: int = 5) -> WeatherForecast:
        if not 1 <= days <= 5:
            raise ValueError("days must be between 1 and 5")

        params = {
            "q": city,
            "appid": self.api_key,
            "units": self.units,
            "cnt": days * 8,  # 8 intervals per day (every 3 hours)
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/forecast", params=params)
            if response.status_code != 200:
                data = response.json()
                self._handle_error(response.status_code, data.get("message", "Unknown error"))

        data = response.json()
        forecasts = []
        for item in data["list"]:
            forecasts.append(
                ForecastItem(
                    dt=item["dt"],
                    datetime_str=datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d %H:%M"),
                    temperature=item["main"]["temp"],
                    feels_like=item["main"]["feels_like"],
                    temp_min=item["main"]["temp_min"],
                    temp_max=item["main"]["temp_max"],
                    humidity=item["main"]["humidity"],
                    wind_speed=item["wind"]["speed"],
                    condition=WeatherCondition(**item["weather"][0]),
                    rain_probability=item.get("pop", 0.0),
                )
            )

        return WeatherForecast(
            city=data["city"]["name"],
            country=data["city"]["country"],
            forecasts=forecasts,
        )

    async def get_weather_by_coords(self, lat: float, lon: float) -> CoordWeather:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": self.units,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/weather", params=params)
            if response.status_code != 200:
                data = response.json()
                self._handle_error(response.status_code, data.get("message", "Unknown error"))
        return self._parse_current(response.json(), lat=lat, lon=lon)
