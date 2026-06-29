import { io, Socket } from 'socket.io-client';

const gpsUrl = process.env.EXPO_PUBLIC_GPS_URL || 'http://localhost:8080';

let socket: Socket | undefined;

export type DriverPosition = {
  driverId: string;
  latitude: number;
  longitude: number;
  heading?: number;
  speed?: number;
  recordedAt: string;
  rideId?: number;
};

export function connectGps(accessToken: string): Socket {
  socket = io(gpsUrl, {
    transports: ['websocket'],
    auth: { token: accessToken },
  });
  return socket;
}

export function getGpsSocket(): Socket | undefined {
  return socket;
}

export function disconnectGps() {
  socket?.disconnect();
  socket = undefined;
}
