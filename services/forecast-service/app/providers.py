"""Weather data providers normalised to a single Forecast format."""

from datetime import UTC, datetime

import httpx

from app.models import CurrentWeather, Forecast


class ProviderError(Exception):
    pass


class OpenMeteoProvider:
    name = "open-meteo"
    url = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, client: httpx.Client):
        self.client = client

    def fetch(self, lat: float, lon: float) -> Forecast:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,surface_pressure,"
            "wind_speed_10m,precipitation,cloud_cover",
            "hourly": "temperature_2m",
            "forecast_hours": 48,
            "wind_speed_unit": "ms",
        }
        try:
            resp = self.client.get(self.url, params=params, timeout=5.0)
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderError(f"{self.name}: {exc}") from exc

        cur = data["current"]
        return Forecast(
            latitude=lat,
            longitude=lon,
            provider=self.name,
            updated_at=cur.get("time", datetime.now(UTC).isoformat()),
            current=CurrentWeather(
                temperature_c=cur["temperature_2m"],
                humidity_pct=cur.get("relative_humidity_2m"),
                pressure_hpa=cur.get("surface_pressure"),
                wind_speed_ms=cur.get("wind_speed_10m"),
                precipitation_mm=cur.get("precipitation"),
                cloud_cover_pct=cur.get("cloud_cover"),
            ),
            hourly_temperature_c=data["hourly"]["temperature_2m"][:48],
        )
