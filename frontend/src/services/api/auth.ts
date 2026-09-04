import { apiClient } from './client';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_verified: boolean;
  is_locked: boolean;
  last_login_at?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  data: AuthTokens;
  request_id?: string;
}

export const authApi = {
  register: async (payload: any): Promise<User> => {
    return (await apiClient.post('/auth/register', payload)) as unknown as User;
  },

  login: async (payload: any): Promise<AuthResponse> => {
    return (await apiClient.post('/auth/login', payload)) as unknown as AuthResponse;
  },

  refresh: async (refreshToken: string): Promise<AuthResponse> => {
    return (await apiClient.post('/auth/refresh', { refresh_token: refreshToken })) as unknown as AuthResponse;
  },

  logout: async (refreshToken: string): Promise<any> => {
    return await apiClient.post('/auth/logout', { refresh_token: refreshToken });
  },

  getMe: async (): Promise<User> => {
    return (await apiClient.get('/auth/me')) as unknown as User;
  },

  changePassword: async (payload: any): Promise<any> => {
    return await apiClient.post('/auth/change-password', payload);
  },

  forgotPassword: async (email: string): Promise<any> => {
    return await apiClient.post('/auth/forgot-password', { email });
  },

  resetPassword: async (payload: any): Promise<any> => {
    return await apiClient.post('/auth/reset-password', payload);
  },

  sendOTP: async (phoneNumber: string): Promise<any> => {
    return await apiClient.post('/auth/otp/send', { phone_number: phoneNumber });
  },

  verifyOTP: async (phoneNumber: string, otpCode: string): Promise<AuthResponse> => {
    return (await apiClient.post('/auth/otp/verify', { phone_number: phoneNumber, otp_code: otpCode })) as unknown as AuthResponse;
  },

  verifyEmail: async (token: string): Promise<any> => {

    return await apiClient.post('/auth/verify-email', { token });
  },

  resendVerification: async (email: string): Promise<any> => {
    return await apiClient.post('/auth/resend-verification', { email });
  },
};
