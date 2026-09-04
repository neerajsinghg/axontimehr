import pytest
import uuid
from httpx import AsyncClient

async def get_authed_headers(client: AsyncClient) -> dict:
    rand_suffix = uuid.uuid4().hex[:6]
    admin_email = f"phase11_user_{rand_suffix}@axontimehr.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": admin_email,
            "password": "Password123!",
            "first_name": "Phase11",
            "last_name": "User"
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
async def test_phase11_employee_experience_workflow(sync_client: AsyncClient):
    """
    Comprehensive Phase 11 Integration Test for ESS, MSS, Helpdesk, Documents & Communications.
    """
    headers = await get_authed_headers(sync_client)

    # 1. Test ESS Dashboard Summary
    dash_res = await sync_client.get("/api/v1/employee-experience/me/dashboard", headers=headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert "employee_id" in dash_data
    assert "leave_balance_days" in dash_data

    # 2. Test Self Profile Update
    prof_update = {
        "personal_email": "updated.employee@example.com",
        "personal_phone": "+91 9876543210"
    }
    upd_res = await sync_client.put("/api/v1/employee-experience/me/profile", json=prof_update, headers=headers)
    assert upd_res.status_code == 200

    # 3. Test Profile Change Request
    change_req = {
        "field_name": "emergency_contact",
        "new_value": "Parent: +91 9988776655",
        "reason": "Updated primary emergency contact phone number"
    }
    cr_res = await sync_client.post("/api/v1/employee-experience/me/profile/change-requests", json=change_req, headers=headers)
    assert cr_res.status_code == 200
    cr_data = cr_res.json()
    assert cr_data["status"] == "PENDING"

    # 4. Test Document Templates & HR Letter Generation
    tmpl_res = await sync_client.get("/api/v1/employee-experience/me/document-templates", headers=headers)
    assert tmpl_res.status_code == 200
    templates = tmpl_res.json()
    assert len(templates) > 0
    target_tmpl_id = templates[0]["id"]

    gen_req = {
        "template_id": target_tmpl_id,
        "employee_id": dash_data["employee_id"]
    }
    gen_res = await sync_client.post("/api/v1/employee-experience/me/documents/letters/generate", json=gen_req, headers=headers)
    assert gen_res.status_code == 200
    gen_data = gen_res.json()
    assert "snapshot_html" in gen_data
    assert gen_data["letter_number"].startswith("LTR-")

    # 5. Test HR Policies & Acknowledgements
    pol_res = await sync_client.get("/api/v1/employee-experience/me/policies", headers=headers)
    assert pol_res.status_code == 200
    policies = pol_res.json()
    assert len(policies) > 0
    target_pol_id = policies[0]["id"]

    ack_res = await sync_client.post(f"/api/v1/employee-experience/me/policies/{target_pol_id}/acknowledge", headers=headers)
    assert ack_res.status_code == 200
    assert ack_res.json()["status"] == "success"

    # 6. Test HR Helpdesk Support Ticket
    ticket_req = {
        "category": "PAYROLL",
        "priority": "HIGH",
        "subject": "Tax deduction query for Q3 bonus",
        "description": "Please clarify TDS tax withholding percentage calculation."
    }
    t_res = await sync_client.post("/api/v1/employee-experience/me/helpdesk/tickets", json=ticket_req, headers=headers)
    assert t_res.status_code == 200
    t_data = t_res.json()
    assert t_data["ticket_number"].startswith("TICK-")

    # 7. Test Ticket Comment
    comm_req = {"comment_text": "Attached proof of investments for tax declaration."}
    comm_res = await sync_client.post(f"/api/v1/employee-experience/me/helpdesk/tickets/{t_data['id']}/comments", json=comm_req, headers=headers)
    assert comm_res.status_code == 200

    # 8. Test Announcements & Unified Tasks
    ann_res = await sync_client.get("/api/v1/employee-experience/me/announcements", headers=headers)
    assert ann_res.status_code == 200
    assert len(ann_res.json()) > 0

    task_res = await sync_client.get("/api/v1/employee-experience/me/tasks", headers=headers)
    assert task_res.status_code == 200
    assert len(task_res.json()) > 0
