import { apiClient } from './client';

export interface JobRequisition {
  id: string;
  tenant_id: string;
  department_id?: string;
  positions_count: number;
  employment_type: string;
  location?: string;
  min_experience: number;
  max_experience: number;
  required_skills?: string;
  salary_min: number;
  salary_max: number;
  budget: number;
  priority: string;
  reason_for_hiring?: string;
  status: string;
  created_at: string;
}

export interface JobPosting {
  id: string;
  tenant_id: string;
  title: string;
  description: string;
  requirements?: string;
  location?: string;
  location_type: string;
  employment_type: string;
  openings_count: number;
  is_published: boolean;
  slug?: string;
  created_at: string;
}

export interface Candidate {
  id: string;
  tenant_id: string;
  job_posting_id?: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  current_company?: string;
  current_designation?: string;
  expected_salary: number;
  notice_period_days: number;
  source: string;
  resume_url?: string;
  skills_list?: string;
  overall_score: number;
  status: string;
  created_at: string;
}

export interface Interview {
  id: string;
  tenant_id: string;
  candidate_id: string;
  interview_type: string;
  scheduled_at: string;
  duration_minutes: number;
  meeting_url?: string;
  status: string;
}

export interface Offer {
  id: string;
  tenant_id: string;
  candidate_id: string;
  offer_number: string;
  base_salary: number;
  variable_pay: number;
  joining_date: string;
  status: string;
}

const unwrap = <T>(res: any): T => (res && res.data !== undefined ? res.data : res) as T;

export const recruitmentApi = {
  getRequisitions: async (): Promise<JobRequisition[]> => {
    const res = await apiClient.get('/recruitment/requisitions');
    return unwrap<JobRequisition[]>(res);
  },
  createRequisition: async (data: Partial<JobRequisition>): Promise<JobRequisition> => {
    const res = await apiClient.post('/recruitment/requisitions', data);
    return unwrap<JobRequisition>(res);
  },
  getJobPostings: async (): Promise<JobPosting[]> => {
    const res = await apiClient.get('/recruitment/jobs');
    return unwrap<JobPosting[]>(res);
  },
  createJobPosting: async (data: Partial<JobPosting>): Promise<JobPosting> => {
    const res = await apiClient.post('/recruitment/jobs', data);
    return unwrap<JobPosting>(res);
  },
  getCandidates: async (): Promise<Candidate[]> => {
    const res = await apiClient.get('/recruitment/candidates');
    return unwrap<Candidate[]>(res);
  },
  createCandidate: async (data: Partial<Candidate>): Promise<Candidate> => {
    const res = await apiClient.post('/recruitment/candidates', data);
    return unwrap<Candidate>(res);
  },
  updateCandidateStage: async (candidateId: string, newStatus: string, reason?: string): Promise<Candidate> => {
    const res = await apiClient.patch(`/recruitment/candidates/${candidateId}/stage`, { new_status: newStatus, reason });
    return unwrap<Candidate>(res);
  },
  getInterviews: async (): Promise<Interview[]> => {
    const res = await apiClient.get('/recruitment/interviews');
    return unwrap<Interview[]>(res);
  },
  scheduleInterview: async (data: Partial<Interview>): Promise<Interview> => {
    const res = await apiClient.post('/recruitment/interviews', data);
    return unwrap<Interview>(res);
  },
  submitInterviewFeedback: async (feedback: any): Promise<any> => {
    const res = await apiClient.post('/recruitment/interviews/feedback', feedback);
    return unwrap<any>(res);
  },
  getOffers: async (): Promise<Offer[]> => {
    const res = await apiClient.get('/recruitment/offers');
    return unwrap<Offer[]>(res);
  },
  createOffer: async (data: Partial<Offer>): Promise<Offer> => {
    const res = await apiClient.post('/recruitment/offers', data);
    return unwrap<Offer>(res);
  },
  convertCandidateToEmployee: async (offerId: string): Promise<any> => {
    const res = await apiClient.post(`/recruitment/offers/${offerId}/convert-employee`);
    return unwrap<any>(res);
  }
};
