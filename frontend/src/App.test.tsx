import { fireEvent, render, screen } from '@testing-library/react';
import App from './App';

const forecast = {
  latitude: 50.45,
  longitude: 30.52,
  provider: 'open-meteo',
  updated_at: '2026-09-27T12:00',
  cached: false,
  current: {
    temperature_c: 18.4,
    humidity_pct: 61,
    pressure_hpa: 1012,
    wind_speed_ms: 3.2,
    precipitation_mm: 0,
    cloud_cover_pct: 40,
  },
  hourly_temperature_c: [],
};

afterEach(() => vi.unstubAllGlobals());

it('shows forecast and adds it to history', async () => {
  const fetchMock = vi
    .fn()
    .mockResolvedValueOnce({ ok: true, json: async () => forecast })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: '1', location: '50.45, 30.52', created_at: '', forecast_snapshot: forecast }),
    });
  vi.stubGlobal('fetch', fetchMock);

  render(<App />);
  fireEvent.click(screen.getByRole('button', { name: 'Отримати прогноз' }));

  expect(await screen.findByText('+18 °C')).toBeInTheDocument();
  expect(await screen.findByText('50.45, 30.52: +18 °C')).toBeInTheDocument();
  expect(fetchMock).toHaveBeenCalledWith('/api/v1/forecast?lat=50.45&lon=30.52');
});

it('validates coordinates before calling the API', () => {
  const fetchMock = vi.fn();
  vi.stubGlobal('fetch', fetchMock);

  render(<App />);
  fireEvent.change(screen.getByLabelText('Координати'), { target: { value: 'abc' } });
  fireEvent.click(screen.getByRole('button', { name: 'Отримати прогноз' }));

  expect(screen.getByRole('alert')).toHaveTextContent('широта, довгота');
  expect(fetchMock).not.toHaveBeenCalled();
});

it('shows an error when the forecast service fails', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 503 }));

  render(<App />);
  fireEvent.click(screen.getByRole('button', { name: 'Отримати прогноз' }));

  expect(await screen.findByRole('alert')).toHaveTextContent('503');
});
