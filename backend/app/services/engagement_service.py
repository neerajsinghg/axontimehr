import uuid
from typing import List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.engagement import Survey, SurveyQuestion, SurveyResponse, EmployeeFeedback, SurveyType, QuestionType
from app.schemas.performance import SurveyCreate, SurveySubmitAnswer, EmployeeFeedbackCreate


class EngagementService:
    @staticmethod
    async def create_survey(db: AsyncSession, tenant_id: uuid.UUID, data: SurveyCreate) -> Survey:
        survey = Survey(
            tenant_id=str(tenant_id),
            title=data.title,
            description=data.description,
            survey_type=data.survey_type,
            start_date=data.start_date,
            end_date=data.end_date,
            is_anonymous=data.is_anonymous,
        )
        db.add(survey)
        await db.commit()
        await db.refresh(survey)

        # Add standard pulse survey questions
        q1 = SurveyQuestion(survey_id=survey.id, question_text="On a scale of 1 to 5, how satisfied are you with your workplace environment?", question_type=QuestionType.RATING_1_5, display_order=1)
        q2 = SurveyQuestion(survey_id=survey.id, question_text="How likely are you to recommend our organization as a great place to work?", question_type=QuestionType.NPS_0_10, display_order=2)
        q3 = SurveyQuestion(survey_id=survey.id, question_text="What is one thing management can improve to support your growth?", question_type=QuestionType.TEXT, display_order=3)
        db.add_all([q1, q2, q3])
        await db.commit()

        return survey

    @staticmethod
    async def get_surveys(db: AsyncSession, tenant_id: uuid.UUID) -> List[Survey]:
        res = await db.execute(
            select(Survey).where(Survey.tenant_id == str(tenant_id)).order_by(Survey.created_at.desc())
        )
        surveys = list(res.scalars().all())
        if not surveys:
            # Seed default pulse survey
            today = datetime.now(timezone.utc).date()
            default_survey = Survey(
                tenant_id=str(tenant_id),
                title="Q3 Quarterly Employee Satisfaction & Culture Pulse",
                description="Anonymous 3-minute pulse survey to gauge workplace sentiment, management support, and eNPS",
                survey_type=SurveyType.PULSE,
                start_date=today,
                end_date=today,
                is_anonymous=True,
            )
            db.add(default_survey)
            await db.commit()

            q1 = SurveyQuestion(survey_id=default_survey.id, question_text="How supported do you feel by your direct manager?", question_type=QuestionType.RATING_1_5, display_order=1)
            q2 = SurveyQuestion(survey_id=default_survey.id, question_text="How satisfied are you with work-life balance and flexible hours?", question_type=QuestionType.RATING_1_5, display_order=2)
            q3 = SurveyQuestion(survey_id=default_survey.id, question_text="Any suggestions for team activities or wellness initiatives?", question_type=QuestionType.TEXT, display_order=3)
            db.add_all([q1, q2, q3])
            await db.commit()

            res_new = await db.execute(
                select(Survey).where(Survey.tenant_id == str(tenant_id)).order_by(Survey.created_at.desc())
            )
            surveys = list(res_new.scalars().all())

        return surveys

    @staticmethod
    async def submit_response(db: AsyncSession, tenant_id: uuid.UUID, survey_id: str, employee_id: str, answers: List[SurveySubmitAnswer]) -> bool:
        res = await db.execute(select(Survey).where(Survey.id == survey_id))
        survey = res.scalar_one_or_none()
        if not survey:
            raise ValueError("Survey not found")

        # Anonymity redaction: set employee_id to None if survey is anonymous
        emp_id = None if survey.is_anonymous else employee_id

        for a in answers:
            resp = SurveyResponse(
                tenant_id=str(tenant_id),
                survey_id=survey_id,
                question_id=a.question_id,
                employee_id=emp_id,
                rating_value=a.answer_rating,
                text_value=a.answer_text,
            )
            db.add(resp)
        await db.commit()
        return True

    @staticmethod
    async def create_feedback(db: AsyncSession, tenant_id: uuid.UUID, employee_id: str, data: EmployeeFeedbackCreate) -> EmployeeFeedback:
        emp_id = None if data.is_anonymous else employee_id
        fb = EmployeeFeedback(
            tenant_id=str(tenant_id),
            employee_id=emp_id,
            category=data.category,
            subject=data.subject,
            message=data.message,
            is_anonymous=data.is_anonymous,
        )
        db.add(fb)
        await db.commit()
        await db.refresh(fb)
        return fb
