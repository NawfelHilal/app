import {
  ConnectedSocket,
  MessageBody,
  OnGatewayConnection,
  SubscribeMessage,
  WebSocketGateway,
  WebSocketServer,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { RedisGpsStore } from './redis-gps.store';
import { RideAccessService } from './ride-access.service';
import { SocketAuthService } from './socket-auth.service';

type PositionPayload = {
  latitude: number;
  longitude: number;
  heading?: number;
  speed?: number;
  rideId?: number;
};

type RideRoomPayload = { rideId: number };

type NearbyPayload = {
  latitude: number;
  longitude: number;
  radiusKm?: number;
};

@WebSocketGateway({
  cors: { origin: true, credentials: true },
})
export class GpsGateway implements OnGatewayConnection {
  @WebSocketServer()
  server!: Server;

  constructor(
    private readonly store: RedisGpsStore,
    private readonly auth: SocketAuthService,
    private readonly rideAccess: RideAccessService,
  ) {}

  handleConnection(socket: Socket) {
    try {
      const user = this.auth.authenticate(socket);
      socket.data.user = user;
      socket.data.accessToken = this.auth.getToken(socket);
      socket.data.rideIds = new Set<number>();
      socket.join(`user:${user.id}`);
      socket.emit('gps:ready', { userId: user.id, role: user.role });
    } catch {
      socket.emit('gps:error', { message: 'Unauthorized socket.' });
      socket.disconnect(true);
    }
  }

  @SubscribeMessage('ride:join')
  async joinRide(@ConnectedSocket() socket: Socket, @MessageBody() payload: RideRoomPayload) {
    const rideId = Number(payload?.rideId);
    const user = socket.data.user;
    const token = socket.data.accessToken;
    if (!user || !token || !Number.isInteger(rideId) || rideId <= 0) {
      return { ok: false, error: 'Invalid ride room request.' };
    }
    if (!(await this.rideAccess.canJoin(user, token, rideId))) {
      return { ok: false, error: 'Ride access denied.' };
    }
    socket.data.rideIds.add(rideId);
    await socket.join(`ride:${rideId}`);
    return { ok: true, rideId };
  }

  @SubscribeMessage('driver:position')
  async updateDriverPosition(@ConnectedSocket() socket: Socket, @MessageBody() payload: PositionPayload) {
    const user = socket.data.user;
    if (!user || user.role !== 'DRIVER') {
      return { ok: false, error: 'Only drivers can publish positions.' };
    }
    if (!isValidCoordinate(payload?.latitude, payload?.longitude)) {
      return { ok: false, error: 'Invalid GPS coordinates.' };
    }

    const position = await this.store.save({
      driverId: user.id,
      latitude: payload.latitude,
      longitude: payload.longitude,
      heading: payload.heading,
      speed: payload.speed,
      recordedAt: new Date().toISOString(),
    });

    const rideId = Number(payload.rideId);
    if (Number.isInteger(rideId) && socket.data.rideIds.has(rideId)) {
      this.server.to(`ride:${rideId}`).emit('driver:position:updated', { ...position, rideId });
    }
    return { ok: true, position };
  }

  @SubscribeMessage('drivers:nearby')
  async findNearby(@MessageBody() payload: NearbyPayload) {
    if (!isValidCoordinate(payload?.latitude, payload?.longitude)) {
      return { ok: false, error: 'Invalid GPS coordinates.' };
    }
    const radiusKm = Math.min(Math.max(Number(payload.radiusKm) || 5, 0.1), 25);
    const drivers = await this.store.findNearby(payload.latitude, payload.longitude, radiusKm);
    return { ok: true, drivers };
  }
}

function isValidCoordinate(latitude: number, longitude: number): boolean {
  return Number.isFinite(latitude) && Number.isFinite(longitude) && latitude >= -90 && latitude <= 90 && longitude >= -180 && longitude <= 180;
}
