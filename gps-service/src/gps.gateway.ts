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
import { SocketAuthService } from './socket-auth.service';

type PositionPayload = {
  latitude: number;
  longitude: number;
  heading?: number;
  speed?: number;
};

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
  ) {}

  handleConnection(socket: Socket) {
    try {
      const user = this.auth.authenticate(socket);
      socket.data.user = user;
      socket.join(`user:${user.id}`);
      socket.emit('gps:ready', { userId: user.id, role: user.role });
    } catch (error) {
      socket.emit('gps:error', { message: 'Unauthorized socket.' });
      socket.disconnect(true);
    }
  }

  @SubscribeMessage('driver:position')
  async updateDriverPosition(@ConnectedSocket() socket: Socket, @MessageBody() payload: PositionPayload) {
    const user = socket.data.user;
    if (!user || user.role !== 'DRIVER') {
      return { ok: false, error: 'Only drivers can publish positions.' };
    }

    const position = await this.store.save({
      driverId: user.id,
      latitude: payload.latitude,
      longitude: payload.longitude,
      heading: payload.heading,
      speed: payload.speed,
      recordedAt: new Date().toISOString(),
    });

    this.server.emit('driver:position:updated', position);
    return { ok: true, position };
  }

  @SubscribeMessage('drivers:nearby')
  async findNearby(@MessageBody() payload: NearbyPayload) {
    const drivers = await this.store.findNearby(payload.latitude, payload.longitude, payload.radiusKm || 5);
    return { ok: true, drivers };
  }
}

