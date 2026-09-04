import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_phase3_organization_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        rand_suffix = uuid.uuid4().hex[:6]
        admin_email = f"hr_admin_{rand_suffix}@axontimehr.com"
        # Register user to get JWT token
        reg_res = await client.post(
            "/api/v1/auth/register",
            json={
                "email": admin_email,
                "password": "Password123!",
                "first_name": "HR",
                "last_name": "Admin"
            }
        )
        assert reg_res.status_code == 201

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

        # 1. Get Organization Profile
        org_res = await client.get("/api/v1/organization", headers=headers)
        assert org_res.status_code == 200
        assert org_res.json()["code"] is not None

        # 2. Update Organization Profile
        up_org_res = await client.put(
            "/api/v1/organization",
            headers=headers,
            json={"display_name": "AxonTime Global HQ", "currency": "USD"}
        )
        assert up_org_res.status_code == 200
        assert up_org_res.json()["display_name"] == "AxonTime Global HQ"

        # 3. Create Department
        dept_res = await client.post(
            "/api/v1/departments",
            headers=headers,
            json={"name": "Engineering", "code": f"ENG-{rand_suffix}", "description": "Software R&D"}
        )
        assert dept_res.status_code == 201
        dept_id = dept_res.json()["id"]

        # 4. Create Designation
        desig_res = await client.post(
            "/api/v1/designations",
            headers=headers,
            json={"name": "Senior Software Engineer", "code": f"SSE-{rand_suffix}", "level": 3}
        )
        assert desig_res.status_code == 201
        desig_id = desig_res.json()["id"]

        # 5. Create Branch
        branch_res = await client.post(
            "/api/v1/branches",
            headers=headers,
            json={"name": "San Francisco Office", "code": f"SFO-{rand_suffix}", "city": "San Francisco", "country": "USA"}
        )
        assert branch_res.status_code == 201
        branch_id = branch_res.json()["id"]

        # 6. Create Manager Employee
        mgr_res = await client.post(
            "/api/v1/employees",
            headers=headers,
            json={
                "employee_id": f"EMP-MGR-{rand_suffix}",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": f"jane_{rand_suffix}@axontimehr.com",
                "joining_date": "2024-01-15",
                "department_id": dept_id,
                "designation_id": desig_id,
                "branch_id": branch_id
            }
        )
        assert mgr_res.status_code == 201, f"mgr_res failed with {mgr_res.status_code}: {mgr_res.text}"
        mgr_id = mgr_res.json()["id"]

        # 7. Create Subordinate Employee with Manager link
        emp_res = await client.post(
            "/api/v1/employees",
            headers=headers,
            json={
                "employee_id": f"EMP-SUB-{rand_suffix}",
                "first_name": "John",
                "last_name": f"Smith_{rand_suffix}",
                "email": f"john_{rand_suffix}@axontimehr.com",
                "joining_date": "2024-03-01",
                "department_id": dept_id,
                "designation_id": desig_id,
                "branch_id": branch_id,
                "manager_id": mgr_id
            }
        )
        assert emp_res.status_code == 201
        emp_id = emp_res.json()["id"]

        # 8. Verify Employee Detail & Manager Link
        detail_res = await client.get(f"/api/v1/employees/{emp_id}", headers=headers)
        assert detail_res.status_code == 200, f"detail_res failed with {detail_res.status_code}: {detail_res.text}"
        assert detail_res.json()["manager"]["first_name"] == "Jane"

        # 9. Verify Hierarchy Cycle Prevention (Jane cannot report to John who reports to Jane)
        cycle_res = await client.put(
            f"/api/v1/employees/{mgr_id}",
            headers=headers,
            json={"manager_id": emp_id}
        )
        assert cycle_res.status_code == 400
        assert "hierarchy cycle" in cycle_res.json()["detail"].lower()

        # 10. Document Metadata Upload & Delete
        doc_res = await client.post(
            f"/api/v1/employees/{emp_id}/documents",
            headers=headers,
            json={
                "document_type": "CONTRACT",
                "file_name": "employment_contract.pdf",
                "storage_key": "s3://axontime/docs/contract_002.pdf",
                "mime_type": "application/pdf",
                "file_size": 2048500
            }
        )
        assert doc_res.status_code == 201, f"doc_res failed with {doc_res.status_code}: {doc_res.text}"
        doc_id = doc_res.json()["id"]

        docs_list_res = await client.get(f"/api/v1/employees/{emp_id}/documents", headers=headers)
        assert docs_list_res.status_code == 200, f"docs_list_res failed with {docs_list_res.status_code}: {docs_list_res.text}"
        assert len(docs_list_res.json()) == 1

        del_doc_res = await client.delete(f"/api/v1/employees/{emp_id}/documents/{doc_id}", headers=headers)
        assert del_doc_res.status_code == 200, f"del_doc_res failed with {del_doc_res.status_code}: {del_doc_res.text}"

        # 11. Employee Search & Pagination
        list_res = await client.get(f"/api/v1/employees?q={rand_suffix}&page=1&limit=10", headers=headers)
        assert list_res.status_code == 200, f"list_res failed with {list_res.status_code}: {list_res.text}"
        assert list_res.json()["total"] >= 1
        assert any(emp["first_name"] == "John" for emp in list_res.json()["data"])
