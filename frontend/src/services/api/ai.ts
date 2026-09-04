import { apiClient } from './client';

export interface AIToolCallTrace {
  tool_name: string;
  parameters: Record<string, any>;
  execution_time_ms: number;
}

export interface AIQueryResponse {
  query_text: string;
  answer_text: string;
  tools_invoked: AIToolCallTrace[];
  supporting_metrics: Record<string, any>;
  provider_used: string;
  confidence_level: string;
  latency_ms: number;
}

const unwrap = <T>(res: any): T => (res && res.data !== undefined ? res.data : res) as T;

export const aiApi = {
  queryAssistant: async (queryText: string): Promise<AIQueryResponse> => {
    const res = await apiClient.post('/ai/query', { query_text: queryText });
    return unwrap<AIQueryResponse>(res);
  }
};
