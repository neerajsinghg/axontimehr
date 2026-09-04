import { apiClient } from './client';

export interface RegularizationRequest {
  id: string;
  tenant_id: string;
  attendance_id?: string;
  employee_id: string;
  employee_name: string;
  attendance_date: string;
  original_check_in?: string;
  original_check_out?: string;
  requested_check_in: string;
  requested_check_out: string;
  reason: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  approval_instance_id?: string;
  created_at: string;
  updated_at: string;
}

export interface RegularizationCreatePayload {
  attendance_date: string;
  requested_check_in: string;
  requested_check_out: string;
  reason: string;
}

export const regularizationApi = {
  getRequests: async (): Promise<RegularizationRequest[]> => {
    return apiClient.get('/regularizations');
  },
  createRequest: async (data: RegularizationCreatePayload): Promise<RegularizationRequest> => {
    return apiClient.post('/regularizations', data);
  }
};
