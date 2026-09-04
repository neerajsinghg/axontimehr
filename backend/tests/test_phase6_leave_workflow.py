import pytest
import uuid
from datetime import date, datetime, timedelta, timezone
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_phase6_leave_and_workflow_complete_flow():
    """Verify complete Phase 6 flow: Leave Types, Policy, Leave Request, Working Days, Approval Inbox, Regularization & Security."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Register Tenant Admin A
        tenant_name = f"Tenant P6 {uuid.uuid4().hex}"
        admin_email = f"p6_admin_{uuid.uuid4().hex[:6]}@tenant-a.com"
        reg_res = await client.post(
            "/api/v1/auth/register",
            json={
                "email": admin_email,
                "password": "Password123!",
                "first_name": "Admin",
                "last_name": "P6",
                "company_name": tenant_name
            }
        )
        assert reg_res.status_code == 201
        
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": admin_email, "password": "Password123!"}
        )
        assert login_res.status_code == 200
        admin_token = login_res.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 2. Create Leave Types
        cl_res = await client.post(
            "/api/v1/leaves/types",
            headers=admin_headers,
            json={
                "code": f"CL_{uuid.uuid4().hex[:4]}",
                "name": "Casual Leave",
                "color_code": "#3B82F6",
                "paid": True,
                "allow_half_day": True,
                "status": "ACTIVE"
            }
        )
        assert cl_res.status_code == 201, f"Failed creating LeaveType: {cl_res.text}"
        cl_type_id = cl_res.json()["id"]

        # 3. Create Leave Policy
        policy_res = await client.post(
            "/api/v1/leaves/policies",
            headers=admin_headers,
            json={
                "leave_type_id": cl_type_id,
                "name": "Standard Casual Leave Policy",
                "annual_entitlement": 12.0,
                "accrual_frequency": "MONTHLY",
                "accrual_amount": 1.0,
                "carry_forward_allowed": True,
                "carry_forward_limit": 5.0
            }
        )
        assert policy_res.status_code == 201

        # 4. Check Initial Employee Balances
        bal_res = await client.get("/api/v1/leaves/balance", headers=admin_headers)
        assert bal_res.status_code == 200
        balances = bal_res.json()
        assert len(balances) >= 1
        cl_bal = next(b for b in balances if b["leave_type_id"] == cl_type_id)
        assert cl_bal["available"] == 12.0

        # 5. Create Holiday Calendar & Holiday
        cal_res = await client.post(
            "/api/v1/holidays/calendars",
            headers=admin_headers,
            json={
                "code": f"HOL_CAL_{uuid.uuid4().hex[:4]}",
                "name": "2026 Company Holidays",
                "year": 2026
            }
        )
        assert cal_res.status_code == 201
        cal_id = cal_res.json()["id"]

        holiday_date = "2026-09-10"
        h_res = await client.post(
            "/api/v1/holidays/",
            headers=admin_headers,
            json={
                "calendar_id": cal_id,
                "holiday_date": holiday_date,
                "holiday_name": "Founders Day",
                "holiday_type": "MANDATORY"
            }
        )
        assert h_res.status_code == 201, f"Create holiday failed: {h_res.status_code} {h_res.text}"

        # 6. Register Employee User B (Requester) in same Tenant A
        emp_email = f"p6_emp_{uuid.uuid4().hex[:6]}@tenant-a.com"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": emp_email,
                "password": "Password123!",
                "first_name": "John",
                "last_name": "Doe",
                "company_name": tenant_name
            }
        )
        login_emp = await client.post(
            "/api/v1/auth/login",
            json={"email": emp_email, "password": "Password123!"}
        )
        emp_token = login_emp.json()["data"]["access_token"]
        emp_headers = {"Authorization": f"Bearer {emp_token}"}

        # 7. Employee Submits Leave Request (2026-09-09 to 2026-09-11: 3 total days, Sep 10 is Holiday -> 2 Working Days)
        leave_req_res = await client.post(
            "/api/v1/leaves/requests",
            headers=emp_headers,
            json={
                "leave_type_id": cl_type_id,
                "start_date": "2026-09-09",
                "end_date": "2026-09-11",
                "duration_type": "FULL_DAY",
                "reason": "Family function"
            }
        )
        assert leave_req_res.status_code == 201, f"Failed submitting leave: {leave_req_res.text}"
        leave_req_data = leave_req_res.json()
        leave_req_id = leave_req_data["id"]
        instance_id = leave_req_data["approval_instance_id"]
        assert leave_req_data["working_days_count"] == 2.0
        assert leave_req_data["holiday_days_count"] == 1.0
        assert leave_req_data["status"] == "PENDING"

        # 8. Verify Employee Cannot Approve Own Request (Self-Approval Blocked)
        self_app_res = await client.post(
            f"/api/v1/approvals/{instance_id}/action",
            headers=emp_headers,
            json={"action": "APPROVE", "comments": "Self approval test"}
        )
        assert self_app_res.status_code == 403

        # 9. Manager / Admin Views Inbox & Approves Request
        inbox_res = await client.get("/api/v1/approvals/inbox", headers=admin_headers)
        assert inbox_res.status_code == 200
        inbox_items = inbox_res.json()
        assert len(inbox_items) >= 1
        target_item = next(i for i in inbox_items if i["instance_id"] == instance_id)
        assert target_item["entity_type"] == "LEAVE_REQUEST"

        approve_res = await client.post(
            f"/api/v1/approvals/{instance_id}/action",
            headers=admin_headers,
            json={"action": "APPROVE", "comments": "Approved by Admin"}
        )
        assert approve_res.status_code == 200
        assert approve_res.json()["status"] == "APPROVED"

        # 10. Check Employee Balance After Approval (Used = 2.0, Available = 10.0)
        bal_res_after = await client.get("/api/v1/leaves/balance", headers=emp_headers)
        emp_balances = bal_res_after.json()
        emp_cl = next(b for b in emp_balances if b["leave_type_id"] == cl_type_id)
        assert emp_cl["used"] == 2.0
        assert emp_cl["available"] == 10.0

        # 11. Employee Cancels Approved Leave -> Restores Balance to 12.0
        cancel_res = await client.post(
            f"/api/v1/leaves/requests/{leave_req_id}/cancel",
            headers=emp_headers
        )
        assert cancel_res.status_code == 200
        assert cancel_res.json()["status"] == "CANCELLED"

        bal_res_restored = await client.get("/api/v1/leaves/balance", headers=emp_headers)
        emp_cl_restored = next(b for b in bal_res_restored.json() if b["leave_type_id"] == cl_type_id)
        assert emp_cl_restored["available"] == 12.0

        # 12. Attendance Regularization Flow
        now_utc = datetime.now(timezone.utc)
        check_in = (now_utc - timedelta(hours=8)).isoformat()
        check_out = now_utc.isoformat()

        reg_res = await client.post(
            "/api/v1/regularizations/",
            headers=emp_headers,
            json={
                "attendance_date": "2026-09-01",
                "requested_check_in": check_in,
                "requested_check_out": check_out,
                "reason": "Forgot badge check in"
            }
        )
        assert reg_res.status_code == 201
        reg_id = reg_res.json()["id"]
        reg_inst_id = reg_res.json()["approval_instance_id"]

        # Admin Approves Regularization
        reg_app_res = await client.post(
            f"/api/v1/approvals/{reg_inst_id}/action",
            headers=admin_headers,
            json={"action": "APPROVE", "comments": "Regularization verified"}
        )
        assert reg_app_res.status_code == 200
        assert reg_app_res.json()["status"] == "APPROVED"


@pytest.mark.asyncio
async def test_phase6_cross_tenant_isolation():
    """Verify Tenant B cannot access, approve, or modify Tenant A's leaves or holiday calendars."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register User A (Tenant A)
        user_a = f"t6_a_{uuid.uuid4().hex[:6]}@tenant-a.com"
        await client.post("/api/v1/auth/register", json={"email": user_a, "password": "Password123!", "first_name": "A", "last_name": "User"})
        login_a = await client.post("/api/v1/auth/login", json={"email": user_a, "password": "Password123!"})
        headers_a = {"Authorization": f"Bearer {login_a.json()['data']['access_token']}"}

        # Register User B (Tenant B)
        user_b = f"t6_b_{uuid.uuid4().hex[:6]}@tenant-b.com"
        await client.post("/api/v1/auth/register", json={"email": user_b, "password": "Password123!", "first_name": "B", "last_name": "User"})
        login_b = await client.post("/api/v1/auth/login", json={"email": user_b, "password": "Password123!"})
        headers_b = {"Authorization": f"Bearer {login_b.json()['data']['access_token']}"}

        # Assign distinct Company (Tenant B) to User B
        from app.db.session import AsyncSessionLocal
        from app.models.organization import Company
        from app.models.user import User as UserModel
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            comp_b = Company(name="Tenant B Corp", code=f"TB-{uuid.uuid4().hex[:6]}")
            db.add(comp_b)
            await db.flush()
            user_b_db = (await db.execute(select(UserModel).where(UserModel.email == user_b))).scalar_one()
            user_b_db.tenant_id = comp_b.id
            await db.commit()

        # Tenant A Creates Leave Type
        lt_a = await client.post(
            "/api/v1/leaves/types",
            headers=headers_a,
            json={"code": f"CL_{uuid.uuid4().hex[:4]}", "name": "Tenant A CL", "color_code": "#10B981"}
        )
        assert lt_a.status_code == 201

        # Tenant B Lists Leave Types -> Cannot see Tenant A's leave type
        lt_b_list = await client.get("/api/v1/leaves/types", headers=headers_b)
        assert lt_b_list.status_code == 200
        codes_b = [t["code"] for t in lt_b_list.json()]
        assert lt_a.json()["code"] not in codes_b
