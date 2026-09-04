import pytest
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.formula_engine import SafeFormulaEvaluator, FormulaEvaluationError
from app.services.statutory_service import StatutoryService


@pytest.mark.asyncio
async def test_formula_evaluator_security_and_correctness():
    # 1. Valid Formula Evaluation
    vars_dict = {
        "BASIC": Decimal("40000.00"),
        "GROSS": Decimal("70000.00"),
        "WORKING_DAYS": Decimal("22.00")
    }

    # HRA = 40% of Basic
    hra = SafeFormulaEvaluator.evaluate("BASIC * 0.40", vars_dict)
    assert hra == Decimal("16000.00")

    # Min formula test
    pf = SafeFormulaEvaluator.evaluate("min(BASIC * 0.12, 1800)", vars_dict)
    assert pf == Decimal("1800.00")

    # 2. Blocked Dangerous Syntax
    with pytest.raises(FormulaEvaluationError):
        SafeFormulaEvaluator.evaluate("__import__('os').system('dir')", vars_dict)

    with pytest.raises(FormulaEvaluationError):
        SafeFormulaEvaluator.evaluate("eval('1 + 1')", vars_dict)


@pytest.mark.asyncio
async def test_statutory_service_rules():
    # PF Test
    pf_res = StatutoryService.calculate_pf(Decimal("40000.00"), cap_enabled=True)
    assert pf_res["employee_pf"] == Decimal("1800.00")

    # ESI Test (Gross > 21,000 should be 0)
    esi_res_high = StatutoryService.calculate_esi(Decimal("25000.00"))
    assert esi_res_high["employee_esi"] == Decimal("0.00")

    # ESI Test (Gross <= 21,000 should calculate 0.75%)
    esi_res_low = StatutoryService.calculate_esi(Decimal("20000.00"))
    assert esi_res_low["employee_esi"] == Decimal("150.00")

    # PT Test
    pt_amount = StatutoryService.calculate_pt(Decimal("15000.00"))
    assert pt_amount == Decimal("200.00")


@pytest.mark.asyncio
async def test_phase7_payroll_full_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Register Admin User
        email = f"payroll_admin_{pytest.importorskip('uuid').uuid4().hex[:6]}@example.com"
        reg_res = await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "Password123!",
            "first_name": "Payroll",
            "last_name": "Admin",
            "company_name": f"Payroll Corp {pytest.importorskip('uuid').uuid4().hex[:6]}"
        })
        assert reg_res.status_code == 201
        
        login_res = await client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "Password123!"
        })
        assert login_res.status_code == 200
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Seed Default Components
        seed_res = await client.post("/api/v1/salary/components/seed", headers=headers)
        assert seed_res.status_code in [200, 201]
        components = seed_res.json()
        assert len(components) >= 5

        # 3. Create Salary Structure
        struct_res = await client.post("/api/v1/salary/structures", headers=headers, json={
            "code": "EXEC_STRUCT",
            "name": "Executive Structure",
            "description": "Standard Executive Compensation",
            "components": []
        })
        assert struct_res.status_code == 201
        struct_id = struct_res.json()["id"]

        # 4. Get Current Admin Employee ID
        emp_res = await client.get("/api/v1/employees/me", headers=headers)
        assert emp_res.status_code == 200
        emp_id = emp_res.json()["id"]

        # 5. Assign Salary to Employee
        assign_res = await client.post("/api/v1/salary/assignments", headers=headers, json={
            "employee_id": emp_id,
            "salary_structure_id": struct_id,
            "annual_ctc": 840000.0,
            "effective_from": "2026-09-01"
        })
        assert assign_res.status_code == 201
        assert assign_res.json()["gross_salary"] == 70000.0

        # 6. Create Payroll Period
        period_res = await client.post("/api/v1/payroll/periods", headers=headers, json={
            "name": "September 2026",
            "year": 2026,
            "month": 9,
            "start_date": "2026-09-01",
            "end_date": "2026-09-30",
            "pay_date": "2026-09-30"
        })
        assert period_res.status_code == 201
        period_id = period_res.json()["id"]

        # 7. Create Payroll Run
        run_res = await client.post("/api/v1/payroll/runs", headers=headers, json={
            "period_id": period_id
        })
        assert run_res.status_code == 201
        run_id = run_res.json()["id"]

        # 8. Calculate Payroll Run
        calc_res = await client.post(f"/api/v1/payroll/runs/{run_id}/calculate", headers=headers)
        assert calc_res.status_code == 200
        run_data = calc_res.json()
        assert run_data["status"] == "PROCESSED"
        assert run_data["total_employees"] >= 1
        assert run_data["total_gross"] > 0

        # 9. Lock Payroll Run & Generate Payslips
        lock_res = await client.post(f"/api/v1/payroll/runs/{run_id}/lock", headers=headers)
        assert lock_res.status_code == 200
        assert lock_res.json()["status"] == "LOCKED"

        # 10. Fetch Payslips for Employee (ESS)
        payslip_res = await client.get("/api/v1/payslips", headers=headers)
        assert payslip_res.status_code == 200
        payslips = payslip_res.json()
        assert len(payslips) >= 1
        token = payslips[0]["download_token"]

        # 11. Download Payslip HTML
        dl_res = await client.get(f"/api/v1/payslips/{token}/download")
        assert dl_res.status_code == 200
        assert "AxonTimeHR" in dl_res.text
        assert "NET SALARY PAYABLE" in dl_res.text


@pytest.mark.asyncio
async def test_phase7_payroll_tenant_isolation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Tenant A
        email_a = f"tenant_a_{pytest.importorskip('uuid').uuid4().hex[:6]}@example.com"
        reg_a = await client.post("/api/v1/auth/register", json={
            "email": email_a,
            "password": "Password123!",
            "first_name": "Tenant",
            "last_name": "A",
            "company_name": f"Company A {pytest.importorskip('uuid').uuid4().hex[:6]}"
        })
        login_a = await client.post("/api/v1/auth/login", json={"email": email_a, "password": "Password123!"})
        token_a = login_a.json()["data"]["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Tenant B
        email_b = f"tenant_b_{pytest.importorskip('uuid').uuid4().hex[:6]}@example.com"
        reg_b = await client.post("/api/v1/auth/register", json={
            "email": email_b,
            "password": "Password123!",
            "first_name": "Tenant",
            "last_name": "B",
            "company_name": f"Company B {pytest.importorskip('uuid').uuid4().hex[:6]}"
        })
        login_b = await client.post("/api/v1/auth/login", json={"email": email_b, "password": "Password123!"})
        token_b = login_b.json()["data"]["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # Tenant A creates Payroll Period
        p_res = await client.post("/api/v1/payroll/periods", headers=headers_a, json={
            "name": "Period A",
            "year": 2026,
            "month": 9,
            "start_date": "2026-09-01",
            "end_date": "2026-09-30",
            "pay_date": "2026-09-30"
        })
        assert p_res.status_code == 201

        # Tenant B lists periods -> Should be empty / isolated
        b_periods = await client.get("/api/v1/payroll/periods", headers=headers_b)
        assert b_periods.status_code == 200
        assert len(b_periods.json()) == 0
