import { apiClient } from './client';

export interface Shift {
  id: string;
  tenant_id: string;
  code: string;
  name: string;
  shift_type: string;
  start_time: string;
  end_time: string;
  grace_period_minutes: number;
  late_threshold_minutes: number;
  early_exit_threshold_minutes: number;
  minimum_work_minutes: number;
  break_duration_minutes: number;
  is_overnight: boolean;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface AttendanceEvent {
  id: string;
  event_type: 'CHECK_IN' | 'CHECK_OUT' | 'BREAK_START' | 'BREAK_END';
  event_time: string;
  source: string;
  device_reference?: string;
  location_reference?: string;
  verification_reference?: string;
  remarks?: string;
}

export interface AttendanceRecord {
  id: string;
  tenant_id: string;
  employee_id: string;
  shift_id?: string;
  attendance_date: string;
  status: string;
  first_check_in?: string;
  last_check_out?: string;
  total_work_minutes: number;
  total_break_minutes: number;
  overtime_minutes: number;
  late_minutes: number;
  early_exit_minutes: number;
  worked_minutes: number;
  location_status?: string;
  verification_status?: string;
  has_exception?: boolean;
  attendance_source: string;
  remarks?: string;
  created_at: string;
  updated_at: string;
  shift?: Shift;
  events?: AttendanceEvent[];
}

export interface DailyAttendanceStatus {
  today_date: string;
  is_checked_in: boolean;
  is_checked_out: boolean;
  current_status: string;
  first_check_in?: string;
  last_check_out?: string;
  worked_minutes: number;
  shift?: Shift;
}

export interface AttendanceListResponse {
  success: boolean;
  data: AttendanceRecord[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface AttendanceDashboardMetrics {
  success: boolean;
  today_date: string;
  total_employees: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  on_leave_count: number;
  wfh_count: number;
  half_day_count: number;
  week_off_count: number;
  holiday_count: number;
}

export interface RegularizationRequest {
  id: string;
  tenant_id: string;
  employee_id: string;
  attendance_date: string;
  requested_check_in?: string;
  requested_check_out?: string;
  reason: string;
  status: string;
  approved_by_id?: string;
  approved_at?: string;
  rejection_reason?: string;
  created_at: string;
}

export interface Holiday {
  id: string;
  tenant_id: string;
  branch_id?: string;
  holiday_name: string;
  holiday_date: string;
  holiday_type: string;
  description?: string;
  status: string;
  created_at: string;
}

export const attendanceApi = {
  // Check-In / Check-Out
  checkIn: async (source: string = 'WEB', remarks?: string): Promise<AttendanceRecord> => {
    return (await apiClient.post('/attendance/check-in', { source, remarks })) as unknown as AttendanceRecord;
  },

  checkOut: async (source: string = 'WEB', remarks?: string): Promise<AttendanceRecord> => {
    return (await apiClient.post('/attendance/check-out', { source, remarks })) as unknown as AttendanceRecord;
  },

  getTodayStatus: async (): Promise<DailyAttendanceStatus> => {
    return (await apiClient.get('/attendance/today')) as unknown as DailyAttendanceStatus;
  },

  getMyHistory: async (page: number = 1, limit: number = 10, startDate?: string, endDate?: string): Promise<AttendanceListResponse> => {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('limit', limit.toString());
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return (await apiClient.get(`/attendance/my?${params.toString()}`)) as unknown as AttendanceListResponse;
  },

  getDashboardMetrics: async (): Promise<AttendanceDashboardMetrics> => {
    return (await apiClient.get('/attendance/dashboard')) as unknown as AttendanceDashboardMetrics;
  },

  // Regularization
  requestRegularization: async (attendance_date: string, reason: string, requested_check_in?: string, requested_check_out?: string): Promise<RegularizationRequest> => {
    return (await apiClient.post('/attendance/regularization', {
      attendance_date,
      reason,
      requested_check_in,
      requested_check_out,
    })) as unknown as RegularizationRequest;
  },

  approveRegularization: async (id: string): Promise<RegularizationRequest> => {
    return (await apiClient.post(`/attendance/regularization/${id}/approve`)) as unknown as RegularizationRequest;
  },

  // Shifts
  getShifts: async (): Promise<Shift[]> => {
    return (await apiClient.get('/shifts')) as unknown as Shift[];
  },

  createShift: async (shiftData: Partial<Shift>): Promise<Shift> => {
    return (await apiClient.post('/shifts', shiftData)) as unknown as Shift;
  },

  assignShift: async (employeeId: string, shiftId: string, effectiveFrom: string, weeklyOffs: string[] = ['SUNDAY']): Promise<any> => {
    return (await apiClient.post(`/employees/${employeeId}/shift`, {
      shift_id: shiftId,
      effective_from: effectiveFrom,
      weekly_offs: weeklyOffs,
    }));
  },

  // Holidays
  getHolidays: async (branchId?: string): Promise<Holiday[]> => {
    const url = branchId ? `/holidays?branch_id=${branchId}` : '/holidays';
    return (await apiClient.get(url)) as unknown as Holiday[];
  },

  createHoliday: async (holidayData: Partial<Holiday>): Promise<Holiday> => {
    return (await apiClient.post('/holidays', holidayData)) as unknown as Holiday;
  },
};
