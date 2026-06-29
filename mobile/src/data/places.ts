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
    id: 'home',
    label: 'Maison',
    address: 'Rue de Rivoli, Paris',
    latitude: 48.8566,
    longitude: 2.3522,
    distanceKm: '4.80',
    durationMinutes: 16,
  },
  {
    id: 'station',
    label: 'Gare de Lyon',
    address: 'Place Louis-Armand, Paris',
    latitude: 48.8443,
    longitude: 2.373,
    distanceKm: '6.20',
    durationMinutes: 18,
  },
  {
    id: 'airport',
    label: 'Orly',
    address: 'Aeroport Paris-Orly',
    latitude: 48.7262,
    longitude: 2.3652,
    distanceKm: '18.40',
    durationMinutes: 32,
  },
];

export const rideOptions = [
  {
    id: 'eco',
    name: 'Fleet Eco',
    seats: '4 places',
    eta: '3 min',
    multiplier: 1,
  },
  {
    id: 'comfort',
    name: 'Fleet Comfort',
    seats: '4 places',
    eta: '5 min',
    multiplier: 1.22,
  },
  {
    id: 'van',
    name: 'Fleet Van',
    seats: '6 places',
    eta: '8 min',
    multiplier: 1.48,
  },
];

