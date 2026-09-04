import { apiClient } from './client';

export interface EmployeeDashboardSummary {
  employee_id: string;
  first_name: string;
  last_name: string;
  designation_name?: string;
  department_name?: string;
  today_status: string;
  check_in_time?: string;
  leave_balance_days: number;
  latest_payslip_month?: string;
  latest_net_pay_inr?: number;
  pending_tasks_count: number;
  active_goals_count: number;
  assigned_trainings_count: number;
  unread_announcements_count: number;
}

export interface ProfileUpdateRequest {
  personal_email?: string;
  personal_phone?: string;
  emergency_contact?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
}

export interface ProfileChangeRequestCreate {
  field_name: string;
  new_value: string;
  reason: string;
}

export interface HRDocumentTemplate {
  id: string;
  tenant_id: string;
  title: string;
  template_code: string;
  category: string;
  template_body: string;
  variables_json?: string;
  is_active: boolean;
  created_at: string;
}

export interface GeneratedHRLetter {
  id: string;
  tenant_id: string;
  employee_id: string;
  template_id?: string;
  title: string;
  letter_number: string;
  snapshot_html: string;
  file_url?: string;
  is_acknowledged: boolean;
  acknowledged_at?: string;
  created_at: string;
}

export interface HRPolicy {
  id: string;
  tenant_id: string;
  title: string;
  category: string;
  current_version: string;
  policy_body: string;
  file_url?: string;
  is_mandatory_ack: boolean;
  created_at: string;
  is_acknowledged_by_me?: boolean;
}

export interface HRRequest {
  id: string;
  tenant_id: string;
  employee_id: string;
  request_type: string;
  subject: string;
  details?: string;
  status: string;
  assigned_to_id?: string;
  expected_completion_date?: string;
  created_at: string;
}

export interface HRHelpdeskComment {
  id: string;
  ticket_id: string;
  sender_id: string;
  comment_text: string;
  attachment_url?: string;
  created_at: string;
}

export interface HRHelpdeskTicket {
  id: string;
  tenant_id: string;
  employee_id: string;
  ticket_number: string;
  category: string;
  priority: string;
  subject: string;
  description: string;
  status: string;
  assigned_agent_id?: string;
  created_at: string;
  updated_at: string;
  comments: HRHelpdeskComment[];
}

export interface CompanyAnnouncement {
  id: string;
  tenant_id: string;
  title: string;
  content: string;
  category: string;
  priority: string;
  target_type: string;
  target_id?: string;
  publish_date: string;
  is_mandatory_ack: boolean;
  status: string;
  is_read_by_me?: boolean;
  is_acknowledged_by_me?: boolean;
}

export interface EmployeeRecognition {
  id: string;
  tenant_id: string;
  sender_id: string;
  recipient_id: string;
  sender_name?: string;
  recipient_name?: string;
  recognition_type: string;
  message: string;
  created_at: string;
}

export interface UnifiedTaskItem {
  id: string;
  module: string;
  title: string;
  description: string;
  created_at: string;
  priority: string;
  action_url: string;
}

export const employeeExperienceApi = {
  getMyDashboard: async (): Promise<EmployeeDashboardSummary> => {
    const res = await apiClient.get('/employee-experience/me/dashboard');
    return res.data;
  },

  updateMyProfile: async (data: ProfileUpdateRequest) => {
    const res = await apiClient.put('/employee-experience/me/profile', data);
    return res.data;
  },

  createProfileChangeRequest: async (data: ProfileChangeRequestCreate) => {
    const res = await apiClient.post('/employee-experience/me/profile/change-requests', data);
    return res.data;
  },

  getDocumentTemplates: async (): Promise<HRDocumentTemplate[]> => {
    const res = await apiClient.get('/employee-experience/me/document-templates');
    return res.data;
  },

  generateHrLetter: async (data: { template_id: string; employee_id: string; custom_variables?: Record<string, any> }): Promise<GeneratedHRLetter> => {
    const res = await apiClient.post('/employee-experience/me/documents/letters/generate', data);
    return res.data;
  },

  getMyLetters: async (): Promise<GeneratedHRLetter[]> => {
    const res = await apiClient.get('/employee-experience/me/documents/letters');
    return res.data;
  },

  getHrPolicies: async (): Promise<HRPolicy[]> => {
    const res = await apiClient.get('/employee-experience/me/policies');
    return res.data;
  },

  acknowledgePolicy: async (policyId: string) => {
    const res = await apiClient.post(`/employee-experience/me/policies/${policyId}/acknowledge`);
    return res.data;
  },

  createHrRequest: async (data: { request_type: string; subject: string; details?: string }): Promise<HRRequest> => {
    const res = await apiClient.post('/employee-experience/me/requests', data);
    return res.data;
  },

  getHrRequests: async (): Promise<HRRequest[]> => {
    const res = await apiClient.get('/employee-experience/me/requests');
    return res.data;
  },

  createHelpdeskTicket: async (data: { category: string; priority: string; subject: string; description: string }): Promise<HRHelpdeskTicket> => {
    const res = await apiClient.post('/employee-experience/me/helpdesk/tickets', data);
    return res.data;
  },

  getHelpdeskTickets: async (): Promise<HRHelpdeskTicket[]> => {
    const res = await apiClient.get('/employee-experience/me/helpdesk/tickets');
    return res.data;
  },

  addTicketComment: async (ticketId: string, commentText: string): Promise<HRHelpdeskComment> => {
    const res = await apiClient.post(`/employee-experience/me/helpdesk/tickets/${ticketId}/comments`, { comment_text: commentText });
    return res.data;
  },

  getAnnouncements: async (): Promise<CompanyAnnouncement[]> => {
    const res = await apiClient.get('/employee-experience/me/announcements');
    return res.data;
  },

  createAnnouncement: async (data: { title: string; content: string; priority: string }): Promise<CompanyAnnouncement> => {
    const res = await apiClient.post('/employee-experience/me/announcements', data);
    return res.data;
  },

  getRecognitions: async (): Promise<EmployeeRecognition[]> => {
    const res = await apiClient.get('/employee-experience/me/recognitions');
    return res.data;
  },

  createRecognition: async (data: { recipient_id: string; recognition_type: string; message: string }): Promise<EmployeeRecognition> => {
    const res = await apiClient.post('/employee-experience/me/recognitions', data);
    return res.data;
  },

  getUnifiedTasks: async (): Promise<UnifiedTaskItem[]> => {
    const res = await apiClient.get('/employee-experience/me/tasks');
    return res.data;
  }
};
