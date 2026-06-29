import { create } from 'zustand';
import { api, Ride } from '../api/client';

export type RideDraft = {
  pickup_label: string;
  pickup_latitude: number;
  pickup_longitude: number;
  dropoff_label: string;
  dropoff_latitude: number;
  dropoff_longitude: number;
  distance_km: string;
  duration_minutes: number;
};

export type RidePlan = RideDraft & {
  dropoffId: string;
  serviceId: string;
  serviceName: string;
  estimatedFareCents: number;
  eta: string;
};

type RideState = {
  rides: Ride[];
  currentPlan?: RidePlan;
  loading: boolean;
  loadRides: () => Promise<void>;
  refreshRide: (rideId: number) => Promise<Ride>;
  setCurrentPlan: (plan: RidePlan) => void;
  requestRide: (draft: RideDraft) => Promise<Ride>;
  createPaymentIntent: (rideId: number) => Promise<string>;
  cancelRide: (rideId: number) => Promise<Ride>;
  acceptRide: (rideId: number) => Promise<Ride>;
  startRide: (rideId: number) => Promise<Ride>;
  completeRide: (rideId: number) => Promise<Ride>;
  simulateRide: (rideId: number) => Promise<Ride>;
};

function replaceRide(rides: Ride[], updatedRide: Ride): Ride[] {
  const exists = rides.some((ride) => ride.id === updatedRide.id);
  if (!exists) {
    return [updatedRide, ...rides];
  }
  return rides.map((ride) => (ride.id === updatedRide.id ? updatedRide : ride));
}

export const useRideStore = create<RideState>((set, get) => ({
  rides: [],
  currentPlan: undefined,
  loading: false,
  loadRides: async () => {
    set({ loading: true });
    try {
      const response = await api.get('/rides/');
      set({ rides: response.data });
    } finally {
      set({ loading: false });
    }
  },
  refreshRide: async (rideId) => {
    const response = await api.get(`/rides/${rideId}/`);
    const ride = response.data as Ride;
    set({ rides: replaceRide(get().rides, ride) });
    return ride;
  },
  setCurrentPlan: (plan) => set({ currentPlan: plan }),
  requestRide: async (draft) => {
    const response = await api.post('/rides/', draft);
    const ride = response.data as Ride;
    set({ rides: [ride, ...get().rides] });
    return ride;
  },
  createPaymentIntent: async (rideId) => {
    const response = await api.post('/payments/create-intent/', { ride_id: rideId });
    return response.data.client_secret as string;
  },
  cancelRide: async (rideId) => {
    const response = await api.post(`/rides/${rideId}/cancel/`);
    const ride = response.data as Ride;
    set({ rides: replaceRide(get().rides, ride) });
    return ride;
  },
  acceptRide: async (rideId) => {
    const response = await api.post(`/rides/${rideId}/accept/`);
    const ride = response.data as Ride;
    set({ rides: replaceRide(get().rides, ride) });
    return ride;
  },
  startRide: async (rideId) => {
    const response = await api.post(`/rides/${rideId}/start/`);
    const ride = response.data as Ride;
    set({ rides: replaceRide(get().rides, ride) });
    return ride;
  },
  completeRide: async (rideId) => {
    const response = await api.post(`/rides/${rideId}/complete/`);
    const ride = response.data as Ride;
    set({ rides: replaceRide(get().rides, ride) });
    return ride;
  },
  simulateRide: async (rideId) => {
    const response = await api.post(`/rides/${rideId}/simulate/`);
    const ride = response.data as Ride;
    set({ rides: replaceRide(get().rides, ride) });
    return ride;
  },
}));
