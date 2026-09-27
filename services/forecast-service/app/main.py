import httpx
from fastapi import Depends, FastAPI, HTTPException, Query

from app.models import Forecast
from app.providers import OpenMeteoProvider, ProviderError
from app.service import ForecastService, TTLCache

app = FastAPI(title="MeteoTrace forecast-service", version="0.1.0")

_service = ForecastService([OpenMeteoProvider(httpx.Client())], TTLCache(ttl_seconds=600))


def get_service() -> ForecastService:
    return _service


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "forecast-service"}


@app.get("/api/v1/forecast", response_model=Forecast)
def forecast(
    lat: float = Query(ge=-90, le=90),
    lon: float = Query(ge=-180, le=180),
    service: ForecastService = Depends(get_service),
) -> Forecast:
    try:
        return service.get_forecast(lat, lon)
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail="Weather providers unavailable") from exc
