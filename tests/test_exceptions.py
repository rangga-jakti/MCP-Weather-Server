import pytest

from weather.exceptions import (
    CityNotFoundError,
    InvalidAPIKeyError,
    RateLimitError,
    WeatherAPIError,
    WeatherServiceUnavailableError,
)


class TestExceptions:
    def test_weather_api_error_base(self):
        err = WeatherAPIError("something went wrong", status_code=400)
        assert str(err) == "something went wrong"
        assert err.status_code == 400

    def test_weather_api_error_no_status(self):
        err = WeatherAPIError("unknown error")
        assert err.status_code is None

    def test_city_not_found_is_weather_error(self):
        err = CityNotFoundError("city not found", 404)
        assert isinstance(err, WeatherAPIError)
        assert err.status_code == 404

    def test_invalid_api_key_is_weather_error(self):
        err = InvalidAPIKeyError("invalid key", 401)
        assert isinstance(err, WeatherAPIError)

    def test_rate_limit_is_weather_error(self):
        err = RateLimitError("rate limited", 429)
        assert isinstance(err, WeatherAPIError)

    def test_service_unavailable_is_weather_error(self):
        err = WeatherServiceUnavailableError("unavailable", 503)
        assert isinstance(err, WeatherAPIError)

    def test_exception_hierarchy_catchable_as_base(self):
        with pytest.raises(WeatherAPIError):
            raise CityNotFoundError("city not found", 404)
