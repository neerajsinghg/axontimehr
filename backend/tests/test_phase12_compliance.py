import pytest
import uuid
from httpx import AsyncClient

async def get_authed_headers(client: AsyncClient) -> dict:
    rand_suffix = uuid.uuid4().hex[:6]
    admin_email = f"phase12_admin_{rand_suffix}@axontimehr.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": admin_email,
            "password": "Password123!",
            "first_name": "Phase12",
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
async def test_phase12_compliance_workflow(sync_client: AsyncClient):
    """
    Comprehensive Phase 12 Integration Test for Statutory Compliance, Rules Engine, Tasks, Audits & Privacy.
    """
    headers = await get_authed_headers(sync_client)

    # 1. Test Dashboard Scorecard
    dash_res = await sync_client.get("/api/v1/compliance/dashboard", headers=headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert "compliance_score" in dash_data
    assert "risk_level" in dash_data

    # 2. Test Establishment Creation
    est_req = {
        "name": "Bengaluru Innovation Hub",
        "code": "EST-BLR-02",
        "country_code": "IN",
        "state_code": "KA",
        "city": "Bengaluru",
        "address": "Outer Ring Road"
    }
    est_res = await sync_client.post("/api/v1/compliance/establishments", json=est_req, headers=headers)
    assert est_res.status_code == 201
    est_data = est_res.json()
    assert est_data["code"] == "EST-BLR-02"

    # 3. Test Statutory Registration Creation & Masking
    reg_req = {
        "registration_type": "TAX_ID",
        "registration_number": "AAACX9876K",
        "authority_name": "Income Tax Department India",
        "establishment_id": est_data["id"]
    }
    reg_res = await sync_client.post("/api/v1/compliance/registrations", json=reg_req, headers=headers)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert reg_data["masked_number"] == "******876K"

    # 4. Test Compliance Rules Engine & Effective-Dating
    rule_req = {
        "rule_code": "MIN_WAGE_KA_2026",
        "rule_name": "Karnataka Statutory Minimum Wage Skilled Category",
        "category": "MINIMUM_WAGE",
        "country_code": "IN",
        "state_code": "KA",
        "effective_from": "2026-01-01",
        "rule_config": {"min_basic_wage": 24000.0}
    }
    rule_res = await sync_client.post("/api/v1/compliance/rules", json=rule_req, headers=headers)
    assert rule_res.status_code == 201
    rule_data = rule_res.json()
    assert rule_data["rule_code"] == "MIN_WAGE_KA_2026"

    # 5. Test Pre-Payroll Compliance Precheck Engine
    precheck_res = await sync_client.post("/api/v1/compliance/payroll/precheck", headers=headers)
    assert precheck_res.status_code == 200
    precheck_data = precheck_res.json()
    assert "status" in precheck_data
    assert "total_employees_checked" in precheck_data

    # 6. Test Compliance Task Creation
    task_req = {
        "title": "File Annual Labour Welfare Fund Returns",
        "compliance_type": "LABOUR_FILING",
        "due_date": "2026-12-31",
        "priority": "HIGH"
    }
    task_res = await sync_client.post("/api/v1/compliance/tasks", json=task_req, headers=headers)
    assert task_res.status_code == 201
    assert task_res.json()["status"] == "OPEN"

    # 7. Test Compliance Violation & CAPA
    viol_req = {
        "violation_code": "VIOL-REST-PERIOD-01",
        "category": "WORKING_HOURS",
        "severity": "MEDIUM",
        "description": "Shift assignment violated mandatory 11-hour rest interval rule."
    }
    viol_res = await sync_client.post("/api/v1/compliance/violations", json=viol_req, headers=headers)
    assert viol_res.status_code == 201

    # 8. Test Internal Audit Planner
    audit_req = {
        "audit_title": "ISO 27001 Data Security & Statutory Audit",
        "audit_type": "PRIVACY",
        "auditor_name": "Compliance Assurance Lead",
        "start_date": "2026-11-01",
        "end_date": "2026-11-10"
    }
    audit_res = await sync_client.post("/api/v1/compliance/audits", json=audit_req, headers=headers)
    assert audit_res.status_code == 201

    # 9. Test Privacy Consent & DSR Requests
    dsr_req = {
        "request_type": "DATA_ACCESS",
        "details": "Request personal statutory tax logs extract."
    }
    dsr_res = await sync_client.post("/api/v1/compliance/privacy/dsr", json=dsr_req, headers=headers)
    assert dsr_res.status_code == 201
    assert dsr_res.json()["request_number"].startswith("DSR-")

    # 10. Test Legal Hold Override Creation
    hold_req = {
        "hold_name": "Q4 Pending Regulatory Investigation Hold",
        "reason": "Preserve all statutory logs for regulatory compliance review.",
        "start_date": "2026-09-02"
    }
    hold_res = await sync_client.post("/api/v1/compliance/privacy/legal-holds", json=hold_req, headers=headers)
    assert hold_res.status_code == 201
    assert hold_res.json()["is_active"] is True
