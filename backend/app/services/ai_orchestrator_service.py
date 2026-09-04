import uuid
import time
from typing import Dict, Any, List
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai_intelligence import AIQueryAudit
from app.services.analytics_service import AnalyticsService
from app.services.workforce_service import WorkforceService
from app.services.recruitment_service import RecruitmentService
from app.schemas.ai import AIQueryRequest, AIQueryResponse, AIToolCallTrace

class AIProviderInterface(ABC):
    @abstractmethod
    async def run_query(self, query: str, context_data: Dict[str, Any]) -> str:
        pass

class MockAIProvider(AIProviderInterface):
    async def run_query(self, query: str, context_data: Dict[str, Any]) -> str:
        q_lower = query.lower()
        if "attrition" in q_lower:
            rate = context_data.get("attrition", {}).get("overall_attrition_rate_pct", 4.8)
            return f"The current organizational attrition rate is {rate}%. The highest turnover occurred in Sales & Marketing (8.5%), while Engineering maintains a low 3.2% exit rate."
        elif "headcount" in q_lower or "employee" in q_lower:
            total = context_data.get("executive", {}).get("active_employees", 25)
            gap = context_data.get("workforce_gap", [{}])[0].get("headcount_gap", 12) if context_data.get("workforce_gap") else 12
            return f"Total active headcount is {total} employees. Our Strategic Workforce Plan target is {total + gap}, leaving an active headcount gap of {gap} positions."
        elif "payroll" in q_lower or "cost" in q_lower or "salary" in q_lower:
            cost = context_data.get("payroll", {}).get("gross_payroll_inr", 3850000)
            return f"Monthly gross payroll spend is ₹{cost:,.2f}. Total tax withholdings account for ₹5,70,000 with an average cost per employee of ₹1,54,000."
        elif "position" in q_lower or "job" in q_lower or "recruitment" in q_lower:
            cands = context_data.get("executive", {}).get("candidates_in_pipeline", 8)
            jobs = context_data.get("executive", {}).get("open_positions", 3)
            return f"We currently have {jobs} active open job listings with {cands} candidates actively undergoing screening and interviews in the candidate pipeline."
        else:
            return f"AxonTimeHR Intelligence Insights: Based on tenant parameters, current organizational operations are running at 96.4% attendance efficiency with a 4.2/5.0 average performance rating."

class AIOrchestratorService:
    @staticmethod
    async def process_query(db: AsyncSession, tenant_id: uuid.UUID, user_id: str, request: AIQueryRequest) -> AIQueryResponse:
        start_time = time.time()
        invoked_tools: List[AIToolCallTrace] = []
        context_data: Dict[str, Any] = {}

        q_lower = request.query_text.lower()

        # Step 1: Intent Detection & Authorized Tool Dispatch (NO DIRECT SQL)
        if any(k in q_lower for k in ["headcount", "employee", "joined", "exit", "growth"]):
            t_start = time.time()
            exec_summary = await AnalyticsService.get_executive_summary(db, tenant_id)
            gap_data = await WorkforceService.get_gap_analysis(db, tenant_id)
            context_data["executive"] = exec_summary.model_dump()
            context_data["workforce_gap"] = [g.model_dump() for g in gap_data]
            t_dur = int((time.time() - t_start) * 1000)
            invoked_tools.append(AIToolCallTrace(tool_name="get_headcount_metrics", parameters={"tenant_id": str(tenant_id)}, execution_time_ms=t_dur))

        if any(k in q_lower for k in ["attrition", "turnover", "exits", "leave_rate"]):
            t_start = time.time()
            attr_data = await AnalyticsService.get_attrition_analytics(db, tenant_id)
            context_data["attrition"] = attr_data.model_dump()
            t_dur = int((time.time() - t_start) * 1000)
            invoked_tools.append(AIToolCallTrace(tool_name="get_attrition_metrics", parameters={"tenant_id": str(tenant_id)}, execution_time_ms=t_dur))

        if any(k in q_lower for k in ["payroll", "cost", "salary", "expense", "budget"]):
            t_start = time.time()
            payroll_data = await AnalyticsService.get_labor_cost_analytics(db, tenant_id)
            context_data["payroll"] = payroll_data.model_dump()
            t_dur = int((time.time() - t_start) * 1000)
            invoked_tools.append(AIToolCallTrace(tool_name="get_payroll_summary", parameters={"tenant_id": str(tenant_id)}, execution_time_ms=t_dur))

        if any(k in q_lower for k in ["job", "position", "candidate", "recruitment", "hiring"]):
            t_start = time.time()
            exec_summary = await AnalyticsService.get_executive_summary(db, tenant_id)
            context_data["executive"] = exec_summary.model_dump()
            t_dur = int((time.time() - t_start) * 1000)
            invoked_tools.append(AIToolCallTrace(tool_name="get_recruitment_metrics", parameters={"tenant_id": str(tenant_id)}, execution_time_ms=t_dur))

        if not invoked_tools:
            # Fallback to executive summary tool
            t_start = time.time()
            exec_summary = await AnalyticsService.get_executive_summary(db, tenant_id)
            context_data["executive"] = exec_summary.model_dump()
            t_dur = int((time.time() - t_start) * 1000)
            invoked_tools.append(AIToolCallTrace(tool_name="get_executive_summary", parameters={"tenant_id": str(tenant_id)}, execution_time_ms=t_dur))

        # Step 2: AI Processing via Provider Abstraction Interface
        provider = MockAIProvider()
        answer = await provider.run_query(request.query_text, context_data)

        total_latency = int((time.time() - start_time) * 1000)

        # Step 3: Record AI Audit Log
        audit = AIQueryAudit(
            tenant_id=str(tenant_id),
            user_id=str(user_id),
            query_text=request.query_text,
            response_summary=answer,
            tools_invoked=",".join([t.tool_name for t in invoked_tools]),
            token_count=180,
            latency_ms=total_latency,
            provider="MOCK_PROVIDER",
            model_name="axon-hr-ai-v1"
        )
        db.add(audit)
        await db.commit()

        return AIQueryResponse(
            query_text=request.query_text,
            answer_text=answer,
            tools_invoked=invoked_tools,
            supporting_metrics=context_data,
            provider_used="MOCK_PROVIDER",
            confidence_level="HIGH (98% Authorized Context Alignment)",
            latency_ms=total_latency
        )
