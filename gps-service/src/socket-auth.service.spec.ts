import { sign } from 'jsonwebtoken';
import { SocketAuthService } from './socket-auth.service';

describe('SocketAuthService', () => {
  beforeEach(() => {
    process.env.GPS_JWT_SECRET = 'test-secret';
  });

  afterEach(() => {
    delete process.env.GPS_JWT_SECRET;
    delete process.env.JWT_SIGNING_KEY;
  });

  it('authenticates a Django SimpleJWT compatible payload', () => {
    const token = sign({ user_id: 42, role: 'DRIVER' }, 'test-secret');
    const socket = {
      handshake: {
        auth: { token },
        headers: {},
      },
    };

    const user = new SocketAuthService().authenticate(socket as any);

    expect(user).toEqual({ id: '42', role: 'DRIVER' });
  });

  it('extracts bearer token from authorization header', () => {
    const token = sign({ sub: '7', user_role: 'PASSENGER' }, 'test-secret');
    const socket = {
      handshake: {
        auth: {},
        headers: { authorization: `Bearer ${token}` },
      },
    };

    const user = new SocketAuthService().authenticate(socket as any);

    expect(user).toEqual({ id: '7', role: 'PASSENGER' });
  });

  it('rejects sockets without token or configured secret', () => {
    delete process.env.GPS_JWT_SECRET;
    const socket = {
      handshake: {
        auth: {},
        headers: {},
      },
    };

    expect(() => new SocketAuthService().authenticate(socket as any)).toThrow('Missing socket token');
  });

  it('rejects tokens without user id', () => {
    const token = sign({ role: 'DRIVER' }, 'test-secret');
    const socket = {
      handshake: {
        auth: { token },
        headers: {},
      },
    };

    expect(() => new SocketAuthService().authenticate(socket as any)).toThrow('Invalid token payload');
  });
});
