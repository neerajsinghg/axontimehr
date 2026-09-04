import { apiClient } from './client';

export interface AttendanceLocation {
  id: string;
  tenant_id: string;
  branch_id?: string;
  name: string;
  code: string;
  latitude: number;
  longitude: number;
  radius_meters: number;
  accuracy_requirement: number;
  geofence_type: 'CIRCULAR' | 'POLYGON';
  coordinates?: any;
  status: 'ACTIVE' | 'INACTIVE' | 'ARCHIVED';
  created_at: string;
  updated_at: string;
}

export interface AttendanceLocationPolicy {
  id: string;
  tenant_id: string;
  location_required: boolean;
  geofence_enabled: boolean;
  allowed_radius: number;
  minimum_accuracy: number;
  location_freshness_seconds: number;
  allow_outside_geofence: boolean;
  outside_geofence_action: 'REJECT' | 'ALLOW_WITH_WARNING' | 'REQUIRE_APPROVAL' | 'RECORD_EXCEPTION';
  selfie_required: boolean;
  verification_failure_action: 'REJECT' | 'REQUIRE_REVIEW' | 'RECORD_EXCEPTION';
}

export interface LocationValidateResponse {
  is_valid: boolean;
  status_code: string;
  distance_meters: number;
  allowed_radius: number;
  message: string;
  location_id?: string;
  location_name?: string;
}

export interface SelfieUploadResponse {
  verification_id: string;
  status: string;
  score: number;
  message: string;
}

export interface AttendanceExceptionItem {
  attendance_id: string;
  employee_id: string;
  employee_name: string;
  attendance_date: string;
  status: string;
  location_status: string;
  verification_status: string;
  latitude?: number;
  longitude?: number;
  accuracy?: number;
  distance_meters?: number;
  verification_id?: string;
  remarks?: string;
  created_at: string;
}

export const locationApi = {
  getLocations: async (): Promise<AttendanceLocation[]> => {
    return (await apiClient.get('/attendance/locations')) as unknown as AttendanceLocation[];
  },

  createLocation: async (payload: {
    name: string;
    code: string;
    latitude: number;
    longitude: number;
    radius_meters: number;
    accuracy_requirement: number;
    branch_id?: string;
  }): Promise<AttendanceLocation> => {
    return (await apiClient.post('/attendance/locations', payload)) as unknown as AttendanceLocation;
  },

  updateLocation: async (id: string, payload: Partial<AttendanceLocation>): Promise<AttendanceLocation> => {
    return (await apiClient.put(`/attendance/locations/${id}`, payload)) as unknown as AttendanceLocation;
  },

  deleteLocation: async (id: string): Promise<void> => {
    await apiClient.delete(`/attendance/locations/${id}`);
  },

  getPolicy: async (): Promise<AttendanceLocationPolicy> => {
    return (await apiClient.get('/attendance/location-policies')) as unknown as AttendanceLocationPolicy;
  },

  updatePolicy: async (payload: Partial<AttendanceLocationPolicy>): Promise<AttendanceLocationPolicy> => {
    return (await apiClient.put('/attendance/location-policies', payload)) as unknown as AttendanceLocationPolicy;
  },

  validateLocation: async (payload: {
    latitude: number;
    longitude: number;
    accuracy: number;
    captured_at?: string;
  }): Promise<LocationValidateResponse> => {
    return (await apiClient.post('/attendance/location/validate', payload)) as unknown as LocationValidateResponse;
  },

  uploadSelfie: async (file: File): Promise<SelfieUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    return (await apiClient.post('/attendance/verification/upload-selfie', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })) as unknown as SelfieUploadResponse;
  },

  getExceptions: async (page = 1, limit = 10): Promise<{ data: AttendanceExceptionItem[]; total: number }> => {
    return (await apiClient.get('/attendance/exceptions', { params: { page, limit } })) as unknown as { data: AttendanceExceptionItem[]; total: number };
  }
};
