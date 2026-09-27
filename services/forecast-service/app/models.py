from pydantic import BaseModel


class CurrentWeather(BaseModel):
    temperature_c: float
    humidity_pct: float | None = None
    pressure_hpa: float | None = None
    wind_speed_ms: float | None = None
    precipitation_mm: float | None = None
    cloud_cover_pct: float | None = None


class Forecast(BaseModel):
    latitude: float
    longitude: float
    provider: str
    updated_at: str
    cached: bool = False
    current: CurrentWeather
    hourly_temperature_c: list[float]
