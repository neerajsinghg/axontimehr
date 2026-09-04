import { apiClient } from './client';

export interface ServiceHealth {
  status: 'healthy' | 'unhealthy';
  latency_ms?: number;
  details?: string;
}

export interface HealthResponse {
  success: boolean;
  message: string;
  version: string;
  environment: string;
  services: {
    database: ServiceHealth;
    redis: ServiceHealth;
  };
  timestamp: string;
  request_id?: string;
}

export const healthApi = {
  getHealthStatus: async (): Promise<HealthResponse> => {
    return (await apiClient.get('/health')) as unknown as HealthResponse;
  },
};
