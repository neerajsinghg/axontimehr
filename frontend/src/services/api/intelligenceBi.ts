import { apiClient } from './client';

export interface AnalyticsMetric {
  id: string;
  tenant_id: string;
  metric_code: string;
  metric_name: string;
  category: string;
  calculation_formula: string;
  unit: string;
  version: number;
}

export interface AnalyticsQueryResult {
  metric_code: string;
  metric_name: string;
  unit: string;
  calculated_value: number;
  formatted_value: string;
  group_breakdown?: Record<string, number>;
  trend_pct?: number;
}

export interface AICopilotChatResponse {
  conversation_id: string;
  message_id: string;
  reply_text: string;
  kpi_cards: Array<{ label: string; value: string; change: string }>;
  chart_type?: string;
  chart_data?: any;
  suggested_questions: string[];
  created_at: string;
}

export interface AnomalyRecord {
  id: string;
  tenant_id: string;
  module: string;
  severity: string;
  title: string;
  description: string;
  anomaly_score: number;
  entity_type?: string;
  entity_id?: string;
  review_status: string;
  resolution_notes?: string;
  created_at: string;
}

export interface WorkforceForecast {
  id: string;
  tenant_id: string;
  forecast_type: string;
  horizon_days: number;
  forecast_results_json: any;
  accuracy_score: number;
  run_date: string;
}

export interface ScenarioModel {
  id: string;
  tenant_id: string;
  scenario_name: string;
  input_parameters_json: any;
  projected_results_json: any;
  created_by_id: string;
  created_at: string;
}

export interface DataQualityIssue {
  id: string;
  tenant_id: string;
  issue_type: string;
  severity: string;
  description: string;
  affected_entity_type: string;
  affected_entity_id: string;
  is_resolved: boolean;
  detected_at: string;
}

export const intelligenceBiApi = {
  getMetricsCatalog: async (): Promise<AnalyticsMetric[]> => {
    const res = await apiClient.get('/analytics/metrics');
    return res.data;
  },

  executeQuery: async (payload: { metric_code: string; aggregation?: string; period?: string }): Promise<AnalyticsQueryResult> => {
    const res = await apiClient.post('/analytics/query', payload);
    return res.data;
  },

  sendCopilotMessage: async (payload: { message_text: string; conversation_id?: string }): Promise<AICopilotChatResponse> => {
    const res = await apiClient.post('/ai/copilot/chat', payload);
    return res.data;
  },

  getAnomalies: async (): Promise<AnomalyRecord[]> => {
    const res = await apiClient.get('/anomalies');
    return res.data;
  },

  reviewAnomaly: async (anomalyId: string, payload: { review_status: string; resolution_notes?: string }): Promise<AnomalyRecord> => {
    const res = await apiClient.patch(`/anomalies/${anomalyId}/review`, payload);
    return res.data;
  },

  getForecasts: async (): Promise<WorkforceForecast[]> => {
    const res = await apiClient.get('/forecasts');
    return res.data;
  },

  createScenario: async (payload: { scenario_name: string; input_parameters: any }): Promise<ScenarioModel> => {
    const res = await apiClient.post('/scenarios', payload);
    return res.data;
  },

  getScenarios: async (): Promise<ScenarioModel[]> => {
    const res = await apiClient.get('/scenarios');
    return res.data;
  },

  getDataQualityIssues: async (): Promise<DataQualityIssue[]> => {
    const res = await apiClient.get('/data-quality/issues');
    return res.data;
  }
};
