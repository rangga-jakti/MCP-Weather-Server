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
    rain_probability: float = Field(
        default=0.0, description="Probability of precipitation (0-1)"
    )


class WeatherForecast(BaseModel):
    city: str
    country: str
    forecasts: list[ForecastItem]


class CoordWeather(CurrentWeather):
    lat: float
    lon: float


class AirQualityComponents(BaseModel):
    co: float = Field(description="Carbon monoxide (ug/m3)")
    no: float = Field(description="Nitrogen monoxide (ug/m3)")
    no2: float = Field(description="Nitrogen dioxide (ug/m3)")
    o3: float = Field(description="Ozone (ug/m3)")
    so2: float = Field(description="Sulphur dioxide (ug/m3)")
    pm2_5: float = Field(description="Fine particles PM2.5 (ug/m3)")
    pm10: float = Field(description="Coarse particles PM10 (ug/m3)")
    nh3: float = Field(description="Ammonia (ug/m3)")


class AirQuality(BaseModel):
    lat: float
    lon: float
    aqi: int = Field(description="AQI: 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor")
    aqi_label: str
    components: AirQualityComponents


AQI_LABELS = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}