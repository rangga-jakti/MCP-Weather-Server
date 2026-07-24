from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    openweather_api_key: str
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
    default_units: str = "metric"


settings = Settings()
