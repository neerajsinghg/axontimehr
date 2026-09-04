import { apiClient } from './client';

export interface ExecutiveSummary {
  total_employees: number;
  active_employees: number;
  new_hires_this_month: number;
  exits_this_month: number;
  attrition_rate_pct: number;
  open_positions: number;
  candidates_in_pipeline: number;
  total_payroll_cost_inr: number;
  avg_attendance_rate_pct: number;
  avg_performance_rating: number;
  training_completion_rate_pct: number;
}

export interface DepartmentMetric {
  department_name: string;
  headcount: number;
  payroll_cost_inr: number;
  attrition_rate_pct: number;
  avg_performance: number;
}

export interface AttritionAnalytics {
  overall_attrition_rate_pct: number;
  voluntary_count: number;
  involuntary_count: number;
  avg_tenure_months: number;
  department_breakdown: DepartmentMetric[];
  monthly_trend: Array<{ month: string; attrition_pct: number }>;
}

export interface LaborCostAnalytics {
  gross_payroll_inr: number;
  net_payroll_inr: number;
  total_tax_inr: number;
  overtime_cost_inr: number;
  reimbursements_cost_inr: number;
  cost_per_employee_inr: number;
}

const unwrap = <T>(res: any): T => (res && res.data !== undefined ? res.data : res) as T;

export const analyticsApi = {
  getExecutiveSummary: async (): Promise<ExecutiveSummary> => {
    const res = await apiClient.get('/analytics/executive-summary');
    return unwrap<ExecutiveSummary>(res);
  },
  getAttritionAnalytics: async (): Promise<AttritionAnalytics> => {
    const res = await apiClient.get('/analytics/attrition');
    return unwrap<AttritionAnalytics>(res);
  },
  getLaborCostAnalytics: async (): Promise<LaborCostAnalytics> => {
    const res = await apiClient.get('/analytics/labor-cost');
    return unwrap<LaborCostAnalytics>(res);
  }
};
