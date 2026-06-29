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
});
