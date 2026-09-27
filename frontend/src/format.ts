export function formatTemperature(value: number): string {
  const rounded = Math.round(value);
  return `${rounded > 0 ? '+' : ''}${rounded === 0 ? 0 : rounded} °C`;
}

export function formatOptional(value: number | null, unit: string): string {
  return value === null || value === undefined ? '—' : `${value} ${unit}`;
}

export function parseCoordinates(input: string): { lat: number; lon: number } | null {
  const match = input.trim().match(/^(-?\d+(?:\.\d+)?)\s*[,;\s]\s*(-?\d+(?:\.\d+)?)$/);
  if (!match) return null;
  const lat = Number(match[1]);
  const lon = Number(match[2]);
  if (Math.abs(lat) > 90 || Math.abs(lon) > 180) return null;
  return { lat, lon };
}
