import { rideOptions, savedPlaces } from './places';

describe('demo places and ride options', () => {
  it('keeps saved places usable for demo ride creation', () => {
    expect(savedPlaces).toHaveLength(3);

    for (const place of savedPlaces) {
      expect(place.id).toBeTruthy();
      expect(place.label).toBeTruthy();
      expect(place.address).toBeTruthy();
      expect(place.latitude).toBeGreaterThanOrEqual(-90);
      expect(place.latitude).toBeLessThanOrEqual(90);
      expect(place.longitude).toBeGreaterThanOrEqual(-180);
      expect(place.longitude).toBeLessThanOrEqual(180);
      expect(Number(place.distanceKm)).toBeGreaterThan(0);
      expect(place.durationMinutes).toBeGreaterThan(0);
    }
  });

  it('keeps ride options stable and ordered from cheapest to largest', () => {
    expect(rideOptions.map((option) => option.id)).toEqual(['STANDARD', 'FLEETHER', 'FLEET_PMR']);
    expect(rideOptions.map((option) => option.multiplier)).toEqual([1, 1.18, 1.35]);
    expect(rideOptions.every((option) => option.name.startsWith('Fleet'))).toBe(true);
    expect(rideOptions.every((option) => option.description.length > 0)).toBe(true);
  });
});
