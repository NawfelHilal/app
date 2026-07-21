jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn(),
  setItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));

jest.mock('../api/gps', () => ({
  connectGps: jest.fn(),
  disconnectGps: jest.fn(),
}));

jest.mock('../api/notifications', () => ({
  registerPushToken: jest.fn(),
}));

import { AxiosHeaders, AxiosRequestConfig } from 'axios';
import { api } from './client';
import { useAuthStore } from '../store/auth';

describe('api client JWT interceptors', () => {
  beforeEach(() => {
    useAuthStore.setState({
      accessToken: undefined,
      refreshToken: undefined,
      role: undefined,
      username: '',
      initialized: false,
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
    api.defaults.adapter = undefined;
  });

  it('adds bearer access token to outgoing requests', async () => {
    useAuthStore.setState({ accessToken: 'access-token' });
    let capturedConfig: AxiosRequestConfig | undefined;
    api.defaults.adapter = async (config) => {
      capturedConfig = config;
      return {
        data: { ok: true },
        status: 200,
        statusText: 'OK',
        headers: {},
        config,
      };
    };

    await api.get('/rides/');

    expect((capturedConfig?.headers as AxiosHeaders).get('Authorization')).toBe('Bearer access-token');
  });

  it('refreshes token once on protected 401 then retries original request', async () => {
    const refreshAccessToken = jest.fn().mockResolvedValue('fresh-token');
    useAuthStore.setState({ refreshToken: 'refresh-token', refreshAccessToken });
    let calls = 0;
    const authorizations: Array<string | undefined> = [];
    api.defaults.adapter = async (config) => {
      calls += 1;
      authorizations.push((config.headers as AxiosHeaders).get('Authorization') as string | undefined);
      if (calls === 1) {
        return Promise.reject({ config, response: { status: 401 } });
      }
      return {
        data: { ok: true },
        status: 200,
        statusText: 'OK',
        headers: {},
        config,
      };
    };

    const response = await api.get('/rides/');

    expect(response.data).toEqual({ ok: true });
    expect(refreshAccessToken).toHaveBeenCalledTimes(1);
    expect(calls).toBe(2);
    expect(authorizations).toEqual([undefined, 'Bearer fresh-token']);
  });

  it('does not refresh failed login requests', async () => {
    const refreshAccessToken = jest.fn();
    useAuthStore.setState({ refreshToken: 'refresh-token', refreshAccessToken });
    api.defaults.adapter = async (config) => Promise.reject({ config, response: { status: 401 } });

    await expect(api.post('/auth/token/', { username: 'driver', password: 'bad' })).rejects.toMatchObject({
      response: { status: 401 },
    });

    expect(refreshAccessToken).not.toHaveBeenCalled();
  });
});
