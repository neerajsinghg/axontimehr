import { apiClient } from './client';

export interface ComplianceDashboardSummary {
  compliance_score: number;
  risk_level: string;
  open_violations_count: number;
  overdue_tasks_count: number;
  active_legal_holds_count: number;
  expiring_registrations_count: number;
  mandatory_policy_ack_pct: number;
  snapshot_date: string;
}

export interface ComplianceEstablishment {
  id: string;
  tenant_id: string;
  name: string;
  code: string;
  country_code: string;
  state_code: string;
  city?: string;
  address?: string;
  is_active: boolean;
  created_at: string;
}

export interface StatutoryRegistration {
  id: string;
  tenant_id: string;
  establishment_id?: string;
  registration_type: string;
  masked_number: string;
  authority_name: string;
  issue_date?: string;
  expiry_date?: string;
  renewal_status: string;
  created_at: string;
}

export interface EmployeeStatutoryProfile {
  id: string;
  tenant_id: string;
  employee_id: string;
  tax_identifier_masked?: string;
  social_security_number_masked?: string;
  pf_uan?: string;
  esi_number?: string;
  professional_tax_registered: boolean;
  verification_status: string;
  verified_at?: string;
}

export interface ComplianceRule {
  id: string;
  tenant_id: string;
  rule_code: string;
  rule_name: string;
  version: number;
  category: string;
  country_code: string;
  state_code: string;
  effective_from: string;
  effective_to?: string;
  rule_config_json: any;
  status: string;
  is_active: boolean;
}

export interface PrePayrollPrecheckResponse {
  status: string;
  total_employees_checked: number;
  issues_count: number;
  issues_list: Array<{
    employee_id: string;
    employee_name: string;
    rule_code: string;
    severity: string;
    issue_description: string;
    recommended_action: string;
  }>;
}

export interface ComplianceTask {
  id: string;
  tenant_id: string;
  title: string;
  compliance_type: string;
  description?: string;
  assigned_to_id?: string;
  reviewer_id?: string;
  due_date: string;
  priority: string;
  status: string;
  evidence_file_url?: string;
  completion_date?: string;
  created_at: string;
}

export interface ComplianceViolation {
  id: string;
  tenant_id: string;
  violation_code: string;
  category: string;
  severity: string;
  description: string;
  employee_id?: string;
  detected_date: string;
  status: string;
  root_cause?: string;
  corrective_action?: string;
  preventive_action?: string;
  resolved_at?: string;
}

export interface InternalAudit {
  id: string;
  tenant_id: string;
  audit_title: string;
  audit_type: string;
  auditor_name: string;
  start_date: string;
  end_date: string;
  status: string;
  checklist_score: number;
  findings_summary?: string;
}

export interface DataSubjectRequest {
  id: string;
  tenant_id: string;
  request_number: string;
  employee_id: string;
  request_type: string;
  status: string;
  details?: string;
  response_summary?: string;
  submitted_at: string;
}

export interface LegalHold {
  id: string;
  tenant_id: string;
  hold_name: string;
  reason: string;
  start_date: string;
  release_date?: string;
  is_active: boolean;
  created_at: string;
}

export const complianceApi = {
  getDashboardSummary: async (): Promise<ComplianceDashboardSummary> => {
    const res = await apiClient.get('/compliance/dashboard');
    return res.data;
  },

  getEstablishments: async (): Promise<ComplianceEstablishment[]> => {
    const res = await apiClient.get('/compliance/establishments');
    return res.data;
  },

  createEstablishment: async (payload: { name: string; code: string; country_code?: string; state_code?: string; city?: string; address?: string }): Promise<ComplianceEstablishment> => {
    const res = await apiClient.post('/compliance/establishments', payload);
    return res.data;
  },

  getRegistrations: async (): Promise<StatutoryRegistration[]> => {
    const res = await apiClient.get('/compliance/registrations');
    return res.data;
  },

  createRegistration: async (payload: { registration_type: string; registration_number: string; authority_name: string; establishment_id?: string }): Promise<StatutoryRegistration> => {
    const res = await apiClient.post('/compliance/registrations', payload);
    return res.data;
  },

  getEmployeeStatutoryProfile: async (employeeId: string): Promise<EmployeeStatutoryProfile> => {
    const res = await apiClient.get(`/compliance/employee-statutory/${employeeId}`);
    return res.data;
  },

  getRules: async (): Promise<ComplianceRule[]> => {
    const res = await apiClient.get('/compliance/rules');
    return res.data;
  },

  createRule: async (payload: { rule_code: string; rule_name: string; category: string; effective_from: string; rule_config?: any }): Promise<ComplianceRule> => {
    const res = await apiClient.post('/compliance/rules', payload);
    return res.data;
  },

  runPayrollPrecheck: async (): Promise<PrePayrollPrecheckResponse> => {
    const res = await apiClient.post('/compliance/payroll/precheck');
    return res.data;
  },

  getTasks: async (): Promise<ComplianceTask[]> => {
    const res = await apiClient.get('/compliance/tasks');
    return res.data;
  },

  createTask: async (payload: { title: string; compliance_type: string; due_date: string; priority?: string; description?: string }): Promise<ComplianceTask> => {
    const res = await apiClient.post('/compliance/tasks', payload);
    return res.data;
  },

  getViolations: async (): Promise<ComplianceViolation[]> => {
    const res = await apiClient.get('/compliance/violations');
    return res.data;
  },

  createViolation: async (payload: { violation_code: string; category: string; description: string; severity?: string }): Promise<ComplianceViolation> => {
    const res = await apiClient.post('/compliance/violations', payload);
    return res.data;
  },

  getAudits: async (): Promise<InternalAudit[]> => {
    const res = await apiClient.get('/compliance/audits');
    return res.data;
  },

  createAudit: async (payload: { audit_title: string; audit_type: string; auditor_name: string; start_date: string; end_date: string }): Promise<InternalAudit> => {
    const res = await apiClient.post('/compliance/audits', payload);
    return res.data;
  },

  getDsrRequests: async (): Promise<DataSubjectRequest[]> => {
    const res = await apiClient.get('/compliance/privacy/dsr');
    return res.data;
  },

  createDsrRequest: async (payload: { request_type: string; details?: string }): Promise<DataSubjectRequest> => {
    const res = await apiClient.post('/compliance/privacy/dsr', payload);
    return res.data;
  },

  getLegalHolds: async (): Promise<LegalHold[]> => {
    const res = await apiClient.get('/compliance/privacy/legal-holds');
    return res.data;
  },

  createLegalHold: async (payload: { hold_name: string; reason: string; start_date: string }): Promise<LegalHold> => {
    const res = await apiClient.post('/compliance/privacy/legal-holds', payload);
    return res.data;
  }
};
