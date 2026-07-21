import { GpsGateway } from './gps.gateway';

describe('GpsGateway', () => {
  const store = {
    save: jest.fn(),
    findNearby: jest.fn(),
  };
  const auth = {
    authenticate: jest.fn(),
    getToken: jest.fn(),
  };
  const rideAccess = {
    canJoin: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  function gateway() {
    const instance = new GpsGateway(store as any, auth as any, rideAccess as any);
    instance.server = { to: jest.fn(() => ({ emit: jest.fn() })) } as any;
    return instance;
  }

  it('authenticates sockets and joins the user room', () => {
    auth.authenticate.mockReturnValue({ id: '42', role: 'DRIVER' });
    auth.getToken.mockReturnValue('access-token');
    const socket: any = {
      data: {},
      join: jest.fn(),
      emit: jest.fn(),
      disconnect: jest.fn(),
    };

    gateway().handleConnection(socket as any);

    expect(socket.data.user).toEqual({ id: '42', role: 'DRIVER' });
    expect(socket.data.accessToken).toBe('access-token');
    expect(socket.join).toHaveBeenCalledWith('user:42');
    expect(socket.emit).toHaveBeenCalledWith('gps:ready', { userId: '42', role: 'DRIVER' });
  });

  it('disconnects unauthorized sockets', () => {
    auth.authenticate.mockImplementation(() => {
      throw new Error('bad token');
    });
    const socket: any = {
      data: {},
      join: jest.fn(),
      emit: jest.fn(),
      disconnect: jest.fn(),
    };

    gateway().handleConnection(socket as any);

    expect(socket.emit).toHaveBeenCalledWith('gps:error', { message: 'Unauthorized socket.' });
    expect(socket.disconnect).toHaveBeenCalledWith(true);
  });

  it('rejects passenger position publishing', async () => {
    const socket = { data: { user: { id: '7', role: 'PASSENGER' }, rideIds: new Set<number>() } };

    const result = await gateway().updateDriverPosition(socket as any, { latitude: 48.8, longitude: 2.3 });

    expect(result).toEqual({ ok: false, error: 'Only drivers can publish positions.' });
    expect(store.save).not.toHaveBeenCalled();
  });

  it('rejects invalid driver coordinates', async () => {
    const socket = { data: { user: { id: '42', role: 'DRIVER' }, rideIds: new Set<number>() } };

    const result = await gateway().updateDriverPosition(socket as any, { latitude: 120, longitude: 2.3 });

    expect(result).toEqual({ ok: false, error: 'Invalid GPS coordinates.' });
    expect(store.save).not.toHaveBeenCalled();
  });

  it('saves valid driver position and emits to joined ride room', async () => {
    const position = {
      driverId: '42',
      latitude: 48.8,
      longitude: 2.3,
      recordedAt: '2026-07-21T00:00:00.000Z',
    };
    store.save.mockResolvedValue(position);
    const emit = jest.fn();
    const instance = gateway();
    instance.server = { to: jest.fn(() => ({ emit })) } as any;
    const socket = { data: { user: { id: '42', role: 'DRIVER' }, rideIds: new Set([9]) } };

    const result = await instance.updateDriverPosition(socket as any, { latitude: 48.8, longitude: 2.3, rideId: 9 });

    expect(result).toEqual({ ok: true, position });
    expect(store.save).toHaveBeenCalledWith(
      expect.objectContaining({ driverId: '42', latitude: 48.8, longitude: 2.3 }),
    );
    expect(instance.server.to).toHaveBeenCalledWith('ride:9');
    expect(emit).toHaveBeenCalledWith('driver:position:updated', { ...position, rideId: 9 });
  });

  it('clamps nearby radius between configured bounds', async () => {
    store.findNearby.mockResolvedValue([]);

    const result = await gateway().findNearby({ latitude: 48.8, longitude: 2.3, radiusKm: 999 });

    expect(result).toEqual({ ok: true, drivers: [] });
    expect(store.findNearby).toHaveBeenCalledWith(48.8, 2.3, 25);
  });

  it('joins ride rooms after core access validation', async () => {
    rideAccess.canJoin.mockResolvedValue(true);
    const socket = {
      data: { user: { id: '42', role: 'DRIVER' }, accessToken: 'token', rideIds: new Set<number>() },
      join: jest.fn(),
    };

    const result = await gateway().joinRide(socket as any, { rideId: 9 });

    expect(result).toEqual({ ok: true, rideId: 9 });
    expect(rideAccess.canJoin).toHaveBeenCalledWith({ id: '42', role: 'DRIVER' }, 'token', 9);
    expect(socket.data.rideIds.has(9)).toBe(true);
    expect(socket.join).toHaveBeenCalledWith('ride:9');
  });

  it('rejects invalid and denied ride room joins', async () => {
    rideAccess.canJoin.mockResolvedValue(false);
    const socket = {
      data: { user: { id: '42', role: 'DRIVER' }, accessToken: 'token', rideIds: new Set<number>() },
      join: jest.fn(),
    };

    const invalid = await gateway().joinRide(socket as any, { rideId: -1 });
    const denied = await gateway().joinRide(socket as any, { rideId: 9 });

    expect(invalid).toEqual({ ok: false, error: 'Invalid ride room request.' });
    expect(denied).toEqual({ ok: false, error: 'Ride access denied.' });
    expect(socket.join).not.toHaveBeenCalled();
  });

  it('rejects invalid nearby coordinates', async () => {
    const result = await gateway().findNearby({ latitude: 120, longitude: 2.3 });

    expect(result).toEqual({ ok: false, error: 'Invalid GPS coordinates.' });
  });
});
