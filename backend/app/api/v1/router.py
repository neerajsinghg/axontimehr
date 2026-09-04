from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.employees import router as employees_router
from app.api.v1.auth import router as auth_router
from app.api.v1.organizations import router as organizations_router
from app.api.v1.attendance import router as attendance_router
from app.api.v1.locations import router as locations_router
from app.api.v1.leaves import router as leaves_router
from app.api.v1.holidays import router as holidays_router
from app.api.v1.workflows import router as workflows_router
from app.api.v1.approvals import router as approvals_router
from app.api.v1.regularizations import router as regularizations_router
from app.api.v1.salary import router as salary_router
from app.api.v1.payroll import router as payroll_router
from app.api.v1.payslips import router as payslips_router
from app.api.v1.expenses import router as expenses_router
from app.api.v1.loans import router as loans_router
from app.api.v1.advances import router as advances_router
from app.api.v1.financial_reports import router as financial_reports_router
from app.api.v1.performance import router as performance_router
from app.api.v1.learning import router as learning_router
from app.api.v1.engagement import router as engagement_router
from app.api.v1.recruitment import router as recruitment_router
from app.api.v1.workforce import router as workforce_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.ai_assistant import router as ai_assistant_router
from app.api.v1.employee_experience import router as employee_experience_router
from app.api.v1.compliance import router as compliance_router
from app.api.v1.intelligence_bi import router as intelligence_bi_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router, tags=["Health"])
api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(organizations_router, tags=["Organization & Master Data"])
api_v1_router.include_router(employees_router, tags=["Employees"])
api_v1_router.include_router(attendance_router, tags=["Attendance & Shifts"])
api_v1_router.include_router(locations_router, prefix="/attendance", tags=["GPS & Verified Attendance"])
api_v1_router.include_router(leaves_router, tags=["Leaves & Balance Engine"])
api_v1_router.include_router(holidays_router, tags=["Holiday Calendars"])
api_v1_router.include_router(workflows_router, tags=["Approval Workflows"])
api_v1_router.include_router(approvals_router, tags=["Manager & HR Approval Inbox"])
api_v1_router.include_router(regularizations_router, tags=["Attendance Regularization"])
api_v1_router.include_router(salary_router, tags=["Salary & Compensation"])
api_v1_router.include_router(payroll_router, tags=["Payroll Management"])
api_v1_router.include_router(payslips_router, tags=["Employee Payslips"])
api_v1_router.include_router(expenses_router, tags=["Phase 8: Expenses & Reimbursements"])
api_v1_router.include_router(loans_router, tags=["Phase 8: Employee Loans"])
api_v1_router.include_router(advances_router, tags=["Phase 8: Salary Advances"])
api_v1_router.include_router(financial_reports_router, tags=["Phase 8: Financial Ledger & Reports"])
api_v1_router.include_router(performance_router, prefix="/performance", tags=["Phase 9: Performance Management"])
api_v1_router.include_router(learning_router, prefix="/training", tags=["Phase 9: Learning & Development"])
api_v1_router.include_router(engagement_router, prefix="/engagement", tags=["Phase 9: Employee Engagement"])
api_v1_router.include_router(recruitment_router, tags=["Phase 10: Recruitment & ATS"])
api_v1_router.include_router(workforce_router, tags=["Phase 10: Workforce Planning"])
api_v1_router.include_router(analytics_router, tags=["Phase 10: Advanced HR Analytics"])
api_v1_router.include_router(ai_assistant_router, tags=["Phase 10: AI HR Intelligence"])
api_v1_router.include_router(employee_experience_router, tags=["Phase 11: Employee Experience Platform"])
api_v1_router.include_router(compliance_router, tags=["Phase 12: Compliance & Governance Platform"])
api_v1_router.include_router(intelligence_bi_router, tags=["Phase 13: Intelligence & BI Platform"])
