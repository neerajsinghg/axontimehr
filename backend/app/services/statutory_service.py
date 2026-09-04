from decimal import Decimal
from typing import Dict, Any


class StatutoryService:
    """
    Statutory deduction calculation engine (PF, ESI, Professional Tax, TDS).
    Uses Decimal arithmetic for precise financial compliance.
    """

    @staticmethod
    def calculate_pf(basic_salary: Decimal, cap_enabled: bool = True) -> Dict[str, Decimal]:
        """
        PF: Employee 12% of Basic, Employer 12% of Basic.
        If cap_enabled is True and Basic > 15,000, PF is capped at 1,800 per month.
        """
        if basic_salary <= 0:
            return {"employee_pf": Decimal("0.00"), "employer_pf": Decimal("0.00")}

        pf_eligible_basic = basic_salary
        if cap_enabled and basic_salary > Decimal("15000.00"):
            pf_eligible_basic = Decimal("15000.00")

        pf_amount = (pf_eligible_basic * Decimal("0.12")).quantize(Decimal("0.01"))
        return {
            "employee_pf": pf_amount,
            "employer_pf": pf_amount
        }

    @staticmethod
    def calculate_esi(gross_salary: Decimal) -> Dict[str, Decimal]:
        """
        ESI: Applicable if Gross <= 21,000/month.
        Employee: 0.75% of Gross
        Employer: 3.25% of Gross
        """
        if gross_salary <= 0 or gross_salary > Decimal("21000.00"):
            return {"employee_esi": Decimal("0.00"), "employer_esi": Decimal("0.00")}

        employee_esi = (gross_salary * Decimal("0.0075")).quantize(Decimal("0.01"))
        employer_esi = (gross_salary * Decimal("0.0325")).quantize(Decimal("0.01"))
        return {
            "employee_esi": employee_esi,
            "employer_esi": employer_esi
        }

    @staticmethod
    def calculate_pt(gross_salary: Decimal, state: str = "MAHARASHTRA") -> Decimal:
        """
        Professional Tax (PT) slab calculation.
        Example (Maharashtra/Karnataka/Telangana):
        Gross <= 7,500: 0
        7,501 to 10,000: 175
        > 10,000: 200
        """
        if gross_salary <= Decimal("7500.00"):
            return Decimal("0.00")
        elif gross_salary <= Decimal("10000.00"):
            return Decimal("175.00")
        else:
            return Decimal("200.00")

    @staticmethod
    def calculate_tds_estimate(gross_salary: Decimal, taxable_declarations: Decimal = Decimal("0.00")) -> Decimal:
        """
        Simplified monthly TDS estimation foundation based on annual projection.
        """
        annual_gross = gross_salary * Decimal("12.00")
        taxable_annual = max(Decimal("0.00"), annual_gross - Decimal("75000.00") - taxable_declarations)  # 75k standard deduction

        if taxable_annual <= Decimal("700000.00"):
            annual_tax = Decimal("0.00")
        elif taxable_annual <= Decimal("1000000.00"):
            annual_tax = (taxable_annual - Decimal("700000.00")) * Decimal("0.10")
        else:
            annual_tax = Decimal("30000.00") + (taxable_annual - Decimal("1000000.00")) * Decimal("0.20")

        monthly_tds = (annual_tax / Decimal("12.00")).quantize(Decimal("0.01"))
        return monthly_tds
