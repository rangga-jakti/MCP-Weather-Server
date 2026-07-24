from pydantic import BaseModel, Field


class WeatherCondition(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class CurrentWeather(BaseModel):
    city: str
    country: str
    temperature: float = Field(description="Temperature in Celsius")
    feels_like: float = Field(description="Feels like temperature in Celsius")
    temp_min: float
    temp_max: float
    humidity: int = Field(description="Humidity percentage")
    pressure: int = Field(description="Atmospheric pressure in hPa")
    wind_speed: float = Field(description="Wind speed in m/s")
    wind_deg: int = Field(description="Wind direction in degrees")
    visibility: int = Field(description="Visibility in meters")
    condition: WeatherCondition
    sunrise: int = Field(description="Sunrise time (Unix timestamp)")
    sunset: int = Field(description="Sunset time (Unix timestamp)")


class ForecastItem(BaseModel):
    dt: int = Field(description="Forecast time (Unix timestamp)")
    datetime_str: str
    temperature: float
    feels_like: float
    temp_min: float
    temp_max: float
    humidity: int
    wind_speed: float
    condition: WeatherCondition
    rain_probability: float = Field(default=0.0, description="Probability of precipitation (0-1)")


class WeatherForecast(BaseModel):
    city: str
    country: str
    forecasts: list[ForecastItem]


class CoordWeather(CurrentWeather):
    lat: float
    lon: float
