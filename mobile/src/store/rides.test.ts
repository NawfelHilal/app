import { api, Ride } from '../api/client';
import { useRideStore } from './rides';

jest.mock('../api/client', () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

const mockedApi = api as jest.Mocked<typeof api>;

function ride(id: number, status: Ride['status'] = 'REQUESTED'): Ride {
  return {
    id,
    status,
    service_type: 'STANDARD',
    pickup_label: 'Paris',
    dropoff_label: 'Tour Eiffel',
    estimated_fare_cents: 2500,
    commission_cents: 375,
    driver_earnings_cents: 2125,
  };
}

describe('useRideStore', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useRideStore.setState({ rides: [], currentPlan: undefined, loading: false });
  });

  it('loads rides and toggles loading state', async () => {
    mockedApi.get.mockResolvedValue({ data: [ride(1), ride(2)] });

    await useRideStore.getState().loadRides();

    expect(mockedApi.get).toHaveBeenCalledWith('/rides/');
    expect(useRideStore.getState().rides.map((item) => item.id)).toEqual([1, 2]);
    expect(useRideStore.getState().loading).toBe(false);
  });

  it('creates a ride and prepends it to store state', async () => {
    mockedApi.post.mockResolvedValue({ data: ride(3) });
    const draft = {
      pickup_label: 'Paris',
      service_type: 'STANDARD' as const,
      pickup_latitude: 48.8566,
      pickup_longitude: 2.3522,
      dropoff_label: 'Tour Eiffel',
      dropoff_latitude: 48.8584,
      dropoff_longitude: 2.2945,
      distance_km: '10.00',
      duration_minutes: 20,
    };

    const created = await useRideStore.getState().requestRide(draft);

    expect(mockedApi.post).toHaveBeenCalledWith('/rides/', draft);
    expect(created.id).toBe(3);
    expect(useRideStore.getState().rides.map((item) => item.id)).toEqual([3]);
  });

  it('refreshes one ride and stores current plan', async () => {
    useRideStore.setState({ rides: [ride(7)] as any });
    mockedApi.get.mockResolvedValue({ data: ride(7, 'ACCEPTED') });
    const plan = {
      pickup_label: 'Paris',
      service_type: 'STANDARD' as const,
      pickup_latitude: 48.8566,
      pickup_longitude: 2.3522,
      dropoff_label: 'Tour Eiffel',
      dropoff_latitude: 48.8584,
      dropoff_longitude: 2.2945,
      distance_km: '10.00',
      duration_minutes: 20,
      dropoffId: 'eiffel',
      serviceId: 'STANDARD',
      serviceName: 'Fleet Standard',
      estimatedFareCents: 2500,
      eta: '3 min',
    };

    useRideStore.getState().setCurrentPlan(plan);
    const refreshed = await useRideStore.getState().refreshRide(7);

    expect(mockedApi.get).toHaveBeenCalledWith('/rides/7/');
    expect(refreshed.status).toBe('ACCEPTED');
    expect(useRideStore.getState().rides[0].status).toBe('ACCEPTED');
    expect(useRideStore.getState().currentPlan).toEqual(plan);
  });

  it('updates rides through lifecycle actions', async () => {
    useRideStore.setState({ rides: [ride(4)] as any });
    mockedApi.post
      .mockResolvedValueOnce({ data: ride(4, 'ACCEPTED') })
      .mockResolvedValueOnce({ data: ride(4, 'IN_PROGRESS') })
      .mockResolvedValueOnce({ data: ride(4, 'COMPLETED') })
      .mockResolvedValueOnce({ data: ride(4, 'CANCELED') });

    await useRideStore.getState().acceptRide(4);
    await useRideStore.getState().startRide(4);
    await useRideStore.getState().completeRide(4);
    const canceled = await useRideStore.getState().cancelRide(4, 'Test');

    expect(mockedApi.post).toHaveBeenNthCalledWith(1, '/rides/4/accept/');
    expect(mockedApi.post).toHaveBeenNthCalledWith(2, '/rides/4/start/');
    expect(mockedApi.post).toHaveBeenNthCalledWith(3, '/rides/4/complete/');
    expect(mockedApi.post).toHaveBeenNthCalledWith(4, '/rides/4/cancel/', { reason: 'Test' });
    expect(canceled.status).toBe('CANCELED');
    expect(useRideStore.getState().rides[0].status).toBe('CANCELED');
  });

  it('handles payment and simulation endpoints', async () => {
    mockedApi.post
      .mockResolvedValueOnce({ data: { client_secret: 'client-secret' } })
      .mockResolvedValueOnce({ data: {} })
      .mockResolvedValueOnce({ data: ride(5, 'ACCEPTED') })
      .mockResolvedValueOnce({ data: ride(6, 'REQUESTED') });

    const clientSecret = await useRideStore.getState().createPaymentIntent(5);
    await useRideStore.getState().simulatePaymentIntent(5);
    const simulated = await useRideStore.getState().simulateRide(5);
    const nearby = await useRideStore.getState().simulateNearbyRequest();

    expect(clientSecret).toBe('client-secret');
    expect(mockedApi.post).toHaveBeenNthCalledWith(1, '/payments/create-intent/', { ride_id: 5 });
    expect(mockedApi.post).toHaveBeenNthCalledWith(2, '/payments/simulate-intent/', { ride_id: 5 });
    expect(mockedApi.post).toHaveBeenNthCalledWith(3, '/rides/5/simulate/');
    expect(mockedApi.post).toHaveBeenNthCalledWith(4, '/rides/simulate-nearby-request/');
    expect(simulated.status).toBe('ACCEPTED');
    expect(nearby.id).toBe(6);
  });
});
