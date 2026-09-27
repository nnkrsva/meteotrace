import { formatOptional, formatTemperature, parseCoordinates } from './format';

describe('formatTemperature', () => {
  it('adds plus sign for positive values and rounds', () => {
    expect(formatTemperature(18.4)).toBe('+18 °C');
  });
  it('keeps minus sign and shows zero without sign', () => {
    expect(formatTemperature(-3.6)).toBe('-4 °C');
    expect(formatTemperature(-0.2)).toBe('0 °C');
  });
});

describe('formatOptional', () => {
  it('renders dash for missing values', () => {
    expect(formatOptional(null, '%')).toBe('—');
    expect(formatOptional(61, '%')).toBe('61 %');
  });
});

describe('parseCoordinates', () => {
  it('parses comma separated coordinates', () => {
    expect(parseCoordinates('50.45, 30.52')).toEqual({ lat: 50.45, lon: 30.52 });
    expect(parseCoordinates('-33.9 18.4')).toEqual({ lat: -33.9, lon: 18.4 });
  });
  it('rejects invalid or out-of-range input', () => {
    expect(parseCoordinates('Kyiv')).toBeNull();
    expect(parseCoordinates('95, 10')).toBeNull();
  });
});
