import asyncio
import random
import sys
import os
from datetime import date, datetime, timedelta, timezone

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.core.security import hash_password
from app.models import Company, Department, Designation, Branch, Employee, User

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
    "Shaurya", "Atharva", "Ananya", "Diya", "Pari", "Anika", "Navya", "Angel", "Myra", "Riya",
    "Emma", "Liam", "Noah", "Olivia", "Ava", "William", "Sophia", "Jackson", "Isabella", "Lucas",
    "Mia", "Ethan", "Harper", "Oliver", "Evelyn", "Benjamin", "Abigail", "Elijah", "Emily", "James",
    "Charlotte", "Alexander", "Amelia", "Sebastian", "Sofia", "Henry", "Ella", "Daniel", "Grace", "Matthew",
    "Rajesh", "Priya", "Amit", "Neha", "Vikram", "Pooja", "Suresh", "Kavita", "Rohan", "Sneha",
    "Deepak", "Swati", "Manish", "Sunita", "Sanjay", "Meena", "Rahul", "Anita", "Vijay", "Geeta"
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Patel", "Singh", "Kumar", "Mehta", "Joshi", "Rao", "Nair",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Kulkarni", "Deshmukh", "Chaudhary", "Reddy", "Iyer", "Banerjee", "Chatterjee", "Bose", "Dutta", "Das"
]

DEPARTMENTS_DATA = [
    ("Engineering", "ENG"),
    ("Human Resources", "HR"),
    ("Sales & Business", "SALES"),
    ("Finance & Accounts", "FIN"),
    ("Operations", "OPS"),
    ("Marketing & Growth", "MKTG"),
]

DESIGNATIONS_DATA = [
    ("Senior Software Engineer", "SR_SE"),
    ("Frontend Developer", "FE_DEV"),
    ("Backend Engineer", "BE_ENG"),
    ("HR Operations Manager", "HR_MGR"),
    ("Sales Lead", "SALES_LEAD"),
    ("Financial Analyst", "FIN_ANALYST"),
    ("DevOps Specialist", "DEVOPS_SPEC"),
    ("Product Designer", "PROD_DES"),
]

BRANCHES_DATA = [
    ("Global Headquarters", "HQ_NYC", "New York", "NY", "USA"),
    ("EMEA Technology Centre", "HUB_LDN", "London", "Greater London", "UK"),
    ("APAC Regional Hub", "OFF_TYO", "Tokyo", "Kanto", "Japan"),
    ("India Operations & R&D", "RD_BLR", "Bangalore", "Karnataka", "India"),
]

async def seed_data():
    print("==================================================================")
    print("STARTING 100+ USER & EMPLOYEE SEEDING INTO POSTGRESQL")
    print("==================================================================")

    async with AsyncSessionLocal() as db:
        # 1. Ensure Company
        res_comp = await db.execute(select(Company).where(Company.code == "AXON_CORP"))
        company = res_comp.scalar_one_or_none()
        if not company:
            company = Company(
                name="Axon Enterprise Technologies",
                code="AXON_CORP",
                domain="axoncorp.com",
                is_active=True
            )
            db.add(company)
            await db.flush()

        # 2. Ensure Departments
        depts = []
        for name, code in DEPARTMENTS_DATA:
            res = await db.execute(select(Department).where(Department.code == code))
            dept = res.scalar_one_or_none()
            if not dept:
                dept = Department(organization_id=company.id, name=name, code=code, is_active=True)
                db.add(dept)
                await db.flush()
            depts.append(dept)

        # 3. Ensure Designations
        desgs = []
        for title, code in DESIGNATIONS_DATA:
            res = await db.execute(select(Designation).where(Designation.code == code))
            desg = res.scalar_one_or_none()
            if not desg:
                desg = Designation(organization_id=company.id, name=title, code=code, is_active=True)
                db.add(desg)
                await db.flush()
            desgs.append(desg)

        # 4. Ensure Branches
        branches = []
        for name, code, city, state, country in BRANCHES_DATA:
            res = await db.execute(select(Branch).where(Branch.code == code))
            b = res.scalar_one_or_none()
            if not b:
                b = Branch(organization_id=company.id, name=name, code=code, city=city, state=state, country=country, is_active=True)
                db.add(b)
                await db.flush()
            branches.append(b)

        # 5. Generate 110 Users & Employees
        default_pwd_hash = hash_password("Password123!")
        statuses = ["ACTIVE"] * 85 + ["ON_LEAVE"] * 15 + ["INACTIVE"] * 10
        random.seed(42)

        created_users = 0
        created_employees = 0

        for i in range(1001, 1111):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            email = f"{fn.lower()}.{ln.lower()}_{i}@axoncorp.com"
            phone = f"+9198765{i:05d}"
            emp_code = f"EMP-{i}"
            status_val = statuses[(i - 1001) % len(statuses)]
            gender = "Male" if i % 2 == 0 else "Female"

            dept = random.choice(depts)
            desg = random.choice(desgs)
            branch = random.choice(branches)

            dob = date(1985 + (i % 15), (i % 12) + 1, (i % 28) + 1)
            joining = date(2021 + (i % 4), (i % 12) + 1, (i % 28) + 1)

            # Check User existence
            res_u = await db.execute(select(User).where(User.email == email))
            u = res_u.scalar_one_or_none()
            if not u:
                u = User(
                    email=email,
                    phone_number=phone,
                    password_hash=default_pwd_hash,
                    first_name=fn,
                    last_name=ln,
                    is_active=(status_val != "INACTIVE"),
                    is_verified=True,
                    is_locked=False,
                    failed_login_attempts=0
                )
                db.add(u)
                created_users += 1

            # Check Employee existence
            res_e = await db.execute(select(Employee).where(Employee.employee_id == emp_code))
            e = res_e.scalar_one_or_none()
            if not e:
                e = Employee(
                    organization_id=company.id,
                    department_id=dept.id,
                    designation_id=desg.id,
                    branch_id=branch.id,
                    employee_id=emp_code,
                    first_name=fn,
                    last_name=ln,
                    email=email,
                    phone=phone,
                    date_of_birth=dob,
                    joining_date=joining,
                    employment_type="FULL_TIME",
                    status=status_val,
                    avatar_url=f"https://images.unsplash.com/photo-{1500000000000 + (i % 50)}?w=150&auto=format&fit=crop&q=80"
                )
                db.add(e)
                created_employees += 1


        await db.commit()

        # Print metrics
        res_user_count = await db.execute(select(User))
        total_users = len(res_user_count.scalars().all())

        res_emp_count = await db.execute(select(Employee))
        total_emps = len(res_emp_count.scalars().all())

        print(f"Successfully processed seeding:")
        print(f"  - New Users Added: {created_users}")
        print(f"  - New Employees Added: {created_employees}")
        print(f"  - Total PostgreSQL Users: {total_users}")
        print(f"  - Total PostgreSQL Employees: {total_emps}")
        print("==================================================================")
        print("SEEDING COMPLETE!")

if __name__ == "__main__":
    asyncio.run(seed_data())
