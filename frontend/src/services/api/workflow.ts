import { apiClient } from './client';

export interface ApprovalItem {
  instance_id: string;
  workflow_id: string;
  workflow_name: string;
  entity_type: 'LEAVE_REQUEST' | 'REGULARIZATION' | string;
  entity_id: string;
  requester_id: string;
  requester_name: string;
  department_name?: string;
  current_step_order: number;
  current_step_name: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'RETURNED' | 'CANCELLED';
  details: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ApprovalActionPayload {
  action: 'APPROVE' | 'REJECT' | 'RETURN' | 'CANCEL' | 'DELEGATE';
  comments?: string;
  delegate_to_user_id?: string;
}

export const workflowApi = {
  getInbox: async (): Promise<ApprovalItem[]> => {
    return apiClient.get('/approvals/inbox');
  },
  processAction: async (instanceId: string, payload: ApprovalActionPayload): Promise<any> => {
    return apiClient.post(`/approvals/${instanceId}/action`, payload);
  }
};
