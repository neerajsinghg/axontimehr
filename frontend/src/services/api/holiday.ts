import { apiClient } from './client';

export interface HolidayCalendar {
  id: string;
  tenant_id: string;
  code: string;
  name: string;
  year: number;
  organization_id?: string;
  branch_id?: string;
  status: 'ACTIVE' | 'INACTIVE';
  total_holidays: number;
  created_at: string;
  updated_at: string;
}

export interface Holiday {
  id: string;
  tenant_id: string;
  calendar_id: string;
  holiday_date: string;
  holiday_name: string;
  holiday_type: 'MANDATORY' | 'OPTIONAL' | 'RESTRICTED';
  branch_id?: string;
  description?: string;
  status: 'ACTIVE' | 'INACTIVE';
  created_at: string;
}

export const holidayApi = {
  getCalendars: async (year?: number): Promise<HolidayCalendar[]> => {
    return apiClient.get('/holidays/calendars', { params: { year } });
  },
  createCalendar: async (data: Partial<HolidayCalendar>): Promise<HolidayCalendar> => {
    return apiClient.post('/holidays/calendars', data);
  },
  createHoliday: async (data: Partial<Holiday>): Promise<Holiday> => {
    return apiClient.post('/holidays', data);
  }
};
