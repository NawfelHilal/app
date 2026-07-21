import { formatEuro, statusLabel } from './format';

describe('format helpers', () => {
  it('formats euro cents with two decimals', () => {
    expect(formatEuro(2500)).toBe('25.00 EUR');
    expect(formatEuro(375)).toBe('3.75 EUR');
    expect(formatEuro(0)).toBe('0.00 EUR');
  });

  it('maps known ride statuses and keeps unknown status readable', () => {
    expect(statusLabel('REQUESTED')).toBe('Recherche chauffeur');
    expect(statusLabel('ACCEPTED')).toBe('Chauffeur en route');
    expect(statusLabel('IN_PROGRESS')).toBe('Course en cours');
    expect(statusLabel('COMPLETED')).toBe('Terminee');
    expect(statusLabel('CANCELED')).toBe('Annulee');
    expect(statusLabel('CUSTOM')).toBe('CUSTOM');
  });
});
