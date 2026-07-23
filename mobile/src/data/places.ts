import { demoDropoff } from './demoRoute';

export type PlaceSuggestion = {
  id: string;
  label: string;
  address: string;
  latitude: number;
  longitude: number;
  distanceKm: string;
  durationMinutes: number;
};

export const savedPlaces: PlaceSuggestion[] = [
  {
    id: 'airport',
    label: demoDropoff.label,
    address: demoDropoff.address,
    latitude: demoDropoff.latitude,
    longitude: demoDropoff.longitude,
    distanceKm: '6.40',
    durationMinutes: 18,
  },
  {
    id: 'old-town',
    label: 'Vieux Nice',
    address: 'Cours Saleya, Nice',
    latitude: 43.695034,
    longitude: 7.276565,
    distanceKm: '2.10',
    durationMinutes: 9,
  },
  {
    id: 'station',
    label: 'Gare Nice-Ville',
    address: 'Avenue Thiers, Nice',
    latitude: 43.704556,
    longitude: 7.261944,
    distanceKm: '1.80',
    durationMinutes: 8,
  },
];

export const rideOptions = [
  {
    id: 'STANDARD',
    name: 'Fleet Standard',
    seats: '4 places',
    eta: '3 min',
    multiplier: 1,
    description: 'Course classique avec chauffeur disponible proche.',
  },
  {
    id: 'FLEETHER',
    name: 'FleetHer',
    seats: '4 places',
    eta: '5 min',
    multiplier: 1.18,
    description: 'Service réservé aux chauffeurs femmes éligibles.',
  },
  {
    id: 'FLEET_PMR',
    name: 'Fleet PMR',
    seats: 'Véhicule adapté',
    eta: '8 min',
    multiplier: 1.35,
    description: 'Service avec véhicule adapté aux personnes à mobilité réduite.',
  },
  {
    id: 'FLEET_LUXE',
    name: 'FleetLuxe',
    seats: 'Berline premium',
    eta: '7 min',
    multiplier: 1.65,
    description: 'Service premium avec chauffeur et véhicule haut de gamme.',
  },
];
