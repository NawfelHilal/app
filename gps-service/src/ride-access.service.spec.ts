import { RideAccessService } from './ride-access.service';

describe('RideAccessService', () => {
  afterEach(() => jest.restoreAllMocks());

  it('allows only the driver assigned to a ride', async () => {
    jest.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ passenger: 4, driver: 42 }),
    } as Response);

    const allowed = await new RideAccessService().canJoin({ id: '42', role: 'DRIVER' }, 'token', 8);
    const denied = await new RideAccessService().canJoin({ id: '7', role: 'DRIVER' }, 'token', 8);

    expect(allowed).toBe(true);
    expect(denied).toBe(false);
  });

  it('allows only the passenger assigned to a ride', async () => {
    jest.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ passenger: 4, driver: 42 }),
    } as Response);

    const allowed = await new RideAccessService().canJoin({ id: '4', role: 'PASSENGER' }, 'token', 8);
    const denied = await new RideAccessService().canJoin({ id: '5', role: 'PASSENGER' }, 'token', 8);

    expect(allowed).toBe(true);
    expect(denied).toBe(false);
  });

  it('allows admins to join existing rides', async () => {
    jest.spyOn(global, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ passenger: 4, driver: null }),
    } as Response);

    const allowed = await new RideAccessService().canJoin({ id: '1', role: 'ADMIN' }, 'token', 8);

    expect(allowed).toBe(true);
  });

  it('denies access when core API rejects or is unreachable', async () => {
    const fetchSpy = jest.spyOn(global, 'fetch');
    fetchSpy.mockResolvedValueOnce({ ok: false } as Response);
    fetchSpy.mockRejectedValueOnce(new Error('network'));

    const rejected = await new RideAccessService().canJoin({ id: '4', role: 'PASSENGER' }, 'token', 8);
    const unreachable = await new RideAccessService().canJoin({ id: '4', role: 'PASSENGER' }, 'token', 8);

    expect(rejected).toBe(false);
    expect(unreachable).toBe(false);
  });
});
