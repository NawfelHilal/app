import { Injectable, OnModuleDestroy } from '@nestjs/common';
import Redis from 'ioredis';

export type DriverPosition = {
  driverId: string;
  latitude: number;
  longitude: number;
  heading?: number;
  speed?: number;
  recordedAt: string;
};

@Injectable()
export class RedisGpsStore implements OnModuleDestroy {
  private readonly redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379/0');
  private readonly ttlSeconds = Number(process.env.GPS_POSITION_TTL_SECONDS || 45);
  private readonly geoKey = 'fleetpro:gps:drivers';

  async save(position: DriverPosition): Promise<DriverPosition> {
    const key = this.positionKey(position.driverId);
    await this.redis
      .multi()
      .geoadd(this.geoKey, position.longitude, position.latitude, position.driverId)
      .set(key, JSON.stringify(position), 'EX', this.ttlSeconds)
      .exec();
    return position;
  }

  async findNearby(latitude: number, longitude: number, radiusKm = 5): Promise<DriverPosition[]> {
    const raw = (await (this.redis as any).geosearch(
      this.geoKey,
      'FROMLONLAT',
      longitude,
      latitude,
      'BYRADIUS',
      radiusKm,
      'km',
    )) as string[];

    if (!raw.length) {
      return [];
    }

    const positions = await this.redis.mget(raw.map((driverId) => this.positionKey(driverId)));
    return positions
      .filter((payload): payload is string => Boolean(payload))
      .map((payload) => JSON.parse(payload) as DriverPosition);
  }

  async onModuleDestroy() {
    await this.redis.quit();
  }

  private positionKey(driverId: string): string {
    return `fleetpro:gps:driver:${driverId}`;
  }
}
