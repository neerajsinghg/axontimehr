import asyncio
import sys
import os
from uuid import UUID

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import AsyncSessionLocal
from app.models import (
    Company,
    Department,
    Designation,
    Branch,
    Employee,
    User,
    AuthSession,
    PasswordResetToken,
    EmailVerificationToken,
    MobileOTP
)

SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "axontimehr.db")
sqlite_url = f"sqlite:///{SQLITE_DB_PATH}"

def get_sqlite_session():
    engine = create_engine(sqlite_url)
    Session = sessionmaker(bind=engine)
    return Session()

async def migrate_data():
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"Source SQLite database not found at {SQLITE_DB_PATH}. Skipping data migration.")
        return

    print("==================================================================")
    print("STARTING SYSTEMATIC DATA MIGRATION FROM SQLITE TO POSTGRESQL")
    print(f"Source: {sqlite_url}")
    print(f"Target: PostgreSQL localhost:5432/axontimehr")
    print("==================================================================")

    sqlite_db = get_sqlite_session()

    async with AsyncSessionLocal() as pg_db:
        # 1. Migrate Companies
        companies = sqlite_db.query(Company).all()
        print(f"Migrating {len(companies)} Company records...")
        for c in companies:
            pg_company = Company(
                id=c.id,
                name=c.name,
                code=c.code,
                domain=c.domain,
                is_active=c.is_active,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            await pg_db.merge(pg_company)
        await pg_db.commit()

        # 2. Migrate Departments
        departments = sqlite_db.query(Department).all()
        print(f"Migrating {len(departments)} Department records...")
        for d in departments:
            pg_dept = Department(
                id=d.id,
                organization_id=d.organization_id,
                name=d.name,
                code=d.code,
                is_active=d.is_active,
                created_at=d.created_at,
                updated_at=d.updated_at
            )
            await pg_db.merge(pg_dept)
        await pg_db.commit()

        # 3. Migrate Designations
        designations = sqlite_db.query(Designation).all()
        print(f"Migrating {len(designations)} Designation records...")
        for desg in designations:
            pg_desg = Designation(
                id=desg.id,
                organization_id=desg.organization_id,
                name=desg.name,
                code=desg.code,
                is_active=desg.is_active,
                created_at=desg.created_at,
                updated_at=desg.updated_at
            )
            await pg_db.merge(pg_desg)
        await pg_db.commit()

        # 4. Migrate Branches
        branches = sqlite_db.query(Branch).all()
        print(f"Migrating {len(branches)} Branch records...")
        for b in branches:
            pg_branch = Branch(
                id=b.id,
                organization_id=b.organization_id,
                name=b.name,
                code=b.code,
                city=b.city,
                state=b.state,
                country=b.country,
                is_active=b.is_active,
                created_at=b.created_at,
                updated_at=b.updated_at
            )
            await pg_db.merge(pg_branch)
        await pg_db.commit()

        # 5. Migrate Employees
        employees = sqlite_db.query(Employee).all()
        print(f"Migrating {len(employees)} Employee records...")
        for emp in employees:
            pg_emp = Employee(
                id=emp.id,
                organization_id=emp.organization_id,
                employee_id=emp.employee_id,
                first_name=emp.first_name,
                last_name=emp.last_name,
                email=emp.email,
                phone=emp.phone,
                date_of_birth=emp.date_of_birth,
                joining_date=emp.joining_date,
                department_id=emp.department_id,
                designation_id=emp.designation_id,
                branch_id=emp.branch_id,
                employment_type=emp.employment_type,
                status=emp.status,
                avatar_url=emp.avatar_url,
                created_at=emp.created_at,
                updated_at=emp.updated_at
            )
            await pg_db.merge(pg_emp)
        await pg_db.commit()

        # 6. Migrate Users
        users = sqlite_db.query(User).all()
        print(f"Migrating {len(users)} User records...")
        for u in users:
            pg_user = User(
                id=u.id,
                email=u.email,
                phone_number=getattr(u, "phone_number", None),
                password_hash=u.password_hash,
                first_name=u.first_name,
                last_name=u.last_name,
                is_active=u.is_active,
                is_verified=u.is_verified,
                is_locked=u.is_locked,
                failed_login_attempts=u.failed_login_attempts,
                locked_until=u.locked_until,
                last_login_at=u.last_login_at,
                password_changed_at=u.password_changed_at,
                created_at=u.created_at,
                updated_at=u.updated_at
            )
            await pg_db.merge(pg_user)
        await pg_db.commit()

        # 7. Migrate Auth Sessions
        sessions = sqlite_db.query(AuthSession).all()
        print(f"Migrating {len(sessions)} AuthSession records...")
        for s in sessions:
            pg_session = AuthSession(
                id=s.id,
                user_id=s.user_id,
                token_jti=s.token_jti,
                refresh_token_hash=s.refresh_token_hash,
                ip_address=s.ip_address,
                user_agent=s.user_agent,
                is_revoked=s.is_revoked,
                expires_at=s.expires_at,
                created_at=s.created_at,
                updated_at=s.updated_at
            )
            await pg_db.merge(pg_session)
        await pg_db.commit()

        # 8. Migrate Mobile OTPs
        try:
            otps = sqlite_db.query(MobileOTP).all()
            print(f"Migrating {len(otps)} MobileOTP records...")
            for otp in otps:
                pg_otp = MobileOTP(
                    id=otp.id,
                    phone_number=otp.phone_number,
                    otp_code=otp.otp_code,
                    is_used=otp.is_used,
                    expires_at=otp.expires_at,
                    created_at=otp.created_at,
                    updated_at=otp.updated_at
                )
                await pg_db.merge(pg_otp)
            await pg_db.commit()
        except Exception as e:
            print(f"Note: MobileOTP query skipped: {e}")

    sqlite_db.close()
    print("==================================================================")
    print("DATA MIGRATION COMPLETED SUCCESSFULLY TO POSTGRESQL!")
    print("==================================================================")

if __name__ == "__main__":
    asyncio.run(migrate_data())
