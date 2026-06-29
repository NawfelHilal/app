import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { GpsGateway } from './gps.gateway';
import { RedisGpsStore } from './redis-gps.store';
import { RideAccessService } from './ride-access.service';
import { SocketAuthService } from './socket-auth.service';

@Module({
  controllers: [AppController],
  providers: [GpsGateway, RedisGpsStore, RideAccessService, SocketAuthService],
})
export class AppModule {}
