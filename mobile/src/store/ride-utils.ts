import type { Ride } from '../api/client';

export function replaceRide(rides: Ride[], updatedRide: Ride): Ride[] {
  const exists = rides.some((ride) => ride.id === updatedRide.id);
  if (!exists) {
    return [updatedRide, ...rides];
  }
  return rides.map((ride) => (ride.id === updatedRide.id ? updatedRide : ride));
}
