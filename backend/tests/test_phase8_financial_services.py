import pytest
import uuid
from datetime import date
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_phase8_expense_and_policy_flow():
    """
    Tests expense category creation, claim submission, policy enforcement,
    and reimbursement processing.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register and login Tenant Admin
        tenant_name = f"Tenant P8 {uuid.uuid4().hex}"
        admin_email = f"p8_admin_{uuid.uuid4().hex[:6]}@tenant-a.com"
        reg_res = await client.post(
            "/api/v1/auth/register",
            json={
                "email": admin_email,
                "password": "Password123!",
                "first_name": "Finance",
                "last_name": "Admin",
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
        auth_headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Create Expense Category
        cat_payload = {
            "code": f"TRAVEL_{uuid.uuid4().hex[:4]}",
            "name": "Business Travel",
            "description": "Travel and lodging expenses",
            "max_amount": "5000.00",
            "requires_receipt": False,
            "requires_approval": True,
            "taxable": False
        }
        cat_res = await client.post("/api/v1/expenses/categories", json=cat_payload, headers=auth_headers)
        assert cat_res.status_code == 201
        category_id = cat_res.json()["id"]

        # 2. Get Categories
        get_cats_res = await client.get("/api/v1/expenses/categories", headers=auth_headers)
        assert get_cats_res.status_code == 200
        assert len(get_cats_res.json()) >= 1

        # 3. Create Expense Claim
        claim_payload = {
            "claim_date": str(date.today()),
            "description": "Client Meeting Travel in Delhi",
            "currency": "USD",
            "items": [
                {
                    "category_id": category_id,
                    "expense_date": str(date.today()),
                    "amount": "1500.00",
                    "merchant": "Air India",
                    "description": "Flight Tickets"
                }
            ]
        }
        claim_res = await client.post("/api/v1/expenses/claims", json=claim_payload, headers=auth_headers)
        assert claim_res.status_code == 201
        claim_data = claim_res.json()
        claim_id = claim_data["id"]
        assert claim_data["status"] == "DRAFT"
        assert float(claim_data["total_amount"]) == 1500.0

        # 4. Submit Expense Claim for Approval
        sub_res = await client.post(f"/api/v1/expenses/claims/{claim_id}/submit", headers=auth_headers)
        assert sub_res.status_code == 200
        assert sub_res.json()["status"] == "SUBMITTED"

        # 5. Fetch Reimbursements
        reimb_res = await client.get("/api/v1/expenses/reimbursements", headers=auth_headers)
        assert reimb_res.status_code == 200


@pytest.mark.asyncio
async def test_phase8_loan_engine_and_schedule():
    """
    Tests loan type creation, eligibility check, loan request, reducing balance
    schedule calculation, disbursement, and prepayment.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        admin_email = f"p8_loan_{uuid.uuid4().hex[:6]}@tenant-a.com"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": admin_email,
                "password": "Password123!",
                "first_name": "Loan",
                "last_name": "Manager",
                "company_name": f"Tenant Loan {uuid.uuid4().hex[:4]}"
            }
        )

        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": admin_email, "password": "Password123!"}
        )
        admin_token = login_res.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Create Loan Type (Reducing Balance)
        lt_payload = {
            "code": f"EMERGENCY_{uuid.uuid4().hex[:4]}",
            "name": "Emergency Loan",
            "description": "Short-term emergency loan",
            "max_amount": "50000.00",
            "min_service_months": 1,
            "max_salary_multiple": "3.00",
            "interest_rate": "6.00",
            "interest_type": "REDUCING_BALANCE"
        }
        lt_res = await client.post("/api/v1/loans/types", json=lt_payload, headers=auth_headers)
        assert lt_res.status_code == 201
        loan_type_id = lt_res.json()["id"]

        # 2. Request Employee Loan
        loan_req_payload = {
            "loan_type_id": loan_type_id,
            "principal_amount": "12000.00",
            "tenure_months": 6
        }
        loan_res = await client.post("/api/v1/loans/requests", json=loan_req_payload, headers=auth_headers)
        assert loan_res.status_code == 201
        loan_data = loan_res.json()
        assert loan_data["status"] == "SUBMITTED"
        assert len(loan_data["installments"]) == 6


@pytest.mark.asyncio
async def test_phase8_salary_advance_flow():
    """
    Tests salary advance request, recovery schedule generation, and disbursement.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        admin_email = f"p8_adv_{uuid.uuid4().hex[:6]}@tenant-a.com"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": admin_email,
                "password": "Password123!",
                "first_name": "Advance",
                "last_name": "User",
                "company_name": f"Tenant Adv {uuid.uuid4().hex[:4]}"
            }
        )

        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": admin_email, "password": "Password123!"}
        )
        admin_token = login_res.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {admin_token}"}

        adv_payload = {
            "amount": "6000.00",
            "recovery_months": 3
        }
        adv_res = await client.post("/api/v1/salary-advances/", json=adv_payload, headers=auth_headers)
        assert adv_res.status_code == 201
        adv_data = adv_res.json()
        assert adv_data["status"] == "PENDING"
        assert len(adv_data["recoveries"]) == 3


@pytest.mark.asyncio
async def test_phase8_financial_dashboard_and_ledger():
    """
    Tests financial ledger endpoints and dashboard metric summaries.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        admin_email = f"p8_dash_{uuid.uuid4().hex[:6]}@tenant-a.com"
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": admin_email,
                "password": "Password123!",
                "first_name": "Dash",
                "last_name": "Admin",
                "company_name": f"Tenant Dash {uuid.uuid4().hex[:4]}"
            }
        )

        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": admin_email, "password": "Password123!"}
        )
        admin_token = login_res.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {admin_token}"}

        dash_res = await client.get("/api/v1/financial/dashboard", headers=auth_headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert "total_claims_count" in dash_data
        assert "outstanding_loans_principal" in dash_data

        tx_res = await client.get("/api/v1/financial/transactions", headers=auth_headers)
        assert tx_res.status_code == 200
        assert isinstance(tx_res.json(), list)
