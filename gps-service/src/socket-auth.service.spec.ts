import { sign } from 'jsonwebtoken';
import { SocketAuthService } from './socket-auth.service';

describe('SocketAuthService', () => {
  beforeEach(() => {
    process.env.GPS_JWT_SECRET = 'test-secret';
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
});

