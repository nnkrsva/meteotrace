import httpx
from fastapi.testclient import TestClient

from app.main import app, get_service
from app.providers import OpenMeteoProvider, ProviderError
from app.service import ForecastService, TTLCache

OPEN_METEO_RESPONSE = {
    "current": {
        "time": "2026-09-27T12:00",
        "temperature_2m": 18.4,
        "relative_humidity_2m": 61,
        "surface_pressure": 1012.3,
        "wind_speed_10m": 3.2,
        "precipitation": 0.0,
        "cloud_cover": 40,
    },
    "hourly": {"temperature_2m": [float(i) for i in range(60)]},
}


def provider_with(handler) -> OpenMeteoProvider:
    return OpenMeteoProvider(httpx.Client(transport=httpx.MockTransport(handler)))


def ok_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=OPEN_METEO_RESPONSE)


def failing_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(500)


class CountingProvider:
    def __init__(self, inner):
        self.inner, self.calls = inner, 0

    def fetch(self, lat, lon):
        self.calls += 1
        return self.inner.fetch(lat, lon)


def test_open_meteo_response_is_normalised():
    f = provider_with(ok_handler).fetch(50.45, 30.52)
    assert f.provider == "open-meteo"
    assert f.current.temperature_c == 18.4
    assert f.current.wind_speed_ms == 3.2
    assert len(f.hourly_temperature_c) == 48


def test_provider_error_on_http_failure():
    try:
        provider_with(failing_handler).fetch(0, 0)
    except ProviderError:
        return
    raise AssertionError("ProviderError expected")


def test_fallback_to_reserve_provider():
    primary = provider_with(failing_handler)
    reserve = provider_with(ok_handler)
    reserve.name = "reserve"
    svc = ForecastService([primary, reserve], TTLCache(600))
    assert svc.get_forecast(50.45, 30.52).current.temperature_c == 18.4


def test_cache_hit_and_expiry():
    now = [0.0]
    provider = CountingProvider(provider_with(ok_handler))
    svc = ForecastService([provider], TTLCache(600, clock=lambda: now[0]))

    assert svc.get_forecast(50.451, 30.521).cached is False
    assert svc.get_forecast(50.452, 30.522).cached is True  # same ~1 km cell
    assert provider.calls == 1

    now[0] = 601
    svc.get_forecast(50.451, 30.521)
    assert provider.calls == 2


def test_api_endpoint_and_validation():
    svc = ForecastService([provider_with(ok_handler)], TTLCache(600))
    app.dependency_overrides[get_service] = lambda: svc
    client = TestClient(app)
    try:
        ok = client.get("/api/v1/forecast", params={"lat": 50.45, "lon": 30.52})
        assert ok.status_code == 200
        bad = client.get("/api/v1/forecast", params={"lat": 120, "lon": 0})
        assert bad.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_api_returns_503_when_all_providers_fail():
    svc = ForecastService([provider_with(failing_handler)], TTLCache(600))
    app.dependency_overrides[get_service] = lambda: svc
    try:
        r = TestClient(app).get("/api/v1/forecast", params={"lat": 1, "lon": 1})
        assert r.status_code == 503
    finally:
        app.dependency_overrides.clear()
