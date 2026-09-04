import { apiClient } from './client';

export interface DepartmentInfo {
  id: string;
  name: string;
  code: string;
}

export interface DesignationInfo {
  id: string;
  name: string;
  code: string;
}

export interface BranchInfo {
  id: string;
  name: string;
  code: string;
  city?: string;
}

export interface ManagerSummary {
  id: string;
  employee_id: string;
  first_name: string;
  last_name: string;
  email: string;
}

export interface EmployeeDocument {
  id: string;
  organization_id: string;
  employee_id: string;
  document_type: string;
  file_name: string;
  storage_key: string;
  mime_type?: string;
  file_size?: number;
  uploaded_at: string;
  verification_status: string;
  expiry_date?: string;
}

export interface Employee {
  id: string;
  organization_id: string;
  employee_id: string;
  first_name: string;
  middle_name?: string;
  last_name: string;
  display_name?: string;
  gender?: string;
  date_of_birth?: string;
  email: string;
  personal_email?: string;
  phone?: string;
  personal_phone?: string;
  emergency_contact?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  joining_date: string;
  date_of_confirmation?: string;
  date_of_leaving?: string;
  employment_type: string;
  employee_category?: string;
  status: string;
  avatar_url?: string;
  department?: DepartmentInfo;
  designation?: DesignationInfo;
  branch?: BranchInfo;
  manager?: ManagerSummary;
}

export interface EmployeeListResponse {
  success: boolean;
  data: Employee[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  request_id?: string;
}

export interface DepartmentStat {
  department_name: string;
  count: number;
}

export interface EmployeeStatsResponse {
  success: boolean;
  total_employees: number;
  active_employees: number;
  on_leave_employees: number;
  inactive_employees: number;
  departments_count: number;
  by_department: DepartmentStat[];
  request_id?: string;
}

export const employeeApi = {
  getEmployees: async (
    page: number = 1,
    limit: number = 10,
    search?: string,
    status?: string,
    departmentId?: string,
    branchId?: string,
    designationId?: string
  ): Promise<EmployeeListResponse> => {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('limit', limit.toString());
    if (search) params.append('q', search);
    if (status && status !== 'ALL') params.append('status', status);
    if (departmentId) params.append('department_id', departmentId);
    if (branchId) params.append('branch_id', branchId);
    if (designationId) params.append('designation_id', designationId);

    return (await apiClient.get(`/employees?${params.toString()}`)) as unknown as EmployeeListResponse;
  },

  getEmployee: async (id: string): Promise<Employee> => {
    return (await apiClient.get(`/employees/${id}`)) as unknown as Employee;
  },

  createEmployee: async (data: Partial<Employee> & { create_user_account?: boolean; user_password?: string }): Promise<Employee> => {
    return (await apiClient.post('/employees', data)) as unknown as Employee;
  },

  updateEmployee: async (id: string, data: Partial<Employee>): Promise<Employee> => {
    return (await apiClient.put(`/employees/${id}`, data)) as unknown as Employee;
  },

  updateStatus: async (id: string, status: string, dateOfLeaving?: string): Promise<Employee> => {
    return (await apiClient.patch(`/employees/${id}/status`, { status, date_of_leaving: dateOfLeaving })) as unknown as Employee;
  },

  deleteEmployee: async (id: string): Promise<void> => {
    await apiClient.delete(`/employees/${id}`);
  },

  getStats: async (): Promise<EmployeeStatsResponse> => {
    return (await apiClient.get('/employees/stats')) as unknown as EmployeeStatsResponse;
  },

  // Documents
  getDocuments: async (employeeId: string): Promise<EmployeeDocument[]> => {
    return (await apiClient.get(`/employees/${employeeId}/documents`)) as unknown as EmployeeDocument[];
  },

  addDocument: async (employeeId: string, doc: Partial<EmployeeDocument>): Promise<EmployeeDocument> => {
    return (await apiClient.post(`/employees/${employeeId}/documents`, doc)) as unknown as EmployeeDocument;
  },

  deleteDocument: async (employeeId: string, documentId: string): Promise<void> => {
    await apiClient.delete(`/employees/${employeeId}/documents/${documentId}`);
  },
};
