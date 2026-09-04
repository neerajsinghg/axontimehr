import uuid
import os
from typing import List, Optional, Tuple
from datetime import datetime, timezone, date
from decimal import Decimal
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, UploadFile

from app.core.config import settings
from app.models.financial import (
    ExpenseCategory,
    ExpensePolicy,
    ExpenseClaim,
    ExpenseItem,
    ExpenseReceipt,
    Reimbursement,
    ExpenseCategoryStatus,
    ExpenseClaimStatus,
    ExpenseItemStatus,
    ReimbursementMethod,
    ReimbursementTaxability,
    ReimbursementStatus,
    FinancialTransactionType,
    TransactionDirection
)
from app.models.employee import Employee
from app.schemas.financial import (
    ExpenseCategoryCreate,
    ExpensePolicyCreate,
    ExpenseClaimCreate,
    ReimbursementProcessRequest
)
from app.services.workflow_service import WorkflowService
from app.services.financial_transaction_service import FinancialTransactionService
from app.services.audit_service import AuditService


ALLOWED_MAGIC_BYTES = {
    b"%PDF": "application/pdf",
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
    b"RIFF": "image/webp"
}


class ExpenseService:

    @staticmethod
    async def create_category(db: AsyncSession, tenant_id: uuid.UUID, data: ExpenseCategoryCreate) -> ExpenseCategory:
        existing = await db.execute(
            select(ExpenseCategory).where(
                and_(ExpenseCategory.tenant_id == tenant_id, ExpenseCategory.code == data.code)
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Expense category code '{data.code}' already exists."
            )

        cat = ExpenseCategory(
            tenant_id=tenant_id,
            code=data.code,
            name=data.name,
            description=data.description,
            max_amount=data.max_amount,
            requires_receipt=data.requires_receipt,
            requires_approval=data.requires_approval,
            taxable=data.taxable,
            status=data.status,
            effective_from=data.effective_from,
            effective_to=data.effective_to
        )
        db.add(cat)
        await db.commit()
        await db.refresh(cat)
        return cat

    @staticmethod
    async def get_categories(db: AsyncSession, tenant_id: uuid.UUID) -> List[ExpenseCategory]:
        res = await db.execute(
            select(ExpenseCategory).where(ExpenseCategory.tenant_id == tenant_id).order_by(ExpenseCategory.name)
        )
        categories = list(res.scalars().all())
        if not categories:
            default_cats = [
                ExpenseCategory(
                    tenant_id=tenant_id,
                    code="TRAVEL",
                    name="Travel & Conveyance",
                    description="Outstation business travel, flight, taxi, and hotel accommodation",
                    max_amount=Decimal("50000.00"),
                    requires_receipt=True,
                    requires_approval=True,
                    taxable=False,
                    status=ExpenseCategoryStatus.ACTIVE
                ),
                ExpenseCategory(
                    tenant_id=tenant_id,
                    code="MEALS",
                    name="Meals & Client Entertainment",
                    description="Official team lunches, client dinners, and refreshments",
                    max_amount=Decimal("10000.00"),
                    requires_receipt=True,
                    requires_approval=True,
                    taxable=False,
                    status=ExpenseCategoryStatus.ACTIVE
                ),
                ExpenseCategory(
                    tenant_id=tenant_id,
                    code="SUPPLIES",
                    name="Office Supplies & Stationery",
                    description="Office stationery, printer ink, and team supplies",
                    max_amount=Decimal("15000.00"),
                    requires_receipt=True,
                    requires_approval=True,
                    taxable=False,
                    status=ExpenseCategoryStatus.ACTIVE
                ),
                ExpenseCategory(
                    tenant_id=tenant_id,
                    code="MEDICAL",
                    name="Medical & Health Reimbursement",
                    description="Outpatient medical consultations, diagnostic tests, and prescribed medicines",
                    max_amount=Decimal("25000.00"),
                    requires_receipt=True,
                    requires_approval=True,
                    taxable=False,
                    status=ExpenseCategoryStatus.ACTIVE
                ),
                ExpenseCategory(
                    tenant_id=tenant_id,
                    code="TELECOM",
                    name="Mobile & Internet Allowance",
                    description="Monthly official mobile voice and high-speed broadband bills",
                    max_amount=Decimal("5000.00"),
                    requires_receipt=False,
                    requires_approval=True,
                    taxable=False,
                    status=ExpenseCategoryStatus.ACTIVE
                ),
                ExpenseCategory(
                    tenant_id=tenant_id,
                    code="TRAINING",
                    name="Training & Skill Certification",
                    description="Professional courses, technical certifications, and conference passes",
                    max_amount=Decimal("100000.00"),
                    requires_receipt=True,
                    requires_approval=True,
                    taxable=False,
                    status=ExpenseCategoryStatus.ACTIVE
                )
            ]
            for c in default_cats:
                db.add(c)
            await db.commit()
            
            res_new = await db.execute(
                select(ExpenseCategory).where(ExpenseCategory.tenant_id == tenant_id).order_by(ExpenseCategory.name)
            )
            categories = list(res_new.scalars().all())

        return categories

    @staticmethod
    async def create_policy(db: AsyncSession, tenant_id: uuid.UUID, data: ExpensePolicyCreate) -> ExpensePolicy:
        policy = ExpensePolicy(
            tenant_id=tenant_id,
            category_id=data.category_id,
            department_id=data.department_id,
            grade=data.grade,
            daily_limit=data.daily_limit,
            monthly_limit=data.monthly_limit,
            currency=data.currency
        )
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
        return policy

    @staticmethod
    async def upload_receipt(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, file: UploadFile) -> ExpenseReceipt:
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Receipt file exceeds 10MB limit.")

        # Magic byte signature check
        is_valid_type = any(content.startswith(header) for header in ALLOWED_MAGIC_BYTES)
        if not is_valid_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid receipt file format. Allowed: PDF, JPG, PNG, WEBP.")

        uploads_dir = os.path.join(settings.PROJECT_ROOT if hasattr(settings, "PROJECT_ROOT") else ".", "uploads", "receipts")
        os.makedirs(uploads_dir, exist_ok=True)

        file_ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
        file_id = uuid.uuid4()
        file_name = f"{file_id}.{file_ext}"
        saved_path = os.path.join(uploads_dir, file_name)

        with open(saved_path, "wb") as f:
            f.write(content)

        receipt = ExpenseReceipt(
            id=file_id,
            tenant_id=tenant_id,
            file_path=saved_path,
            file_name=file.filename,
            content_type=file.content_type or "application/octet-stream",
            file_size=len(content),
            file_signature=content[:16].hex(),
            uploaded_by=user_id
        )
        db.add(receipt)
        await db.commit()
        await db.refresh(receipt)
        return receipt

    @staticmethod
    async def create_claim(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        employee_id: uuid.UUID,
        data: ExpenseClaimCreate
    ) -> ExpenseClaim:
        if not data.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expense claim must contain at least one line item.")

        total_amount = Decimal("0.00")
        items_to_create = []

        for item_in in data.items:
            cat_res = await db.execute(
                select(ExpenseCategory).where(
                    and_(ExpenseCategory.id == item_in.category_id, ExpenseCategory.tenant_id == tenant_id)
                )
            )
            cat = cat_res.scalar_one_or_none()
            if not cat or cat.status != ExpenseCategoryStatus.ACTIVE:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or inactive expense category.")

            if cat.max_amount and item_in.amount > cat.max_amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Amount {item_in.amount} exceeds maximum category limit of {cat.max_amount} for '{cat.name}'."
                )

            if cat.requires_receipt and not item_in.receipt_file_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Receipt is mandatory for category '{cat.name}'."
                )

            # Duplicate expense detection check (same employee, same date, same amount, same merchant)
            dup_res = await db.execute(
                select(ExpenseItem).join(ExpenseClaim).where(
                    and_(
                        ExpenseClaim.tenant_id == tenant_id,
                        ExpenseClaim.employee_id == employee_id,
                        ExpenseClaim.status.in_([ExpenseClaimStatus.SUBMITTED, ExpenseClaimStatus.APPROVED]),
                        ExpenseItem.expense_date == item_in.expense_date,
                        ExpenseItem.amount == item_in.amount,
                        ExpenseItem.merchant == item_in.merchant
                    )
                )
            )
            if dup_res.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Potential duplicate expense item detected on {item_in.expense_date} for amount {item_in.amount}."
                )

            total_amount += item_in.amount
            items_to_create.append(
                ExpenseItem(
                    tenant_id=tenant_id,
                    category_id=item_in.category_id,
                    expense_date=item_in.expense_date,
                    amount=item_in.amount,
                    merchant=item_in.merchant,
                    description=item_in.description,
                    location=item_in.location,
                    receipt_file_id=item_in.receipt_file_id,
                    project_code=item_in.project_code,
                    cost_center=item_in.cost_center,
                    status=ExpenseItemStatus.PENDING
                )
            )

        claim_number = f"EXP-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"
        claim = ExpenseClaim(
            tenant_id=tenant_id,
            claim_number=claim_number,
            employee_id=employee_id,
            claim_date=data.claim_date,
            description=data.description,
            total_amount=total_amount,
            approved_amount=total_amount,
            currency=data.currency,
            status=ExpenseClaimStatus.DRAFT
        )
        db.add(claim)
        await db.flush()

        for item in items_to_create:
            item.claim_id = claim.id
            db.add(item)

        await db.commit()
        
        res_full = await db.execute(
            select(ExpenseClaim)
            .options(selectinload(ExpenseClaim.items))
            .where(ExpenseClaim.id == claim.id)
        )
        return res_full.scalar_one()

    @staticmethod
    async def submit_claim(db: AsyncSession, tenant_id: uuid.UUID, claim_id: uuid.UUID) -> ExpenseClaim:
        res = await db.execute(
            select(ExpenseClaim).where(
                and_(ExpenseClaim.id == claim_id, ExpenseClaim.tenant_id == tenant_id)
            )
        )
        claim = res.scalar_one_or_none()
        if not claim or claim.status != ExpenseClaimStatus.DRAFT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Claim not found or not in draft status.")

        claim.status = ExpenseClaimStatus.SUBMITTED

        instance = await WorkflowService.start_approval_instance(
            db, tenant_id, "EXPENSE_CLAIM", claim.id, claim.employee_id
        )
        claim.approval_instance_id = instance.id

        await db.commit()

        res_full = await db.execute(
            select(ExpenseClaim)
            .options(selectinload(ExpenseClaim.items))
            .where(ExpenseClaim.id == claim.id)
        )
        return res_full.scalar_one()

    @staticmethod
    async def approve_claim(db: AsyncSession, tenant_id: uuid.UUID, claim_id: uuid.UUID) -> ExpenseClaim:
        res = await db.execute(
            select(ExpenseClaim)
            .options(selectinload(ExpenseClaim.items))
            .where(
                and_(ExpenseClaim.id == claim_id, ExpenseClaim.tenant_id == tenant_id)
            )
        )
        claim = res.scalar_one_or_none()
        if not claim or claim.status not in (ExpenseClaimStatus.SUBMITTED, ExpenseClaimStatus.UNDER_REVIEW):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Claim not found or not pending approval.")

        claim.status = ExpenseClaimStatus.APPROVED
        for item in claim.items:
            item.status = ExpenseItemStatus.APPROVED

        # Queue Reimbursement Entry
        reimb = Reimbursement(
            tenant_id=tenant_id,
            claim_id=claim.id,
            employee_id=claim.employee_id,
            amount=claim.approved_amount,
            payment_method=ReimbursementMethod.PAYROLL,
            taxability=ReimbursementTaxability.NON_TAXABLE,
            status=ReimbursementStatus.PENDING
        )
        db.add(reimb)

        await db.commit()

        res_full = await db.execute(
            select(ExpenseClaim)
            .options(selectinload(ExpenseClaim.items))
            .where(ExpenseClaim.id == claim.id)
        )
        return res_full.scalar_one()

    @staticmethod
    async def process_reimbursement(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        reimbursement_id: uuid.UUID,
        req: ReimbursementProcessRequest
    ) -> Reimbursement:
        res = await db.execute(
            select(Reimbursement).where(
                and_(Reimbursement.id == reimbursement_id, Reimbursement.tenant_id == tenant_id)
            )
        )
        reimb = res.scalar_one_or_none()
        if not reimb or reimb.status != ReimbursementStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reimbursement not found or already processed.")

        reimb.payment_method = req.payment_method
        reimb.taxability = req.taxability
        reimb.payroll_period_id = req.payroll_period_id
        reimb.status = ReimbursementStatus.PROCESSED
        reimb.processed_at = datetime.now(timezone.utc)

        claim_res = await db.execute(select(ExpenseClaim).where(ExpenseClaim.id == reimb.claim_id))
        claim = claim_res.scalar_one()
        claim.status = ExpenseClaimStatus.REIMBURSED
        claim.reimbursed_at = datetime.now(timezone.utc)

        # Record Financial Transaction Ledger
        await FinancialTransactionService.record_transaction(
            db=db,
            tenant_id=tenant_id,
            employee_id=reimb.employee_id,
            transaction_type=FinancialTransactionType.EXPENSE_REIMBURSEMENT,
            reference_id=str(claim.id),
            amount=reimb.amount,
            direction=TransactionDirection.CREDIT,
            currency=claim.currency
        )

        await db.commit()
        await db.refresh(reimb)
        return reimb
