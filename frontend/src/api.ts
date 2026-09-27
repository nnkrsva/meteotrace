import type { Forecast, HistoryRecord } from './types';

const USER_ID = 'demo-user'; // replaced by JWT from auth-service at later stages

export async function fetchForecast(lat: number, lon: number): Promise<Forecast> {
  const resp = await fetch(`/api/v1/forecast?lat=${lat}&lon=${lon}`);
  if (!resp.ok) throw new Error(`Forecast request failed: ${resp.status}`);
  return resp.json();
}

export async function saveHistory(location: string, forecast: Forecast): Promise<HistoryRecord> {
  const resp = await fetch('/api/v1/history', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-User-Id': USER_ID },
    body: JSON.stringify({
      location,
      latitude: forecast.latitude,
      longitude: forecast.longitude,
      forecast_snapshot: forecast,
    }),
  });
  if (!resp.ok) throw new Error(`History request failed: ${resp.status}`);
  return resp.json();
}
