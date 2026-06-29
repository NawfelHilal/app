import { create } from 'zustand';
import { jwtDecode } from 'jwt-decode';
import * as SecureStore from 'expo-secure-store';
import { api, UserRole } from '../api/client';
import { connectGps, disconnectGps } from '../api/gps';
import { registerPushToken } from '../api/notifications';

type AuthState = {
  accessToken?: string;
  refreshToken?: string;
  role?: UserRole;
  username: string;
  initialized: boolean;
  initialize: () => Promise<void>;
  login: (username: string, password: string) => Promise<void>;
  refreshAccessToken: () => Promise<string>;
  logout: () => Promise<void>;
};

function decodeSession(token: string): { role: UserRole; username: string } {
  const payload = jwtDecode<{ role?: UserRole; username?: string }>(token);
  return { role: payload.role || 'PASSENGER', username: payload.username || '' };
}

async function persistSession(accessToken: string, refreshToken: string) {
  await SecureStore.setItemAsync('fleetpro_access_token', accessToken);
  await SecureStore.setItemAsync('fleetpro_refresh_token', refreshToken);
}

export const useAuthStore = create<AuthState>((set, get) => ({
  username: '',
  initialized: false,
  initialize: async () => {
    const refreshToken = await SecureStore.getItemAsync('fleetpro_refresh_token');
    if (!refreshToken) {
      set({ initialized: true });
      return;
    }
    set({ refreshToken });
    try {
      await get().refreshAccessToken();
    } catch {
      await get().logout();
    } finally {
      set({ initialized: true });
    }
  },
  login: async (username, password) => {
    const response = await api.post('/auth/token/', { username, password });
    const access = response.data.access as string;
    const refresh = response.data.refresh as string;
    const session = decodeSession(access);
    await persistSession(access, refresh);
    connectGps(access);
    set({
      username: session.username || username,
      accessToken: access,
      refreshToken: refresh,
      role: session.role,
    });
    registerPushToken().catch(() => undefined);
  },
  refreshAccessToken: async () => {
    const refreshToken = get().refreshToken;
    if (!refreshToken) {
      throw new Error('Missing refresh token.');
    }
    const response = await api.post('/auth/token/refresh/', { refresh: refreshToken });
    const accessToken = response.data.access as string;
    const nextRefreshToken = (response.data.refresh as string | undefined) || refreshToken;
    const session = decodeSession(accessToken);
    await persistSession(accessToken, nextRefreshToken);
    disconnectGps();
    connectGps(accessToken);
    set({ accessToken, refreshToken: nextRefreshToken, role: session.role, username: session.username });
    return accessToken;
  },
  logout: async () => {
    disconnectGps();
    set({ accessToken: undefined, refreshToken: undefined, role: undefined, username: '' });
    await SecureStore.deleteItemAsync('fleetpro_access_token');
    await SecureStore.deleteItemAsync('fleetpro_refresh_token');
  },
}));
