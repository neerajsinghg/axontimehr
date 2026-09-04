import asyncio
import sys
import os
from datetime import datetime, timedelta, timezone

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.core.security import hash_password
from app.models import User, MobileOTP

DEMO_ACCOUNTS = [
    {
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@axoncorp.com",
        "phone": "+919900000001",
        "password": "Password123!",
        "otp": "123456"
    },
    {
        "first_name": "HR",
        "last_name": "Manager",
        "email": "hr.manager@axoncorp.com",
        "phone": "+919900000002",
        "password": "Password123!",
        "otp": "123456"
    },
    {
        "first_name": "Alex",
        "last_name": "Morgan",
        "email": "employee1@axoncorp.com",
        "phone": "+919900000003",
        "password": "Password123!",
        "otp": "123456"
    },
    {
        "first_name": "Sarah",
        "last_name": "Connor",
        "email": "employee2@axoncorp.com",
        "phone": "+919900000004",
        "password": "Password123!",
        "otp": "123456"
    },
    {
        "first_name": "David",
        "last_name": "Miller",
        "email": "employee3@axoncorp.com",
        "phone": "+919900000005",
        "password": "Password123!",
        "otp": "123456"
    }
]

async def create_demo_users():
    pwd_hash = hash_password("Password123!")
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=365) # Valid for 1 year for demo testing

    async with AsyncSessionLocal() as db:
        print("==================================================================")
        print("CREATING 5 DEDICATED DEMO ACCOUNTS WITH FIXED PWD AND OTP")
        print("==================================================================")

        for acc in DEMO_ACCOUNTS:
            # 1. Create or update User
            res_u = await db.execute(select(User).where(User.email == acc["email"]))
            u = res_u.scalar_one_or_none()
            if not u:
                u = User(
                    email=acc["email"],
                    phone_number=acc["phone"],
                    password_hash=pwd_hash,
                    first_name=acc["first_name"],
                    last_name=acc["last_name"],
                    is_active=True,
                    is_verified=True,
                    is_locked=False,
                    failed_login_attempts=0
                )
                db.add(u)
                await db.flush()
                print(f"Created User: {acc['email']}")
            else:
                u.phone_number = acc["phone"]
                u.password_hash = pwd_hash
                u.is_active = True
                u.is_verified = True
                u.is_locked = False
                print(f"Updated User: {acc['email']}")

            # 2. Insert Active Mobile OTP
            otp_record = MobileOTP(
                phone_number=acc["phone"],
                otp_code=acc["otp"],
                is_used=False,
                expires_at=expires_at
            )
            db.add(otp_record)

        await db.commit()
        print("==================================================================")
        print("5 DEMO ACCOUNTS CREATED SUCCESSFULLY!")
        print("==================================================================")

if __name__ == "__main__":
    asyncio.run(create_demo_users())
