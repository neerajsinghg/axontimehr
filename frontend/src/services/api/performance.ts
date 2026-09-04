import { apiClient } from './client';

export interface PerformanceCycle {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  cycle_type: string;
  start_date: string;
  end_date: string;
  status: string;
  created_at: string;
}

export interface Goal {
  id: string;
  tenant_id: string;
  cycle_id: string;
  employee_id: string;
  title: string;
  description?: string;
  goal_type: string;
  baseline_value: number;
  target_value: number;
  current_value: number;
  unit: string;
  weightage: number;
  due_date?: string;
  status: string;
  progress_pct: number;
  achievement_pct: number;
  created_at: string;
}

export interface PerformanceReview {
  id: string;
  tenant_id: string;
  cycle_id: string;
  employee_id: string;
  manager_id?: string;
  self_score?: number;
  manager_score?: number;
  calculated_score?: number;
  calibrated_score?: number;
  final_score?: number;
  status: string;
  is_acknowledged: boolean;
  acknowledged_at?: string;
  employee_comments?: string;
  created_at: string;
}

export interface Course {
  id: string;
  tenant_id: string;
  title: string;
  description?: string;
  category: string;
  provider: string;
  mode: string;
  duration_hours: number;
  cost: number;
  capacity: number;
  course_url?: string;
  is_active: boolean;
}

export interface TrainingEnrollment {
  id: string;
  tenant_id: string;
  course_id: string;
  employee_id: string;
  status: string;
  completion_pct: number;
  created_at: string;
}

export interface EmployeeSkill {
  id: string;
  tenant_id: string;
  employee_id: string;
  skill_name: string;
  category: string;
  current_level: number;
  target_level: number;
  skill_gap: number;
  updated_at: string;
}

export interface Survey {
  id: string;
  tenant_id: string;
  title: string;
  description?: string;
  survey_type: string;
  start_date: string;
  end_date: string;
  is_anonymous: boolean;
  status: string;
  created_at: string;
}

const unwrap = (res: any) => {
  if (!res) return res;
  if (Array.isArray(res)) return res;
  if (typeof res === 'object' && 'data' in res && (Array.isArray(res.data) || typeof res.data === 'object')) {
    return res.data;
  }
  return res;
};

export const performanceApi = {
  getCycles: async (): Promise<PerformanceCycle[]> => {
    const res: any = await apiClient.get('/performance/cycles');
    const data = unwrap(res);
    return Array.isArray(data) ? data : [];
  },

  createCycle: async (data: Partial<PerformanceCycle>): Promise<PerformanceCycle> => {
    const res: any = await apiClient.post('/performance/cycles', data);
    return unwrap(res);
  },

  getGoals: async (employeeId?: string): Promise<Goal[]> => {
    const res: any = await apiClient.get('/performance/goals', { params: { employee_id: employeeId } });
    const data = unwrap(res);
    return Array.isArray(data) ? data : [];
  },

  createGoal: async (data: Partial<Goal>): Promise<Goal> => {
    const res: any = await apiClient.post('/performance/goals', data);
    return unwrap(res);
  },

  updateGoalProgress: async (goalId: string, data: { current_value: number; comments?: string }): Promise<Goal> => {
    const res: any = await apiClient.post(`/performance/goals/${goalId}/progress`, data);
    return unwrap(res);
  },

  getMyReview: async (cycleId: string): Promise<PerformanceReview> => {
    const res: any = await apiClient.get('/performance/reviews/my-review', { params: { cycle_id: cycleId } });
    return unwrap(res);
  },

  submitSelfAssessment: async (reviewId: string, data: { self_score: number; employee_comments?: string }): Promise<PerformanceReview> => {
    const res: any = await apiClient.post(`/performance/reviews/${reviewId}/self-assessment`, data);
    return unwrap(res);
  },

  submitManagerAssessment: async (reviewId: string, data: { manager_score: number; manager_comments?: string }): Promise<PerformanceReview> => {
    const res: any = await apiClient.post(`/performance/reviews/${reviewId}/manager-assessment`, data);
    return unwrap(res);
  },

  submitCalibration: async (data: { review_id: string; calibrated_score: number; reason: string }): Promise<PerformanceReview> => {
    const res: any = await apiClient.post('/performance/calibration', data);
    return unwrap(res);
  },

  getCourses: async (): Promise<Course[]> => {
    const res: any = await apiClient.get('/training/courses');
    const data = unwrap(res);
    return Array.isArray(data) ? data : [];
  },

  createCourse: async (data: Partial<Course>): Promise<Course> => {
    const res: any = await apiClient.post('/training/courses', data);
    return unwrap(res);
  },

  getEnrollments: async (): Promise<TrainingEnrollment[]> => {
    const res: any = await apiClient.get('/training/enrollments');
    const data = unwrap(res);
    return Array.isArray(data) ? data : [];
  },

  enrollEmployee: async (courseId: string): Promise<TrainingEnrollment> => {
    const res: any = await apiClient.post('/training/enrollments', { course_id: courseId });
    return unwrap(res);
  },

  getSkillsMatrix: async (): Promise<EmployeeSkill[]> => {
    const res: any = await apiClient.get('/training/skills/matrix');
    const data = unwrap(res);
    return Array.isArray(data) ? data : [];
  },

  updateSkill: async (data: { skill_name: string; category?: string; current_level: number; target_level: number }): Promise<EmployeeSkill> => {
    const res: any = await apiClient.post('/training/skills/update', data);
    return unwrap(res);
  },

  getSurveys: async (): Promise<Survey[]> => {
    const res: any = await apiClient.get('/engagement/surveys');
    const data = unwrap(res);
    return Array.isArray(data) ? data : [];
  },

  createSurvey: async (data: Partial<Survey>): Promise<Survey> => {
    const res: any = await apiClient.post('/engagement/surveys', data);
    return unwrap(res);
  },
};
