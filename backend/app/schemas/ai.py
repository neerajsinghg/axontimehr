from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class AIQueryRequest(BaseModel):
    query_text: str

class AIToolCallTrace(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    execution_time_ms: int

class AIQueryResponse(BaseModel):
    query_text: str
    answer_text: str
    tools_invoked: List[AIToolCallTrace]
    supporting_metrics: Dict[str, Any]
    provider_used: str
    confidence_level: str
    latency_ms: int
