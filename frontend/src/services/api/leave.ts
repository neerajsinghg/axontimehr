import { apiClient } from './client';

export interface LeaveType {
  id: string;
  tenant_id: string;
  code: string;
  name: string;
  description?: string;
  color_code: string;
  paid: boolean;
  requires_document: boolean;
  allow_half_day: boolean;
  allow_partial_day: boolean;
  allow_backdated: boolean;
  allow_future: boolean;
  minimum_notice_days: number;
  maximum_consecutive_days?: number;
  status: 'ACTIVE' | 'INACTIVE';
  created_at: string;
  updated_at: string;
}

export interface LeaveBalance {
  id: string;
  tenant_id: string;
  employee_id: string;
  leave_type_id: string;
  leave_type_code: string;
  leave_type_name: string;
  color_code: string;
  year: number;
  allocated: number;
  accrued: number;
  adjusted: number;
  used: number;
  pending: number;
  expired: number;
  carried_forward: number;
  available: number;
  updated_at: string;
}

export interface LeaveRequest {
  id: string;
  tenant_id: string;
  employee_id: string;
  employee_name: string;
  leave_type_id: string;
  leave_type_name: string;
  leave_type_code: string;
  color_code: string;
  start_date: string;
  end_date: string;
  duration_type: 'FULL_DAY' | 'HALF_DAY' | 'PARTIAL_DAY';
  half_day_position?: 'FIRST_HALF' | 'SECOND_HALF';
  total_requested_days: number;
  working_days_count: number;
  holiday_days_count: number;
  weekly_off_days_count: number;
  reason: string;
  document_url?: string;
  status: 'DRAFT' | 'PENDING' | 'APPROVED' | 'REJECTED' | 'CANCEL_REQUESTED' | 'CANCELLED' | 'WITHDRAWN' | 'EXPIRED';
  approval_instance_id?: string;
  created_at: string;
  updated_at: string;
}

export interface LeaveRequestCreatePayload {
  leave_type_id: string;
  start_date: string;
  end_date: string;
  duration_type?: 'FULL_DAY' | 'HALF_DAY' | 'PARTIAL_DAY';
  half_day_position?: 'FIRST_HALF' | 'SECOND_HALF';
  reason: string;
  document_url?: string;
}

export const leaveApi = {
  getLeaveTypes: async (): Promise<LeaveType[]> => {
    return apiClient.get('/leaves/types');
  },
  createLeaveType: async (data: Partial<LeaveType>): Promise<LeaveType> => {
    return apiClient.post('/leaves/types', data);
  },
  getBalances: async (year?: number): Promise<LeaveBalance[]> => {
    return apiClient.get('/leaves/balance', { params: { year } });
  },
  getLeaveRequests: async (): Promise<LeaveRequest[]> => {
    return apiClient.get('/leaves/requests');
  },
  createLeaveRequest: async (data: LeaveRequestCreatePayload): Promise<LeaveRequest> => {
    return apiClient.post('/leaves/requests', data);
  },
  cancelLeaveRequest: async (id: string): Promise<LeaveRequest> => {
    return apiClient.post(`/leaves/requests/${id}/cancel`);
  }
};
