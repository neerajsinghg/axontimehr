import uuid
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.performance import (
    PerformanceCycle,
    PerformanceCycleConfig,
    Goal,
    GoalProgressHistory,
    PerformanceReview,
    PeerReview360,
    PerformanceCalibration,
    CycleStatus,
    GoalStatus,
    ReviewStatus,
)
from app.schemas.performance import (
    PerformanceCycleCreate,
    GoalCreate,
    GoalProgressUpdate,
    SelfAssessmentSubmit,
    ManagerAssessmentSubmit,
    PeerReviewSubmit,
    CalibrationSubmit,
)


class PerformanceService:
    @staticmethod
    async def create_cycle(db: AsyncSession, tenant_id: uuid.UUID, data: PerformanceCycleCreate) -> PerformanceCycle:
        cycle = PerformanceCycle(
            tenant_id=str(tenant_id),
            name=data.name,
            description=data.description,
            cycle_type=data.cycle_type,
            start_date=data.start_date,
            end_date=data.end_date,
            self_review_end=data.self_review_end,
            manager_review_end=data.manager_review_end,
            peer_review_end=data.peer_review_end,
            calibration_end=data.calibration_end,
            status=CycleStatus.GOAL_SETTING,
        )
        db.add(cycle)
        await db.commit()
        await db.refresh(cycle)

        # Create default cycle configuration (60% goals, 20% competency, 20% manager)
        config = PerformanceCycleConfig(
            tenant_id=str(tenant_id),
            cycle_id=cycle.id,
            goal_weightage=Decimal("60.00"),
            competency_weightage=Decimal("20.00"),
            manager_weightage=Decimal("20.00"),
        )
        db.add(config)
        await db.commit()
        return cycle

    @staticmethod
    async def get_cycles(db: AsyncSession, tenant_id: uuid.UUID) -> List[PerformanceCycle]:
        res = await db.execute(
            select(PerformanceCycle)
            .where(PerformanceCycle.tenant_id == str(tenant_id))
            .order_by(PerformanceCycle.created_at.desc())
        )
        return list(res.scalars().all())

    @staticmethod
    async def create_goal(db: AsyncSession, tenant_id: uuid.UUID, data: GoalCreate) -> Goal:
        goal = Goal(
            tenant_id=str(tenant_id),
            cycle_id=data.cycle_id,
            employee_id=data.employee_id,
            parent_goal_id=data.parent_goal_id,
            title=data.title,
            description=data.description,
            goal_type=data.goal_type,
            baseline_value=data.baseline_value,
            target_value=data.target_value,
            current_value=data.current_value,
            unit=data.unit,
            weightage=data.weightage,
            due_date=data.due_date,
            status=GoalStatus.IN_PROGRESS,
        )
        db.add(goal)
        await db.commit()
        await db.refresh(goal)
        return goal

    @staticmethod
    async def update_goal_progress(db: AsyncSession, goal_id: str, data: GoalProgressUpdate) -> Goal:
        res = await db.execute(select(Goal).where(Goal.id == goal_id))
        goal = res.scalar_one_or_none()
        if not goal:
            raise ValueError("Goal not found")

        prev_val = goal.current_value
        goal.current_value = data.current_value

        # Calculate progress %
        if goal.target_value > goal.baseline_value:
            range_val = goal.target_value - goal.baseline_value
            achieved = goal.current_value - goal.baseline_value
            pct = (achieved / range_val) * Decimal("100.00")
            goal.progress_pct = max(Decimal("0.00"), min(Decimal("100.00"), pct))
            goal.achievement_pct = goal.progress_pct

        if goal.progress_pct >= Decimal("100.00"):
            goal.status = GoalStatus.COMPLETED

        history = GoalProgressHistory(
            goal_id=goal.id,
            previous_value=prev_val,
            new_value=data.current_value,
            progress_pct=goal.progress_pct,
            comments=data.comments,
        )
        db.add(history)
        await db.commit()
        await db.refresh(goal)
        return goal

    @staticmethod
    async def get_goals(db: AsyncSession, tenant_id: uuid.UUID, employee_id: Optional[str] = None) -> List[Goal]:
        query = select(Goal).where(Goal.tenant_id == str(tenant_id))
        if employee_id:
            query = query.where(Goal.employee_id == employee_id)
        res = await db.execute(query.order_by(Goal.created_at.desc()))
        return list(res.scalars().all())

    @staticmethod
    async def get_or_create_review(db: AsyncSession, tenant_id: uuid.UUID, cycle_id: str, employee_id: str) -> PerformanceReview:
        res = await db.execute(
            select(PerformanceReview).where(
                PerformanceReview.tenant_id == str(tenant_id),
                PerformanceReview.cycle_id == cycle_id,
                PerformanceReview.employee_id == employee_id,
            )
        )
        review = res.scalar_one_or_none()
        if not review:
            review = PerformanceReview(
                tenant_id=str(tenant_id),
                cycle_id=cycle_id,
                employee_id=employee_id,
                status=ReviewStatus.SELF_ASSESSMENT_PENDING,
            )
            db.add(review)
            await db.commit()
            await db.refresh(review)
        return review

    @staticmethod
    async def submit_self_assessment(db: AsyncSession, review_id: str, data: SelfAssessmentSubmit) -> PerformanceReview:
        res = await db.execute(select(PerformanceReview).where(PerformanceReview.id == review_id))
        review = res.scalar_one_or_none()
        if not review:
            raise ValueError("Review record not found")

        review.self_score = data.self_score
        review.employee_comments = data.employee_comments
        review.self_submitted_at = datetime.now(timezone.utc)
        review.status = ReviewStatus.MANAGER_REVIEW_PENDING

        await db.commit()
        await db.refresh(review)
        return review

    @staticmethod
    async def submit_manager_assessment(db: AsyncSession, review_id: str, data: ManagerAssessmentSubmit) -> PerformanceReview:
        res = await db.execute(select(PerformanceReview).where(PerformanceReview.id == review_id))
        review = res.scalar_one_or_none()
        if not review:
            raise ValueError("Review record not found")

        review.manager_score = data.manager_score
        review.manager_submitted_at = datetime.now(timezone.utc)

        # Calculate final weighted score (60% goals/self, 40% manager)
        if review.self_score is not None:
            review.calculated_score = (review.self_score * Decimal("0.4")) + (data.manager_score * Decimal("0.6"))
        else:
            review.calculated_score = data.manager_score

        review.final_score = review.calculated_score
        review.status = ReviewStatus.FINAL_REVIEW_PENDING

        await db.commit()
        await db.refresh(review)
        return review

    @staticmethod
    async def submit_calibration(db: AsyncSession, tenant_id: uuid.UUID, calibrated_by_id: str, data: CalibrationSubmit) -> PerformanceReview:
        res = await db.execute(select(PerformanceReview).where(PerformanceReview.id == data.review_id))
        review = res.scalar_one_or_none()
        if not review:
            raise ValueError("Review record not found")

        orig = review.final_score or review.calculated_score or Decimal("3.00")
        calib_rec = PerformanceCalibration(
            tenant_id=str(tenant_id),
            review_id=review.id,
            original_score=orig,
            calibrated_score=data.calibrated_score,
            reason=data.reason,
            calibrated_by_id=calibrated_by_id,
        )
        db.add(calib_rec)

        review.calibrated_score = data.calibrated_score
        review.final_score = data.calibrated_score
        review.calibrated_at = datetime.now(timezone.utc)
        review.status = ReviewStatus.FINALIZED
        review.finalized_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(review)
        return review
