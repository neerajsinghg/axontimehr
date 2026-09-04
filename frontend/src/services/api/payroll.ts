import { apiClient } from './client';

export interface SalaryComponent {
  id: string;
  tenant_id: string;
  code: string;
  name: string;
  description?: string;
  component_type: 'EARNING' | 'DEDUCTION' | 'EMPLOYER_CONTRIBUTION' | 'REIMBURSEMENT' | 'TAX';
  calculation_type: 'FIXED' | 'PERCENTAGE' | 'FORMULA' | 'VARIABLE';
  percentage?: number;
  fixed_amount?: number;
  formula?: string;
  taxable: boolean;
  included_in_ctc: boolean;
  affects_gross: boolean;
  affects_net: boolean;
  status: string;
}

export interface SalaryStructureComponentItem {
  id: string;
  component_id: string;
  component_code?: string;
  component_name?: string;
  component_type?: string;
  calculation_type: string;
  amount?: number;
  percentage?: number;
  formula?: string;
}

export interface SalaryStructure {
  id: string;
  tenant_id: string;
  code: string;
  name: string;
  description?: string;
  status: string;
  components: SalaryStructureComponentItem[];
  created_at: string;
}

export interface EmployeeSalaryAssignment {
  id: string;
  tenant_id: string;
  employee_id: string;
  salary_structure_id: string;
  structure_name?: string;
  annual_ctc: number;
  monthly_ctc: number;
  gross_salary: number;
  effective_from: string;
  effective_to?: string;
  version: number;
  status: string;
  created_at: string;
}

export interface PayrollPeriod {
  id: string;
  tenant_id: string;
  name: string;
  year: number;
  month: number;
  start_date: string;
  end_date: string;
  pay_date: string;
  status: string;
  created_at: string;
}

export interface PayrollLineItem {
  id: string;
  component_code: string;
  component_name: string;
  line_type: string;
  amount: number;
  calculation_explanation?: string;
}

export interface PayrollEmployee {
  id: string;
  employee_id: string;
  employee_name?: string;
  employee_code?: string;
  calendar_days: number;
  working_days: number;
  present_days: number;
  paid_leave_days: number;
  unpaid_leave_days: number;
  lop_days: number;
  holiday_days: number;
  overtime_hours: number;
  gross_salary: number;
  total_earnings: number;
  total_deductions: number;
  employer_contributions: number;
  net_salary: number;
  status: string;
  exception_message?: string;
  line_items: PayrollLineItem[];
}

export interface PayrollRun {
  id: string;
  tenant_id: string;
  period_id: string;
  period_name?: string;
  total_employees: number;
  total_gross: number;
  total_deductions: number;
  total_net: number;
  status: string;
  approval_instance_id?: string;
  locked_at?: string;
  paid_at?: string;
  employees: PayrollEmployee[];
  created_at: string;
}

export interface PayrollAdjustment {
  id: string;
  tenant_id: string;
  employee_id: string;
  employee_name?: string;
  adjustment_type: string;
  amount: number;
  reason: string;
  status: string;
  created_at: string;
}

export interface Payslip {
  id: string;
  tenant_id: string;
  payroll_employee_id: string;
  employee_id: string;
  period_id: string;
  period_name: string;
  pdf_path?: string;
  download_token: string;
  download_count: number;
  generated_at: string;
}

export const payrollApi = {
  getComponents: async (): Promise<SalaryComponent[]> => {
    return apiClient.get('/salary/components');
  },

  seedComponents: async (): Promise<SalaryComponent[]> => {
    return apiClient.post('/salary/components/seed');
  },

  getStructures: async (): Promise<SalaryStructure[]> => {
    return apiClient.get('/salary/structures');
  },

  createStructure: async (data: { code: string; name: string; description?: string; components: any[] }): Promise<SalaryStructure> => {
    return apiClient.post('/salary/structures', data);
  },

  assignSalary: async (data: { employee_id: string; salary_structure_id: string; annual_ctc: number; effective_from: string }): Promise<EmployeeSalaryAssignment> => {
    return apiClient.post('/salary/assignments', data);
  },

  getAssignment: async (employeeId: string): Promise<EmployeeSalaryAssignment | null> => {
    return apiClient.get(`/salary/assignments/${employeeId}`);
  },

  getPeriods: async (): Promise<PayrollPeriod[]> => {
    return apiClient.get('/payroll/periods');
  },

  createPeriod: async (data: { name: string; year: number; month: number; start_date: string; end_date: string; pay_date: string }): Promise<PayrollPeriod> => {
    return apiClient.post('/payroll/periods', data);
  },

  createRun: async (periodId: string): Promise<PayrollRun> => {
    return apiClient.post('/payroll/runs', { period_id: periodId });
  },

  calculateRun: async (runId: string): Promise<PayrollRun> => {
    return apiClient.post(`/payroll/runs/${runId}/calculate`);
  },

  submitRunApproval: async (runId: string): Promise<PayrollRun> => {
    return apiClient.post(`/payroll/runs/${runId}/approve`);
  },

  lockRun: async (runId: string): Promise<PayrollRun> => {
    return apiClient.post(`/payroll/runs/${runId}/lock`);
  },

  markRunPaid: async (runId: string): Promise<PayrollRun> => {
    return apiClient.post(`/payroll/runs/${runId}/mark-paid`);
  },

  getPayslips: async (): Promise<Payslip[]> => {
    return apiClient.get('/payslips');
  },

  downloadPayslipUrl: (token: string): string => {
    return `/api/v1/payslips/${token}/download`;
  }
};
