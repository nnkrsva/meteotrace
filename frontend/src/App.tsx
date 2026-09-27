import { useState, type FormEvent } from 'react';
import { fetchForecast, saveHistory } from './api';
import { formatOptional, formatTemperature, parseCoordinates } from './format';
import type { Forecast, HistoryRecord } from './types';

export default function App() {
  const [query, setQuery] = useState('50.45, 30.52');
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const coords = parseCoordinates(query);
    if (!coords) {
      setError('Введіть координати у форматі «широта, довгота»');
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const result = await fetchForecast(coords.lat, coords.lon);
      setForecast(result);
      const record = await saveHistory(query, result);
      setHistory((prev) => [record, ...prev]);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Невідома помилка');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>MeteoTrace</h1>
      <form onSubmit={onSubmit}>
        <label htmlFor="query">Координати</label>
        <input id="query" value={query} onChange={(e) => setQuery(e.target.value)} />
        <button type="submit" disabled={loading}>
          {loading ? 'Завантаження…' : 'Отримати прогноз'}
        </button>
      </form>
      {error && <p role="alert">{error}</p>}
      {forecast && (
        <section aria-label="Поточна погода">
          <p className="temperature">{formatTemperature(forecast.current.temperature_c)}</p>
          <p>Вологість: {formatOptional(forecast.current.humidity_pct, '%')}</p>
          <p>Вітер: {formatOptional(forecast.current.wind_speed_ms, 'м/с')}</p>
          <p>
            Джерело: {forecast.provider}, оновлено {forecast.updated_at}
            {forecast.cached && ' (з кешу)'}
          </p>
        </section>
      )}
      <section aria-label="Історія запитів">
        <h2>Історія запитів</h2>
        {history.length === 0 ? (
          <p>Історія порожня</p>
        ) : (
          <ul>
            {history.map((r) => (
              <li key={r.id}>
                {r.location}: {formatTemperature(r.forecast_snapshot.current.temperature_c)}
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
