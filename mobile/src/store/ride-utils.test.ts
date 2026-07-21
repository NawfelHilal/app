import type { Ride } from '../api/client';
import { replaceRide } from './ride-utils';

function ride(id: number, status: Ride['status'] = 'REQUESTED'): Ride {
  return {
    id,
    status,
    service_type: 'STANDARD',
    pickup_label: 'Paris',
    pickup_latitude: '48.856600',
    pickup_longitude: '2.352200',
    dropoff_label: 'Tour Eiffel',
    dropoff_latitude: '48.858400',
    dropoff_longitude: '2.294500',
    passenger_note: '',
    cancellation_reason: '',
    distance_km: '10.00',
    duration_minutes: 20,
    estimated_fare_cents: 2500,
    final_fare_cents: null,
    commission_cents: 375,
    driver_earnings_cents: 2125,
    payment_status: null,
    requested_at: '2026-07-21T10:00:00Z',
  };
}

describe('replaceRide', () => {
  it('prepends unknown rides without mutating existing state', () => {
    const existing = [ride(1)];
    const updated = ride(2, 'ACCEPTED');

    const result = replaceRide(existing, updated);

    expect(result.map((item) => item.id)).toEqual([2, 1]);
    expect(existing.map((item) => item.id)).toEqual([1]);
  });

  it('replaces existing ride by id while preserving list order', () => {
    const existing = [ride(2, 'ACCEPTED'), ride(1, 'REQUESTED')];
    const updated = ride(1, 'CANCELED');

    const result = replaceRide(existing, updated);

    expect(result.map((item) => item.id)).toEqual([2, 1]);
    expect(result.map((item) => item.status)).toEqual(['ACCEPTED', 'CANCELED']);
    expect(existing[1].status).toBe('REQUESTED');
  });
});
