import pytest
import uuid
from httpx import AsyncClient

async def get_authed_headers(client: AsyncClient) -> dict:
    rand_suffix = uuid.uuid4().hex[:6]
    admin_email = f"phase13_admin_{rand_suffix}@axontimehr.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": admin_email,
            "password": "Password123!",
            "first_name": "Phase13",
            "last_name": "Admin"
        }
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_email,
            "password": "Password123!"
        }
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_phase13_intelligence_bi_workflow(sync_client: AsyncClient):
    """
    Comprehensive Phase 13 Integration Test for Metric Catalog, AI Copilot, Anomalies, Forecasts & Data Quality.
    """
    headers = await get_authed_headers(sync_client)

    # 1. Test Centralized Metric Catalog
    cat_res = await sync_client.get("/api/v1/analytics/metrics", headers=headers)
    assert cat_res.status_code == 200
    metrics = cat_res.json()
    assert len(metrics) > 0

    # 2. Test Metric Query Execution Engine
    q_req = {
        "metric_code": "PAYROLL_COST_MONTHLY",
        "aggregation": "SUM",
        "period": "current_month"
    }
    q_res = await sync_client.post("/api/v1/analytics/query", json=q_req, headers=headers)
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert q_data["metric_code"] == "PAYROLL_COST_MONTHLY"
    assert q_data["calculated_value"] > 0

    # 3. Test AxonTime AI Copilot Conversational Chat
    chat_req = {
        "message_text": "What is our current monthly payroll expenditure and active headcount?"
    }
    chat_res = await sync_client.post("/api/v1/ai/copilot/chat", json=chat_req, headers=headers)
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert "conversation_id" in chat_data
    assert len(chat_data["reply_text"]) > 0
    assert len(chat_data["kpi_cards"]) > 0

    # 4. Test Anomaly Detection Center
    anom_res = await sync_client.get("/api/v1/anomalies", headers=headers)
    assert anom_res.status_code == 200
    anomalies = anom_res.json()
    assert len(anomalies) > 0
    target_anom_id = anomalies[0]["id"]

    # 5. Test Anomaly Review Workflow
    rev_req = {
        "review_status": "CONFIRMED",
        "resolution_notes": "Confirmed overtime anomaly during Q3 release push."
    }
    rev_res = await sync_client.patch(f"/api/v1/anomalies/{target_anom_id}/review", json=rev_req, headers=headers)
    assert rev_res.status_code == 200
    assert rev_res.json()["review_status"] == "CONFIRMED"

    # 6. Test 12-Month Workforce Forecasts
    fore_res = await sync_client.get("/api/v1/forecasts", headers=headers)
    assert fore_res.status_code == 200
    forecasts = fore_res.json()
    assert len(forecasts) > 0

    # 7. Test What-If Scenario Planner
    scen_req = {
        "scenario_name": "Engineering Team 20-Person Expansion",
        "input_parameters": {"additional_hires": 20, "average_salary_inr": 2000000}
    }
    scen_res = await sync_client.post("/api/v1/scenarios", json=scen_req, headers=headers)
    assert scen_res.status_code == 201
    scen_data = scen_res.json()
    assert scen_data["scenario_name"] == "Engineering Team 20-Person Expansion"
    assert "projected_results_json" in scen_data

    # 8. Test Data Quality Audit Diagnostics
    dq_res = await sync_client.get("/api/v1/data-quality/issues", headers=headers)
    assert dq_res.status_code == 200
    issues = dq_res.json()
    assert len(issues) > 0
