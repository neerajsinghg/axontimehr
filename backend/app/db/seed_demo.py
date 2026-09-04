import asyncio
import uuid
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.core.security import get_password_hash

async def seed_demo_data():
    """
    Populates safe, realistic multi-tenant demo data for AxonTimeHR sandbox environments.
    """
    async with AsyncSessionLocal() as db:
        print("==> Seeding AxonTimeHR Multi-Tenant Demo Data...")

        # 1. Seed Demo Tenant
        tenant_id = str(uuid.uuid4())
        tenant = Tenant(
            id=tenant_id,
            name="AxonTimeHR Demo Enterprise Corp",
            code="DEMO-CORP",
            is_active=True
        )
        db.add(tenant)

        # 2. Seed Admin User
        admin_email = "admin@axontimehr.com"
        admin_pass = get_password_hash("Password123!")
        user = User(
            email=admin_email,
            password_hash=admin_pass,
            first_name="Demo",
            last_name="Administrator",
            role=UserRole.SUPER_ADMIN,
            tenant_id=tenant_id,
            is_active=True,
            is_verified=True
        )
        db.add(user)

        await db.commit()
        print("==> Demo Data Seeding Completed Successfully!")
        print(f"    Tenant: {tenant.name} ({tenant.code})")
        print(f"    Admin User: {admin_email} / Password123!")

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
