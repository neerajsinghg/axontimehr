import asyncio
from datetime import date, timedelta
import random
import uuid
from sqlalchemy import select
from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
from app.models.organization import Company, Department, Designation, Branch
from app.models.employee import Employee
from app.core.logging import logger

FIRST_NAMES = [
    "Alex", "Amara", "Arjun", "Aria", "Benjamin", "Chloe", "Daniel", "Elena", "Ethan", "Fatima",
    "Gabriel", "Hannah", "Ibrahim", "Isabella", "Jack", "Jasmine", "Kavya", "Liam", "Maya", "Nathan",
    "Olivia", "Parth", "Rachel", "Rohan", "Sophia", "Tariq", "Victoria", "William", "Yusuf", "Zoe",
    "Aditya", "Ananya", "Brian", "Camila", "David", "Emma", "Farhan", "Grace", "Harsh", "Ines",
    "Julian", "Kira", "Lucas", "Meera", "Noah", "Priya", "Quentin", "Riya", "Samuel", "Tara"
]

LAST_NAMES = [
    "Anderson", "Bhagat", "Chen", "Deshmukh", "Evans", "Fernandez", "Gupta", "Hoffman", "Iyer", "Joshi",
    "Khan", "Kumar", "Lopez", "Mehta", "Nair", "Patel", "Rao", "Sharma", "Singh", "Taylor",
    "Verma", "Williams", "Yilmaz", "Zhang", "Agarwal", "Bhatia", "Chopra", "Dutta", "Gomez", "Kulkarni"
]

DEPARTMENTS_DATA = [
    ("Engineering", "ENG"),
    ("Human Resources", "HR"),
    ("Finance & Accounting", "FIN"),
    ("Sales & Business Development", "SALES"),
    ("Marketing", "MKT"),
    ("Operations & Support", "OPS"),
]

DESIGNATIONS_DATA = [
    ("Software Engineer", "SWE"),
    ("Senior Software Engineer", "SR_SWE"),
    ("Tech Lead", "TL"),
    ("HR Manager", "HRM"),
    ("Financial Analyst", "FA"),
    ("Sales Executive", "SE"),
    ("Marketing Specialist", "MS"),
    ("Operations Lead", "OPS_LEAD"),
]

BRANCHES_DATA = [
    ("Global Headquarters", "HQ", "New York", "NY", "USA"),
    ("Technology Innovation Hub", "HUB", "San Francisco", "CA", "USA"),
    ("EMEA Regional Office", "EMEA", "London", "Greater London", "UK"),
    ("APAC Enterprise Center", "APAC", "Singapore", "Central", "Singapore"),
]

async def seed_data() -> None:
    logger.info("Initializing database table creation...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if already seeded
        result = await session.execute(select(Employee))
        existing_employees = result.scalars().all()
        if len(existing_employees) >= 100:
            logger.info(f"Database already contains {len(existing_employees)} employees. Skipping seed.")
            return

        logger.info("Seeding Company, Departments, Designations, and Branches...")

        # 1. Company
        res_comp = await session.execute(select(Company).where(Company.code == "AXON_CORP"))
        company = res_comp.scalar_one_or_none()
        if not company:
            company = Company(
                id=uuid.uuid4(),
                name="Axon Enterprise Technologies",
                code="AXON_CORP",
                domain="axoncorp.com",
                is_active=True
            )
            session.add(company)
            await session.flush()

        # 2. Departments
        departments = []
        for name, code in DEPARTMENTS_DATA:
            res_d = await session.execute(select(Department).where(Department.organization_id == company.id, Department.code == code))
            dept = res_d.scalar_one_or_none()
            if not dept:
                dept = Department(
                    id=uuid.uuid4(),
                    organization_id=company.id,
                    name=name,
                    code=code,
                    is_active=True
                )
                session.add(dept)
                await session.flush()
            departments.append(dept)

        # 3. Designations
        designations = []
        for name, code in DESIGNATIONS_DATA:
            res_ds = await session.execute(select(Designation).where(Designation.organization_id == company.id, Designation.code == code))
            desig = res_ds.scalar_one_or_none()
            if not desig:
                desig = Designation(
                    id=uuid.uuid4(),
                    organization_id=company.id,
                    name=name,
                    code=code,
                    is_active=True
                )
                session.add(desig)
                await session.flush()
            designations.append(desig)

        # 4. Branches
        branches = []
        for name, code, city, state, country in BRANCHES_DATA:
            res_b = await session.execute(select(Branch).where(Branch.organization_id == company.id, Branch.code == code))
            branch = res_b.scalar_one_or_none()
            if not branch:
                branch = Branch(
                    id=uuid.uuid4(),
                    organization_id=company.id,
                    name=name,
                    code=code,
                    city=city,
                    state=state,
                    country=country,
                    is_active=True
                )
                session.add(branch)
                await session.flush()
            branches.append(branch)

        # 5. Employees (105 dummy records)
        logger.info("Generating 105 realistic employee records...")
        base_date = date(2022, 1, 15)
        
        statuses = ["ACTIVE"] * 85 + ["ON_LEAVE"] * 12 + ["INACTIVE"] * 8
        random.shuffle(statuses)

        emp_count = 0
        for i in range(1, 106):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            emp_id_str = f"EMP-{1000 + i}"
            email = f"{first.lower()}.{last.lower()}{i}@axoncorp.com"
            phone = f"+1 (555) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
            joining = base_date + timedelta(days=random.randint(1, 1200))
            dob = date(1985, 1, 1) + timedelta(days=random.randint(1, 7000))
            
            dept = random.choice(departments)
            desig = random.choice(designations)
            branch = random.choice(branches)
            emp_status = statuses[i - 1]

            emp = Employee(
                id=uuid.uuid4(),
                organization_id=company.id,
                employee_id=emp_id_str,
                first_name=first,
                last_name=last,
                email=email,
                phone=phone,
                date_of_birth=dob,
                joining_date=joining,
                department_id=dept.id,
                designation_id=desig.id,
                branch_id=branch.id,
                employment_type=random.choice(["FULL_TIME", "FULL_TIME", "CONTRACT"]),
                status=emp_status,
                avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={first}{last}"
            )
            session.add(emp)
            emp_count += 1

        await session.commit()
        logger.info(f"Successfully seeded {emp_count} employee records into database!")

if __name__ == "__main__":
    asyncio.run(seed_data())
