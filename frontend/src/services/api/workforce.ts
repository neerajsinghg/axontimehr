import { apiClient } from './client';

export interface HeadcountPlan {
  id: string;
  tenant_id: string;
  planning_year: number;
  current_headcount: number;
  target_headcount: number;
  planned_hiring: number;
  expected_attrition: number;
  allocated_budget: number;
  status: string;
  created_at: string;
}

export interface GapAnalysis {
  department_id?: string;
  department_name: string;
  current_headcount: number;
  required_headcount: number;
  headcount_gap: number;
  planned_hiring: number;
  skill_gap_count: number;
  advisory_recommendation: string;
}

export interface WorkforceForecast {
  forecast_period: string;
  expected_headcount: number;
  expected_hiring_need: number;
  expected_attrition: number;
  expected_labor_cost: number;
  confidence_level: string;
}

const unwrap = <T>(res: any): T => (res && res.data !== undefined ? res.data : res) as T;

export const workforceApi = {
  getHeadcountPlans: async (): Promise<HeadcountPlan[]> => {
    const res = await apiClient.get('/workforce/headcount-plans');
    return unwrap<HeadcountPlan[]>(res);
  },
  createHeadcountPlan: async (data: Partial<HeadcountPlan>): Promise<HeadcountPlan> => {
    const res = await apiClient.post('/workforce/headcount-plans', data);
    return unwrap<HeadcountPlan>(res);
  },
  getGapAnalysis: async (): Promise<GapAnalysis[]> => {
    const res = await apiClient.get('/workforce/gap-analysis');
    return unwrap<GapAnalysis[]>(res);
  },
  getForecast: async (): Promise<WorkforceForecast> => {
    const res = await apiClient.get('/workforce/forecast');
    return unwrap<WorkforceForecast>(res);
  }
};
