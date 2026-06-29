import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtPayload, verify } from 'jsonwebtoken';
import { Socket } from 'socket.io';

export type AuthenticatedUser = {
  id: string;
  role: 'PASSENGER' | 'DRIVER' | 'ADMIN';
};

@Injectable()
export class SocketAuthService {
  authenticate(socket: Socket): AuthenticatedUser {
    const token = this.getToken(socket);
    const secret = process.env.GPS_JWT_SECRET || process.env.JWT_SIGNING_KEY;

    if (!token || !secret) {
      throw new UnauthorizedException('Missing socket token or GPS_JWT_SECRET.');
    }

    const payload = verify(token, secret) as JwtPayload;
    const id = String(payload.user_id || payload.sub || '');
    const role = String(payload.role || payload.user_role || 'PASSENGER') as AuthenticatedUser['role'];

    if (!id) {
      throw new UnauthorizedException('Invalid token payload.');
    }

    return { id, role };
  }

  getToken(socket: Socket): string | undefined {
    return this.extractToken(socket);
  }

  private extractToken(socket: Socket): string | undefined {
    const authToken = socket.handshake.auth?.token;
    if (typeof authToken === 'string') {
      return authToken;
    }

    const header = socket.handshake.headers.authorization;
    if (header?.startsWith('Bearer ')) {
      return header.slice('Bearer '.length);
    }

    return undefined;
  }
}
