import { Injectable } from '@nestjs/common';
import { AuthenticatedUser } from './socket-auth.service';

type RideAccess = {
  passenger: number;
  driver: number | null;
};

@Injectable()
export class RideAccessService {
  async canJoin(user: AuthenticatedUser, token: string, rideId: number): Promise<boolean> {
    const apiUrl = process.env.CORE_API_URL || 'http://backend:8000/api/v1';
    try {
      const response = await fetch(`${apiUrl}/rides/${rideId}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) {
        return false;
      }
      const ride = (await response.json()) as RideAccess;
      if (user.role === 'DRIVER') {
        return String(ride.driver || '') === user.id;
      }
      if (user.role === 'PASSENGER') {
        return String(ride.passenger) === user.id;
      }
      return user.role === 'ADMIN';
    } catch {
      return false;
    }
  }
}
