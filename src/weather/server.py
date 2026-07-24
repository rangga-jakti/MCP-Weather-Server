from fastmcp import FastMCP

from .client import OpenWeatherClient
from .exceptions import WeatherAPIError

mcp = FastMCP(
    name="mcp-weather-server",
    instructions=(
        "Weather server providing current conditions, forecasts, and coordinate-based lookups "
        "via OpenWeather API. Units are metric (Celsius, m/s)."
    ),
)

client = OpenWeatherClient()


@mcp.tool()
async def get_current_weather(city: str) -> dict:
    """
    Get current weather for a city.

    Args:
        city: City name (e.g. 'Jakarta', 'London', 'New York')

    Returns:
        Current weather data including temperature, humidity, wind, and conditions.
    """
    try:
        weather = await client.get_current_weather(city)
        return weather.model_dump()
    except WeatherAPIError as e:
        return {"error": str(e), "status_code": e.status_code}


@mcp.tool()
async def get_forecast(city: str, days: int = 5) -> dict:
    """
    Get weather forecast for a city.

    Args:
        city: City name (e.g. 'Jakarta', 'London')
        days: Number of days to forecast (1-5, default: 5)

    Returns:
        Weather forecast with 3-hour intervals for the specified number of days.
    """
    try:
        forecast = await client.get_forecast(city, days)
        return forecast.model_dump()
    except ValueError as e:
        return {"error": str(e)}
    except WeatherAPIError as e:
        return {"error": str(e), "status_code": e.status_code}


@mcp.tool()
async def get_weather_by_coords(lat: float, lon: float) -> dict:
    """
    Get current weather by geographic coordinates.

    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)

    Returns:
        Current weather data for the given coordinates.
    """
    if not -90 <= lat <= 90:
        return {"error": "Latitude must be between -90 and 90"}
    if not -180 <= lon <= 180:
        return {"error": "Longitude must be between -180 and 180"}

    try:
        weather = await client.get_weather_by_coords(lat, lon)
        return weather.model_dump()
    except WeatherAPIError as e:
        return {"error": str(e), "status_code": e.status_code}


def main():
    mcp.run()


if __name__ == "__main__":
    main()
