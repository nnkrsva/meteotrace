export interface CurrentWeather {
  temperature_c: number;
  humidity_pct: number | null;
  pressure_hpa: number | null;
  wind_speed_ms: number | null;
  precipitation_mm: number | null;
  cloud_cover_pct: number | null;
}

export interface Forecast {
  latitude: number;
  longitude: number;
  provider: string;
  updated_at: string;
  cached: boolean;
  current: CurrentWeather;
  hourly_temperature_c: number[];
}

export interface HistoryRecord {
  id: string;
  location: string;
  latitude: number;
  longitude: number;
  created_at: string;
  forecast_snapshot: Forecast;
}
