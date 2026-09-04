import logging
from uuid import UUID
from app.db.session import SessionLocal
from app.services.payroll_service import PayrollService

logger = logging.getLogger(__name__)


def process_bulk_payroll_job(tenant_id: UUID, payroll_run_id: UUID):
    """
    Background worker job for heavy multi-employee payroll processing.
    Idempotent and tenant-scoped.
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting background payroll calculation for run: {payroll_run_id}")
        payroll_run = PayrollService.calculate_payroll_run(
            db=db,
            tenant_id=tenant_id,
            payroll_run_id=payroll_run_id
        )
        logger.info(f"Completed payroll calculation for run: {payroll_run_id}, employees: {payroll_run.total_employees}")
        return {"status": "SUCCESS", "payroll_run_id": str(payroll_run_id), "total_employees": payroll_run.total_employees}
    except Exception as e:
        logger.error(f"Error processing background payroll calculation: {str(e)}")
        raise e
    finally:
        db.close()


def generate_batch_payslips_job(tenant_id: UUID, payroll_run_id: UUID):
    """
    Background worker job for asynchronous PDF payslip batch generation.
    """
    db = SessionLocal()
    try:
        logger.info(f"Locking payroll run and generating batch payslips: {payroll_run_id}")
        payroll_run = PayrollService.lock_payroll_run(
            db=db,
            tenant_id=tenant_id,
            payroll_run_id=payroll_run_id
        )
        return {"status": "SUCCESS", "payroll_run_id": str(payroll_run_id), "locked_at": str(payroll_run.locked_at)}
    except Exception as e:
        logger.error(f"Error generating batch payslips: {str(e)}")
        raise e
    finally:
        db.close()
