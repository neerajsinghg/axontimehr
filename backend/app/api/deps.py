from typing import Callable
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import decode_jwt_token
from app.models.user import User
from app.models.organization import Company
from app.services.organization_service import OrganizationService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    res = await db.execute(select(User).where(User.id == UUID(user_id_str)))
    user = res.scalar_one_or_none()

    if not user:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is inactive")
    if user.is_locked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is locked")

    return user

async def get_current_tenant_id(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UUID:
    if current_user.tenant_id:
        return current_user.tenant_id
    
    # If unassigned, resolve default tenant
    company = await OrganizationService.get_or_create_default_company(db)
    current_user.tenant_id = company.id
    await db.commit()
    return company.id

def require_permission(permission: str) -> Callable:
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        # Super-admin or active users pass default RBAC in Phase 3
        return current_user
    return permission_checker
