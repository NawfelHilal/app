import * as SecureStore from 'expo-secure-store';
import { api } from '../api/client';
import { connectGps, disconnectGps } from '../api/gps';
import { registerPushToken } from '../api/notifications';
import { useAuthStore } from './auth';

jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn(),
  setItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));

jest.mock('../api/client', () => ({
  api: {
    post: jest.fn(),
  },
}));

jest.mock('../api/gps', () => ({
  connectGps: jest.fn(),
  disconnectGps: jest.fn(),
}));

jest.mock('../api/notifications', () => ({
  registerPushToken: jest.fn(),
}));

jest.mock('jwt-decode', () => ({
  jwtDecode: jest.fn((token: string) => {
    if (token.includes('driver')) {
      return { role: 'DRIVER', username: 'driver' };
    }
    return { role: 'PASSENGER', username: 'passenger' };
  }),
}));

const mockedApi = api as jest.Mocked<typeof api>;
const mockedSecureStore = SecureStore as jest.Mocked<typeof SecureStore>;

describe('useAuthStore', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useAuthStore.setState({
      accessToken: undefined,
      refreshToken: undefined,
      role: undefined,
      username: '',
      initialized: false,
    });
    mockedSecureStore.getItemAsync.mockResolvedValue(null);
    mockedSecureStore.setItemAsync.mockResolvedValue(undefined);
    mockedSecureStore.deleteItemAsync.mockResolvedValue(undefined);
    (registerPushToken as jest.Mock).mockResolvedValue(undefined);
  });

  it('logs in, persists tokens and connects GPS', async () => {
    mockedApi.post.mockResolvedValue({ data: { access: 'driver-access-token', refresh: 'refresh-token' } });

    await useAuthStore.getState().login('driver', 'password123');

    expect(mockedApi.post).toHaveBeenCalledWith('/auth/token/', { username: 'driver', password: 'password123' });
    expect(mockedSecureStore.setItemAsync).toHaveBeenCalledWith('fleetpro_access_token', 'driver-access-token');
    expect(mockedSecureStore.setItemAsync).toHaveBeenCalledWith('fleetpro_refresh_token', 'refresh-token');
    expect(connectGps).toHaveBeenCalledWith('driver-access-token');
    expect(registerPushToken).toHaveBeenCalled();
    expect(useAuthStore.getState()).toMatchObject({
      accessToken: 'driver-access-token',
      refreshToken: 'refresh-token',
      role: 'DRIVER',
      username: 'driver',
    });
  });

  it('refreshes access token and keeps refresh token when API does not rotate it', async () => {
    useAuthStore.setState({ refreshToken: 'refresh-token' });
    mockedApi.post.mockResolvedValue({ data: { access: 'passenger-access-token' } });

    const accessToken = await useAuthStore.getState().refreshAccessToken();

    expect(accessToken).toBe('passenger-access-token');
    expect(mockedApi.post).toHaveBeenCalledWith('/auth/token/refresh/', { refresh: 'refresh-token' });
    expect(disconnectGps).toHaveBeenCalled();
    expect(connectGps).toHaveBeenCalledWith('passenger-access-token');
    expect(useAuthStore.getState()).toMatchObject({
      accessToken: 'passenger-access-token',
      refreshToken: 'refresh-token',
      role: 'PASSENGER',
      username: 'passenger',
    });
  });

  it('initializes as anonymous when no refresh token is stored', async () => {
    mockedSecureStore.getItemAsync.mockResolvedValue(null);

    await useAuthStore.getState().initialize();

    expect(mockedSecureStore.getItemAsync).toHaveBeenCalledWith('fleetpro_refresh_token');
    expect(useAuthStore.getState().initialized).toBe(true);
    expect(mockedApi.post).not.toHaveBeenCalled();
  });

  it('initializes from stored refresh token', async () => {
    mockedSecureStore.getItemAsync.mockResolvedValue('stored-refresh-token');
    mockedApi.post.mockResolvedValue({ data: { access: 'passenger-access-token', refresh: 'rotated-refresh-token' } });

    await useAuthStore.getState().initialize();

    expect(mockedApi.post).toHaveBeenCalledWith('/auth/token/refresh/', { refresh: 'stored-refresh-token' });
    expect(useAuthStore.getState()).toMatchObject({
      accessToken: 'passenger-access-token',
      refreshToken: 'rotated-refresh-token',
      initialized: true,
    });
  });

  it('logs out during initialization when refresh fails', async () => {
    mockedSecureStore.getItemAsync.mockResolvedValue('stored-refresh-token');
    mockedApi.post.mockRejectedValue(new Error('expired refresh'));

    await useAuthStore.getState().initialize();

    expect(disconnectGps).toHaveBeenCalled();
    expect(mockedSecureStore.deleteItemAsync).toHaveBeenCalledWith('fleetpro_access_token');
    expect(mockedSecureStore.deleteItemAsync).toHaveBeenCalledWith('fleetpro_refresh_token');
    expect(useAuthStore.getState().initialized).toBe(true);
    expect(useAuthStore.getState().refreshToken).toBeUndefined();
  });

  it('rejects refresh when no refresh token is available', async () => {
    await expect(useAuthStore.getState().refreshAccessToken()).rejects.toThrow('Missing refresh token.');
  });

  it('logs out and clears persisted tokens', async () => {
    useAuthStore.setState({ accessToken: 'access', refreshToken: 'refresh', role: 'DRIVER', username: 'driver' });

    await useAuthStore.getState().logout();

    expect(disconnectGps).toHaveBeenCalled();
    expect(mockedSecureStore.deleteItemAsync).toHaveBeenCalledWith('fleetpro_access_token');
    expect(mockedSecureStore.deleteItemAsync).toHaveBeenCalledWith('fleetpro_refresh_token');
    expect(useAuthStore.getState()).toMatchObject({
      accessToken: undefined,
      refreshToken: undefined,
      role: undefined,
      username: '',
    });
  });
});
