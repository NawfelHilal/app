import { create } from 'zustand';
import { jwtDecode } from 'jwt-decode';
import { api, UserRole } from '../api/client';
import { connectGps, disconnectGps } from '../api/gps';

type AuthState = {
  accessToken?: string;
  refreshToken?: string;
  role?: UserRole;
  username: string;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

function decodeRole(token: string): UserRole {
  const payload = jwtDecode<{ role?: UserRole }>(token);
  return payload.role || 'PASSENGER';
}

export const useAuthStore = create<AuthState>((set) => ({
  username: '',
  login: async (username, password) => {
    const response = await api.post('/auth/token/', { username, password });
    const access = response.data.access as string;
    const refresh = response.data.refresh as string;
    connectGps(access);
    set({
      username,
      accessToken: access,
      refreshToken: refresh,
      role: decodeRole(access),
    });
  },
  logout: () => {
    disconnectGps();
    set({ accessToken: undefined, refreshToken: undefined, role: undefined, username: '' });
  },
}));
