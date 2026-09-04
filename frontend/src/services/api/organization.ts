import { apiClient } from './client';

export interface Company {
  id: string;
  name: string;
  code: string;
  domain?: string;
  legal_name?: string;
  display_name?: string;
  tax_id?: string;
  email?: string;
  phone?: string;
  website?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  timezone?: string;
  currency?: string;
  date_format?: string;
  fiscal_year_start?: string;
  status?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Branch {
  id: string;
  organization_id: string;
  name: string;
  code: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  latitude?: number;
  longitude?: number;
  timezone: string;
  phone?: string;
  email?: string;
  status: string;
  is_active: boolean;
}

export interface Department {
  id: string;
  organization_id: string;
  name: string;
  code: string;
  description?: string;
  parent_department_id?: string;
  status: string;
  is_active: boolean;
}

export interface Designation {
  id: string;
  organization_id: string;
  name: string;
  code: string;
  description?: string;
  level: number;
  status: string;
  is_active: boolean;
}

export const organizationApi = {
  // Organization Profile
  getOrganization: async (): Promise<Company> => {
    return (await apiClient.get('/organization')) as unknown as Company;
  },
  updateOrganization: async (data: Partial<Company>): Promise<Company> => {
    return (await apiClient.put('/organization', data)) as unknown as Company;
  },

  // Branches
  getBranches: async (): Promise<Branch[]> => {
    return (await apiClient.get('/branches')) as unknown as Branch[];
  },
  createBranch: async (data: Partial<Branch>): Promise<Branch> => {
    return (await apiClient.post('/branches', data)) as unknown as Branch;
  },
  updateBranch: async (id: string, data: Partial<Branch>): Promise<Branch> => {
    return (await apiClient.put(`/branches/${id}`, data)) as unknown as Branch;
  },
  deleteBranch: async (id: string): Promise<void> => {
    await apiClient.delete(`/branches/${id}`);
  },

  // Departments
  getDepartments: async (): Promise<Department[]> => {
    return (await apiClient.get('/departments')) as unknown as Department[];
  },
  createDepartment: async (data: Partial<Department>): Promise<Department> => {
    return (await apiClient.post('/departments', data)) as unknown as Department;
  },
  updateDepartment: async (id: string, data: Partial<Department>): Promise<Department> => {
    return (await apiClient.put(`/departments/${id}`, data)) as unknown as Department;
  },
  deleteDepartment: async (id: string): Promise<void> => {
    await apiClient.delete(`/departments/${id}`);
  },

  // Designations
  getDesignations: async (): Promise<Designation[]> => {
    return (await apiClient.get('/designations')) as unknown as Designation[];
  },
  createDesignation: async (data: Partial<Designation>): Promise<Designation> => {
    return (await apiClient.post('/designations', data)) as unknown as Designation;
  },
  updateDesignation: async (id: string, data: Partial<Designation>): Promise<Designation> => {
    return (await apiClient.put(`/designations/${id}`, data)) as unknown as Designation;
  },
  deleteDesignation: async (id: string): Promise<void> => {
    await apiClient.delete(`/designations/${id}`);
  },
};
