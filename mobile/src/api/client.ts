import axios from 'axios';
import { useAuthStore } from '../store/auth';

export const apiUrl = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

export const api = axios.create({
  baseURL: apiUrl,
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(undefined, async (error) => {
  const request = error.config as (typeof error.config & { _retry?: boolean });
  if (error.response?.status !== 401 || request?._retry || request?.url?.includes('/auth/token/')) {
    return Promise.reject(error);
  }
  request._retry = true;
  const accessToken = await useAuthStore.getState().refreshAccessToken();
  request.headers.Authorization = `Bearer ${accessToken}`;
  return api(request);
});

export type UserRole = 'PASSENGER' | 'DRIVER' | 'ADMIN';

export type Ride = {
  id: number;
  status: 'REQUESTED' | 'ACCEPTED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELED';
  service_type: 'STANDARD' | 'FLEETHER' | 'FLEET_PMR';
  pickup_label: string;
  pickup_latitude?: string;
  pickup_longitude?: string;
  dropoff_label: string;
  dropoff_latitude?: string;
  dropoff_longitude?: string;
  passenger_note?: string;
  cancellation_reason?: string;
  distance_km?: string;
  duration_minutes?: number;
  estimated_fare_cents: number;
  final_fare_cents?: number | null;
  commission_cents: number;
  driver_earnings_cents: number;
  payment_status?: 'REQUIRES_PAYMENT_METHOD' | 'REQUIRES_CONFIRMATION' | 'REQUIRES_ACTION' | 'REQUIRES_CAPTURE' | 'PROCESSING' | 'SUCCEEDED' | 'CANCELED' | 'FAILED' | null;
  requested_at?: string;
};
