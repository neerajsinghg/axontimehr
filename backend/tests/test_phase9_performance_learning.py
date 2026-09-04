import pytest
import uuid
from decimal import Decimal
from datetime import date
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_phase9_performance_learning_workflow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login Tenant Admin
        tenant_name = f"Tenant P9 {uuid.uuid4().hex[:6]}"
        admin_email = f"p9_admin_{uuid.uuid4().hex[:6]}@tenant-p9.com"
        reg_res = await client.post(
            "/api/v1/auth/register",
            json={
                "company_name": tenant_name,
                "company_code": f"P9-{uuid.uuid4().hex[:4]}",
                "first_name": "Performance",
                "last_name": "Admin",
                "email": admin_email,
                "password": "Password123!",
            },
        )
        assert reg_res.status_code == 201

        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": admin_email, "password": "Password123!"},
        )
        assert login_res.status_code == 200
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create Performance Cycle
        cycle_payload = {
            "name": "2026 Annual Performance Appraisal Cycle",
            "description": "Company-wide annual goal alignment and performance review",
            "cycle_type": "ANNUAL",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31"
        }
        resp_cycle = await client.post("/api/v1/performance/cycles", json=cycle_payload, headers=headers)
        assert resp_cycle.status_code == 201
        cycle_data = resp_cycle.json()
        cycle_id = cycle_data["id"]
        assert cycle_data["name"] == "2026 Annual Performance Appraisal Cycle"

        # 2. Get Performance Cycles
        resp_list_cycles = await client.get("/api/v1/performance/cycles", headers=headers)
        assert resp_list_cycles.status_code == 200
        assert len(resp_list_cycles.json()) >= 1

        # 3. Create Goal
        goal_payload = {
            "cycle_id": cycle_id,
            "employee_id": "emp-test-001",
            "title": "Achieve 99.9% Backend Service Uptime SLA",
            "description": "Optimize FastAPI microservices and database query indexing",
            "goal_type": "INDIVIDUAL",
            "baseline_value": 0.0,
            "target_value": 100.0,
            "current_value": 0.0,
            "unit": "PERCENT",
            "weightage": 30.0
        }
        resp_goal = await client.post("/api/v1/performance/goals", json=goal_payload, headers=headers)
        assert resp_goal.status_code == 201
        goal_data = resp_goal.json()
        goal_id = goal_data["id"]
        assert goal_data["title"] == "Achieve 99.9% Backend Service Uptime SLA"

        # 4. Update Goal Progress
        resp_progress = await client.post(
            f"/api/v1/performance/goals/{goal_id}/progress",
            json={"current_value": 75.0, "comments": "Completed Phase 1-8 optimizations"},
            headers=headers
        )
        assert resp_progress.status_code == 200
        assert float(resp_progress.json()["progress_pct"]) == 75.0

        # 5. Fetch Review and Submit Self Assessment
        resp_review = await client.get(f"/api/v1/performance/reviews/my-review?cycle_id={cycle_id}", headers=headers)
        assert resp_review.status_code == 200
        review_id = resp_review.json()["id"]

        resp_self = await client.post(
            f"/api/v1/performance/reviews/{review_id}/self-assessment",
            json={"self_score": 4.5, "employee_comments": "Exceeded all system reliability metrics"},
            headers=headers
        )
        assert resp_self.status_code == 200
        assert float(resp_self.json()["self_score"]) == 4.5

        # 6. Submit Manager Assessment
        resp_mgr = await client.post(
            f"/api/v1/performance/reviews/{review_id}/manager-assessment",
            json={"manager_score": 4.8},
            headers=headers
        )
        assert resp_mgr.status_code == 200
        # Final weighted score = (4.5 * 0.4) + (4.8 * 0.6) = 1.8 + 2.88 = 4.68
        assert float(resp_mgr.json()["final_score"]) == 4.68

        # 7. Rating Calibration Override
        resp_calib = await client.post(
            "/api/v1/performance/calibration",
            json={
                "review_id": review_id,
                "calibrated_score": 4.5,
                "reason": "Department rating normalization across team"
            },
            headers=headers
        )
        assert resp_calib.status_code == 200
        assert float(resp_calib.json()["calibrated_score"]) == 4.5

        # 8. L&D Training Courses & Skills Matrix
        resp_courses = await client.get("/api/v1/training/courses", headers=headers)
        assert resp_courses.status_code == 200
        assert len(resp_courses.json()) >= 1

        resp_skills = await client.get("/api/v1/training/skills/matrix", headers=headers)
        assert resp_skills.status_code == 200
        assert len(resp_skills.json()) >= 1

        # 9. Employee Pulse Surveys
        resp_surveys = await client.get("/api/v1/engagement/surveys", headers=headers)
        assert resp_surveys.status_code == 200
        assert len(resp_surveys.json()) >= 1
