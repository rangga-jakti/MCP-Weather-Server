class WeatherAPIError(Exception):
    """Base exception for Weather API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class CityNotFoundError(WeatherAPIError):
    """Raised when city is not found."""


class InvalidAPIKeyError(WeatherAPIError):
    """Raised when API key is invalid."""


class RateLimitError(WeatherAPIError):
    """Raised when API rate limit is exceeded."""


class WeatherServiceUnavailableError(WeatherAPIError):
    """Raised when OpenWeather service is unavailable."""
