import { apiClient } from './client';

export interface ExpenseCategory {
  id: string;
  tenant_id: string;
  code: string;
  name: string;
  description?: string;
  max_amount?: number;
  requires_receipt: boolean;
  requires_approval: boolean;
  taxable: boolean;
  status: string;
}

export interface ExpenseItem {
  id: string;
  claim_id: string;
  category_id: string;
  category_name?: string;
  expense_date: string;
  amount: number;
  merchant: string;
  description?: string;
  receipt_file_id?: string;
  status: string;
}

export interface ExpenseClaim {
  id: string;
  claim_number: string;
  employee_id: string;
  claim_date: string;
  description: string;
  total_amount: number;
  approved_amount: number;
  currency: string;
  status: string;
  items: ExpenseItem[];
}

export interface LoanType {
  id: string;
  code: string;
  name: string;
  description?: string;
  max_amount: number;
  min_service_months: number;
  max_salary_multiple: number;
  interest_rate: number;
  interest_type: string;
  status: string;
}

export interface LoanInstallment {
  id: string;
  installment_number: number;
  due_date: string;
  principal_amount: number;
  interest_amount: number;
  total_amount: number;
  paid_amount: number;
  remaining_amount: number;
  status: string;
}

export interface EmployeeLoan {
  id: string;
  loan_number: string;
  employee_id: string;
  principal_amount: number;
  approved_principal: number;
  interest_rate: number;
  interest_type: string;
  tenure_months: number;
  monthly_installment: number;
  status: string;
  installments: LoanInstallment[];
}

export interface SalaryAdvance {
  id: string;
  advance_number: string;
  employee_id: string;
  amount: number;
  approved_amount: number;
  recovery_months: number;
  monthly_recovery_amount: number;
  status: string;
}

export interface FinancialDashboardSummary {
  total_claims_count: number;
  pending_claims_amount: number;
  approved_reimbursements_amount: number;
  total_active_loans_count: number;
  outstanding_loans_principal: number;
  monthly_loan_recovery_expected: number;
  total_active_advances_count: number;
  outstanding_advances_amount: number;
}

export interface FinancialTransaction {
  id: string;
  tenant_id: string;
  employee_id: string;
  employee_name?: string;
  employee_code?: string;
  transaction_type: string;
  reference_id: string;
  amount: number;
  currency: string;
  direction: 'DEBIT' | 'CREDIT';
  transaction_date: string;
  department_id?: string;
  department_name?: string;
  cost_center?: string;
}

export const financialApi = {
  // Expenses & Categories
  getCategories: () => apiClient.get<ExpenseCategory[]>('/expenses/categories'),
  createCategory: (data: Partial<ExpenseCategory>) => apiClient.post<ExpenseCategory>('/expenses/categories', data),
  getClaims: () => apiClient.get<ExpenseClaim[]>('/expenses/claims'),
  createClaim: (data: any) => apiClient.post<ExpenseClaim>('/expenses/claims', data),
  submitClaim: (id: string) => apiClient.post<ExpenseClaim>(`/expenses/claims/${id}/submit`),
  uploadReceipt: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post<{ id: string; file_name: string }>('/expenses/receipts/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Loans
  getLoanTypes: () => apiClient.get<LoanType[]>('/loans/types'),
  createLoanType: (data: Partial<LoanType>) => apiClient.post<LoanType>('/loans/types', data),
  getLoans: () => apiClient.get<EmployeeLoan[]>('/loans/requests'),
  requestLoan: (data: { loan_type_id: string; principal_amount: number; tenure_months: number }) =>
    apiClient.post<EmployeeLoan>('/loans/requests', data),

  // Advances
  getAdvances: () => apiClient.get<SalaryAdvance[]>('/salary-advances/'),
  requestAdvance: (data: { amount: number; recovery_months: number }) =>
    apiClient.post<SalaryAdvance>('/salary-advances/', data),

  // Dashboard & Transactions
  getDashboard: () => apiClient.get<FinancialDashboardSummary>('/financial/dashboard'),
  getTransactions: (params?: { transaction_type?: string; direction?: string; search?: string }) =>
    apiClient.get<FinancialTransaction[]>('/financial/transactions', { params }),
};
