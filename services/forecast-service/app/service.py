import time

from app.models import Forecast
from app.providers import ProviderError


class TTLCache:
    """Minimal in-memory TTL cache (Redis replaces it at stage 2)."""

    def __init__(self, ttl_seconds: float, clock=time.monotonic):
        self.ttl = ttl_seconds
        self.clock = clock
        self._data: dict[str, tuple[float, Forecast]] = {}

    def get(self, key: str) -> Forecast | None:
        item = self._data.get(key)
        if item is None or self.clock() - item[0] > self.ttl:
            return None
        return item[1]

    def set(self, key: str, value: Forecast) -> None:
        self._data[key] = (self.clock(), value)


class ForecastService:
    """Queries providers in priority order and falls back to the next one on failure."""

    def __init__(self, providers: list, cache: TTLCache):
        self.providers = providers
        self.cache = cache

    @staticmethod
    def cache_key(lat: float, lon: float) -> str:
        # ~1 km grid so that nearby requests share a cache entry
        return f"{round(lat, 2)}:{round(lon, 2)}"

    def get_forecast(self, lat: float, lon: float) -> Forecast:
        key = self.cache_key(lat, lon)
        if cached := self.cache.get(key):
            return cached.model_copy(update={"cached": True})

        errors = []
        for provider in self.providers:
            try:
                forecast = provider.fetch(lat, lon)
            except ProviderError as exc:
                errors.append(str(exc))
                continue
            self.cache.set(key, forecast)
            return forecast
        raise ProviderError("; ".join(errors) or "no providers configured")
