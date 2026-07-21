const redisMock = {
  multi: jest.fn(),
  geosearch: jest.fn(),
  mget: jest.fn(),
  quit: jest.fn(),
};

const multiMock = {
  geoadd: jest.fn(),
  set: jest.fn(),
  exec: jest.fn(),
};

const mockRedisConstructor = jest.fn(() => redisMock);

jest.mock('ioredis', () => ({
  __esModule: true,
  default: mockRedisConstructor,
}));

import { RedisGpsStore } from './redis-gps.store';

describe('RedisGpsStore', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    process.env.GPS_POSITION_TTL_SECONDS = '60';
    redisMock.multi.mockReturnValue(multiMock);
    multiMock.geoadd.mockReturnValue(multiMock);
    multiMock.set.mockReturnValue(multiMock);
    multiMock.exec.mockResolvedValue([]);
  });

  it('saves driver position in GEO index and TTL payload', async () => {
    const position = {
      driverId: '42',
      latitude: 48.8566,
      longitude: 2.3522,
      recordedAt: '2026-07-21T12:00:00.000Z',
    };

    const saved = await new RedisGpsStore().save(position);

    expect(saved).toBe(position);
    expect(multiMock.geoadd).toHaveBeenCalledWith('fleetpro:gps:drivers', 2.3522, 48.8566, '42');
    expect(multiMock.set).toHaveBeenCalledWith(
      'fleetpro:gps:driver:42',
      JSON.stringify(position),
      'EX',
      60,
    );
    expect(multiMock.exec).toHaveBeenCalled();
  });

  it('returns only drivers with non-expired payloads', async () => {
    redisMock.geosearch.mockResolvedValue(['42', '7']);
    redisMock.mget.mockResolvedValue([
      JSON.stringify({ driverId: '42', latitude: 48.8566, longitude: 2.3522, recordedAt: 'now' }),
      null,
    ]);

    const drivers = await new RedisGpsStore().findNearby(48.8, 2.3, 5);

    expect(redisMock.geosearch).toHaveBeenCalledWith(
      'fleetpro:gps:drivers',
      'FROMLONLAT',
      2.3,
      48.8,
      'BYRADIUS',
      5,
      'km',
    );
    expect(drivers).toEqual([{ driverId: '42', latitude: 48.8566, longitude: 2.3522, recordedAt: 'now' }]);
  });

  it('quits redis connection on module destroy', async () => {
    redisMock.quit.mockResolvedValue('OK');

    await new RedisGpsStore().onModuleDestroy();

    expect(redisMock.quit).toHaveBeenCalled();
  });
});
