import uuid
import pytest
from datetime import datetime, date, time, timedelta, timezone
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_phase4_attendance_engine_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        rand_suffix = uuid.uuid4().hex[:6]
        admin_email = f"att_admin_{rand_suffix}@axontimehr.com"

        # 1. Register & Login Admin User
        reg_res = await client.post(
            "/api/v1/auth/register",
            json={
                "email": admin_email,
                "password": "Password123!",
                "first_name": "Attendance",
                "last_name": "Admin"
            }
        )
        assert reg_res.status_code == 201

        from app.db.session import AsyncSessionLocal
        from app.models.organization import Company
        from app.models.user import User
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            comp_p4 = Company(name=f"Tenant P4 Corp {rand_suffix}", code=f"TP4-{rand_suffix}")
            db.add(comp_p4)
            await db.flush()
            user = (await db.execute(select(User).where(User.email == admin_email))).scalar_one()
            user.tenant_id = comp_p4.id
            await db.commit()

        login_res = await client.post(
            "/api/v1/auth/login",
            json={
                "email": admin_email,
                "password": "Password123!"
            }
        )
        assert login_res.status_code == 200
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Shift Master (General Shift 09:00 - 18:00)
        shift_res = await client.post(
            "/api/v1/shifts",
            headers=headers,
            json={
                "code": f"GEN-{rand_suffix}",
                "name": "General Day Shift",
                "shift_type": "FIXED",
                "start_time": "09:00:00",
                "end_time": "18:00:00",
                "grace_period_minutes": 15,
                "late_threshold_minutes": 30,
                "early_exit_threshold_minutes": 15,
                "minimum_work_minutes": 480,
                "break_duration_minutes": 60,
                "is_overnight": False
            }
        )
        assert shift_res.status_code == 201
        shift_id = shift_res.json()["id"]

        # Duplicate Shift Code Rejection Test
        dup_shift_res = await client.post(
            "/api/v1/shifts",
            headers=headers,
            json={
                "code": f"GEN-{rand_suffix}",
                "name": "Duplicate Shift",
                "start_time": "09:00:00",
                "end_time": "18:00:00"
            }
        )
        assert dup_shift_res.status_code == 400

        # 3. Create Employee linked to Admin user
        emp_res = await client.post(
            "/api/v1/employees",
            headers=headers,
            json={
                "employee_id": f"EMP-ATT-{rand_suffix}",
                "first_name": "Attendance",
                "last_name": "User",
                "email": admin_email,
                "joining_date": "2024-01-01"
            }
        )
        assert emp_res.status_code == 201, f"emp_res failed: {emp_res.status_code} {emp_res.text}"
        emp_id = emp_res.json()["id"]

        # 4. Assign Shift Roster to Employee
        assign_res = await client.post(
            f"/api/v1/employees/{emp_id}/shift",
            headers=headers,
            json={
                "shift_id": shift_id,
                "effective_from": "2024-01-01",
                "weekly_offs": ["SUNDAY"]
            }
        )
        assert assign_res.status_code == 201, f"assign_res failed: {assign_res.status_code} {assign_res.text}"

        # 5. Verify Check-in Punch
        check_in_res = await client.post(
            "/api/v1/attendance/check-in",
            headers=headers,
            json={
                "source": "WEB",
                "remarks": "Morning Check-In"
            }
        )
        assert check_in_res.status_code == 200, f"check_in_res failed: {check_in_res.status_code} {check_in_res.text}"
        att_data = check_in_res.json()
        assert att_data["first_check_in"] is not None
        assert att_data["last_check_out"] is None

        # 6. Verify Duplicate Check-In Protection (Idempotent rejection)
        dup_check_in = await client.post(
            "/api/v1/attendance/check-in",
            headers=headers,
            json={"source": "WEB"}
        )
        assert dup_check_in.status_code == 400, f"dup_check_in failed: {dup_check_in.status_code} {dup_check_in.text}"
        assert dup_check_in.json()["detail"]["code"] == "ALREADY_CHECKED_IN"

        # 7. Verify Check-out Punch
        check_out_res = await client.post(
            "/api/v1/attendance/check-out",
            headers=headers,
            json={
                "source": "WEB",
                "remarks": "Evening Check-Out"
            }
        )
        assert check_out_res.status_code == 200, f"check_out_res failed: {check_out_res.status_code} {check_out_res.text}"
        out_data = check_out_res.json()
        assert out_data["last_check_out"] is not None

        # 8. Verify Invalid Check-out Protection (without active check-in)
        invalid_checkout = await client.post(
            "/api/v1/attendance/check-out",
            headers=headers,
            json={"source": "WEB"}
        )
        assert invalid_checkout.status_code == 400, f"invalid_checkout failed: {invalid_checkout.status_code} {invalid_checkout.text}"
        assert invalid_checkout.json()["detail"]["code"] == "INVALID_ATTENDANCE_STATE"

        # 9. Verify Today Status Endpoint
        today_res = await client.get("/api/v1/attendance/today", headers=headers)
        assert today_res.status_code == 200
        assert today_res.json()["is_checked_out"] is True

        # 10. Verify Attendance Dashboard Aggregation
        dash_res = await client.get("/api/v1/attendance/dashboard", headers=headers)
        assert dash_res.status_code == 200
        assert dash_res.json()["total_employees"] >= 1

        # 11. Request & Approve Attendance Regularization
        reg_req = await client.post(
            "/api/v1/attendance/regularization",
            headers=headers,
            json={
                "attendance_date": "2024-02-01",
                "requested_check_in": "2024-02-01T09:00:00Z",
                "requested_check_out": "2024-02-01T18:00:00Z",
                "reason": "Forgot badge punch"
            }
        )
        assert reg_req.status_code == 200
        reg_id = reg_req.json()["id"]

        approve_res = await client.post(
            f"/api/v1/attendance/regularization/{reg_id}/approve",
            headers=headers
        )
        assert approve_res.status_code == 200
        assert approve_res.json()["status"] == "APPROVED"

        # 12. Create & Query Holiday Calendar
        hol_res = await client.post(
            "/api/v1/holidays",
            headers=headers,
            json={
                "holiday_name": "New Year Day",
                "holiday_date": "2024-01-01",
                "holiday_type": "NATIONAL",
                "description": "National Holiday"
            }
        )
        assert hol_res.status_code == 201

        get_hol_res = await client.get("/api/v1/holidays", headers=headers)
        assert get_hol_res.status_code == 200
        assert len(get_hol_res.json()) >= 1

@pytest.mark.asyncio
async def test_phase4_cross_tenant_isolation():
    """Verify Tenant A cannot access or modify Tenant B shift or attendance records."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register User A in Tenant A
        user_a_email = f"user_a_{uuid.uuid4().hex[:6]}@tenant-a.com"
        await client.post("/api/v1/auth/register", json={"email": user_a_email, "password": "Password123!", "first_name": "A", "last_name": "User"})
        login_a = await client.post("/api/v1/auth/login", json={"email": user_a_email, "password": "Password123!"})
        headers_a = {"Authorization": f"Bearer {login_a.json()['data']['access_token']}"}

        # Create Shift in Tenant A
        code_a = f"SHIFT-{uuid.uuid4().hex[:6]}"
        shift_a = await client.post("/api/v1/shifts", headers=headers_a, json={"code": code_a, "name": "Shift A", "start_time": "09:00:00", "end_time": "18:00:00"})
        assert shift_a.status_code == 201
        shift_a_id = shift_a.json()["id"]

        # Register User B in Tenant B
        user_b_email = f"user_b_{uuid.uuid4().hex[:6]}@tenant-b.com"
        await client.post("/api/v1/auth/register", json={"email": user_b_email, "password": "Password123!", "first_name": "B", "last_name": "User"})
        login_b = await client.post("/api/v1/auth/login", json={"email": user_b_email, "password": "Password123!"})
        headers_b = {"Authorization": f"Bearer {login_b.json()['data']['access_token']}"}

        # Assign distinct Company (Tenant B) to User B
        from app.db.session import AsyncSessionLocal
        from app.models.organization import Company
        from app.models.user import User
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            comp_b = Company(name="Tenant B Corp", code=f"TB-{uuid.uuid4().hex[:6]}")
            db.add(comp_b)
            await db.flush()
            user_b = (await db.execute(select(User).where(User.email == user_b_email))).scalar_one()
            user_b.tenant_id = comp_b.id
            await db.commit()

        # Tenant B tries to get Tenant A's shift by ID -> 404 Not Found
        get_b_shift = await client.get(f"/api/v1/shifts/{shift_a_id}", headers=headers_b)
        assert get_b_shift.status_code == 404
