import uuid
import pytest
from httpx import AsyncClient

async def get_authed_headers(client: AsyncClient) -> dict:
    rand_suffix = uuid.uuid4().hex[:6]
    admin_email = f"phase10_admin_{rand_suffix}@axontimehr.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": admin_email,
            "password": "Password123!",
            "first_name": "Phase10",
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
async def test_phase10_recruitment_and_ats_workflow(sync_client: AsyncClient):
    headers = await get_authed_headers(sync_client)

    # 2. Create Job Requisition
    req_payload = {
        "positions_count": 2,
        "location": "Bengaluru Tech Park",
        "min_experience": 3,
        "max_experience": 8,
        "required_skills": "Python, FastAPI, React",
        "salary_min": 1400000,
        "salary_max": 2000000,
        "budget": 4000000,
        "priority": "HIGH",
        "reason_for_hiring": "Q4 Enterprise Scale Up"
    }
    req_res = await sync_client.post("/api/v1/recruitment/requisitions", json=req_payload, headers=headers)
    assert req_res.status_code == 201
    requisition = req_res.json()
    assert requisition["status"] == "APPROVED"

    # 3. Create Job Posting
    job_payload = {
        "requisition_id": requisition["id"],
        "title": "Principal AI & Backend Architect",
        "description": "Architect core SaaS scalability & AI engines.",
        "requirements": "7+ years Python & Distributed Systems",
        "location": "Bengaluru HQ",
        "location_type": "HYBRID",
        "openings_count": 2
    }
    job_res = await sync_client.post("/api/v1/recruitment/jobs", json=job_payload, headers=headers)
    assert job_res.status_code == 201
    job = job_res.json()
    assert job["is_published"] is True

    # 4. Create Candidate
    cand_payload = {
        "job_posting_id": job["id"],
        "first_name": "Vikram",
        "last_name": "Aditya",
        "email": "vikram.aditya@example.com",
        "phone": "+91 9988776655",
        "current_company": "Apex Cloud Systems",
        "expected_salary": 1800000,
        "skills_list": "Python, FastAPI, Docker, Microservices"
    }
    cand_res = await sync_client.post("/api/v1/recruitment/candidates", json=cand_payload, headers=headers)
    assert cand_res.status_code == 201
    candidate = cand_res.json()
    assert candidate["status"] == "APPLIED"

    # 5. Update Candidate Stage to INTERVIEW
    stage_res = await sync_client.patch(f"/api/v1/recruitment/candidates/{candidate['id']}/stage", json={"new_status": "INTERVIEW", "reason": "Shortlisted by Hiring Manager"}, headers=headers)
    assert stage_res.status_code == 200
    assert stage_res.json()["status"] == "INTERVIEW"

    # 6. Schedule Panel Interview
    int_payload = {
        "candidate_id": candidate["id"],
        "job_posting_id": job["id"],
        "interview_type": "TECHNICAL",
        "scheduled_at": "2026-09-10T10:00:00Z",
        "duration_minutes": 60,
        "meeting_url": "https://meet.google.com/axon-tech-interview"
    }
    int_res = await sync_client.post("/api/v1/recruitment/interviews", json=int_payload, headers=headers)
    assert int_res.status_code == 201
    interview = int_res.json()

    # 7. Submit Interview Feedback
    fb_payload = {
        "interview_id": interview["id"],
        "technical_score": 4.8,
        "communication_score": 4.5,
        "culture_fit_score": 4.5,
        "problem_solving_score": 5.0,
        "overall_rating": 4.7,
        "recommendation": "STRONG_HIRE",
        "comments": "Outstanding technical depth and clean code principles."
    }
    fb_res = await sync_client.post("/api/v1/recruitment/interviews/feedback", json=fb_payload, headers=headers)
    assert fb_res.status_code == 201

    # 8. Create Offer
    off_payload = {
        "candidate_id": candidate["id"],
        "job_posting_id": job["id"],
        "offer_number": f"OFF-{uuid.uuid4().hex[:6]}",
        "base_salary": 1800000,
        "variable_pay": 200000,
        "joining_date": "2026-10-01"
    }
    off_res = await sync_client.post("/api/v1/recruitment/offers", json=off_payload, headers=headers)
    assert off_res.status_code == 201
    offer = off_res.json()

    # 9. 1-Click Candidate to Employee Onboarding Conversion
    conv_res = await sync_client.post(f"/api/v1/recruitment/offers/{offer['id']}/convert-employee", headers=headers)
    assert conv_res.status_code == 200
    conv_data = conv_res.json()
    assert conv_data["status"] == "success"
    assert "employee_code" in conv_data

@pytest.mark.asyncio
async def test_phase10_workforce_planning_and_analytics(sync_client: AsyncClient):
    headers = await get_authed_headers(sync_client)

    # Headcount Plan
    plan_res = await sync_client.get("/api/v1/workforce/headcount-plans", headers=headers)
    assert plan_res.status_code == 200
    plans = plan_res.json()
    assert len(plans) > 0

    # Gap Analysis
    gap_res = await sync_client.get("/api/v1/workforce/gap-analysis", headers=headers)
    assert gap_res.status_code == 200
    gaps = gap_res.json()
    assert len(gaps) > 0

    # Executive Analytics Summary
    exec_res = await sync_client.get("/api/v1/analytics/executive-summary", headers=headers)
    assert exec_res.status_code == 200
    exec_summary = exec_res.json()
    assert "active_employees" in exec_summary
    assert exec_summary["attrition_rate_pct"] > 0

    # Attrition Analytics
    attr_res = await sync_client.get("/api/v1/analytics/attrition", headers=headers)
    assert attr_res.status_code == 200
    attrition = attr_res.json()
    assert len(attrition["department_breakdown"]) > 0

@pytest.mark.asyncio
async def test_phase10_ai_hr_intelligence_assistant(sync_client: AsyncClient):
    headers = await get_authed_headers(sync_client)

    # Natural Language AI Query
    ai_req = {"query_text": "What is our current attrition rate and active headcount?"}
    ai_res = await sync_client.post("/api/v1/ai/query", json=ai_req, headers=headers)
    assert ai_res.status_code == 200
    ai_data = ai_res.json()
    assert "answer_text" in ai_data
    assert len(ai_data["tools_invoked"]) > 0
    assert "attrition" in ai_data["answer_text"].lower() or "headcount" in ai_data["answer_text"].lower()
