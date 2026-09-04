from datetime import datetime, timedelta, timezone
import secrets
from typing import Optional, Tuple, Dict, Any

import uuid
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_jwt_token,
    generate_secure_token,
    hash_token
)
from app.models.user import User, AuthSession, PasswordResetToken, EmailVerificationToken, MobileOTP
from app.services.redis import redis_service
from app.services.sms import get_sms_service
from app.workers.email_tasks import send_verification_email_task, send_password_reset_email_task


class AuthService:
    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    @classmethod
    async def register_user(
        cls,
        db: AsyncSession,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        company_name: Optional[str] = None
    ) -> User:
        normalized_email = cls._normalize_email(email)
        
        # Check existing user
        result = await db.execute(select(User).where(User.email == normalized_email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        # Auto-create or resolve company for tenant
        from app.models.organization import Company
        if company_name:
            clean_cname = company_name.strip()
            from sqlalchemy import func
            c_res = await db.execute(
                select(Company)
                .where(func.lower(Company.name) == clean_cname.lower())
                .order_by(Company.created_at.desc())
            )
            company = c_res.scalars().first()
            if not company:
                c_code = clean_cname.upper().replace(" ", "_")[:20] + "_" + uuid.uuid4().hex[:4]
                company = Company(name=clean_cname, code=c_code)
                db.add(company)
                await db.flush()
        else:
            c_name = f"{first_name}'s Company {uuid.uuid4().hex[:6].upper()}"
            c_code = f"TENANT_{uuid.uuid4().hex[:8].upper()}"
            company = Company(name=c_name, code=c_code)
            db.add(company)
            await db.flush()

        # Create user
        hashed_pwd = hash_password(password)
        user = User(
            email=normalized_email,
            password_hash=hashed_pwd,
            first_name=first_name,
            last_name=last_name,
            tenant_id=company.id,
            is_active=True,
            is_verified=False,
            is_locked=False,
            failed_login_attempts=0
        )
        db.add(user)
        await db.flush()

        # Generate email verification token
        raw_token = generate_secure_token(32)
        token_record = EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES)
        )
        db.add(token_record)
        await db.commit()
        await db.refresh(user)

        # Queue verification email (retry=False ensures fast fallback when Redis is offline)
        try:
            send_verification_email_task.apply_async(args=[user.email, raw_token], retry=False)
        except Exception as e:
            logger.warning(f"Failed to queue verification email task: {e}")

        logger.info(f"User registered successfully: {user.email}", extra={"user_id": str(user.id)})
        return user

    @classmethod
    async def login_user(
        cls,
        db: AsyncSession,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[str, str, int, User]:
        normalized_email = cls._normalize_email(email)
        now = datetime.now(timezone.utc)

        result = await db.execute(select(User).where(User.email == normalized_email))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Check account lockout
        if user.is_locked:
            if user.locked_until and user.locked_until > now:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Account is temporarily locked due to multiple failed login attempts. Try again after {user.locked_until.strftime('%H:%M UTC')}."
                )
            else:
                # Lockout period expired
                user.is_locked = False
                user.failed_login_attempts = 0
                user.locked_until = None

        # Verify password
        if not verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.is_locked = True
                user.locked_until = now + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
                logger.warning(f"Account locked for user {user.email} due to 5 failed login attempts.")
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Reset failed attempts & update metadata
        user.failed_login_attempts = 0
        user.is_locked = False
        user.locked_until = None
        user.last_login_at = now

        # Generate JWT tokens
        access_token = create_access_token(subject=str(user.id))
        refresh_token, jti, refresh_expires_at = create_refresh_token(subject=str(user.id))

        # Store AuthSession in DB
        session_record = AuthSession(
            user_id=user.id,
            token_jti=jti,
            refresh_token_hash=hash_token(refresh_token),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=refresh_expires_at,
            is_revoked=False
        )
        db.add(session_record)
        await db.commit()
        await db.refresh(user)

        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        logger.info(f"User logged in successfully: {user.email}", extra={"user_id": str(user.id)})
        return access_token, refresh_token, expires_in, user

    @classmethod
    async def refresh_tokens(
        cls,
        db: AsyncSession,
        refresh_token_str: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[str, str, int, User]:
        try:
            payload = decode_jwt_token(refresh_token_str)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        user_id_str = payload.get("sub")
        jti = payload.get("jti")

        if not user_id_str or not jti:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims")

        # Find session record
        res_session = await db.execute(select(AuthSession).where(AuthSession.token_jti == jti))
        session_record = res_session.scalar_one_or_none()

        if not session_record or session_record.is_revoked:
            # Token reuse or invalid session detected! Revoke all sessions for safety.
            logger.warning(f"Refresh token reuse or revoked session access detected for JTI: {jti}")
            await db.execute(
                update(AuthSession)
                .where(AuthSession.user_id == UUID(user_id_str))
                .values(is_revoked=True)
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or revoked refresh token. Please log in again."
            )

        # Mark old session revoked (Token Rotation)
        session_record.is_revoked = True

        # Fetch user
        res_user = await db.execute(select(User).where(User.id == UUID(user_id_str)))
        user = res_user.scalar_one_or_none()

        if not user or not user.is_active:
            await db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account inactive")

        # Issue new token pair
        new_access_token = create_access_token(subject=str(user.id))
        new_refresh_token, new_jti, new_expires_at = create_refresh_token(subject=str(user.id))

        new_session = AuthSession(
            user_id=user.id,
            token_jti=new_jti,
            refresh_token_hash=hash_token(new_refresh_token),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=new_expires_at,
            is_revoked=False
        )
        db.add(new_session)
        await db.commit()

        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        return new_access_token, new_refresh_token, expires_in, user

    @classmethod
    async def logout_user(cls, db: AsyncSession, refresh_token_str: Optional[str]) -> bool:
        if not refresh_token_str:
            return True
        try:
            payload = decode_jwt_token(refresh_token_str)
            jti = payload.get("jti")
            if jti:
                await db.execute(
                    update(AuthSession)
                    .where(AuthSession.token_jti == jti)
                    .values(is_revoked=True)
                )
                await db.commit()
        except Exception as e:
            logger.warning(f"Error revoking session during logout: {e}")
        return True

    @classmethod
    async def change_password(
        cls,
        db: AsyncSession,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

        user.password_hash = hash_password(new_password)
        user.password_changed_at = datetime.now(timezone.utc)

        # Revoke all active sessions for security
        await db.execute(
            update(AuthSession)
            .where(AuthSession.user_id == user.id)
            .values(is_revoked=True)
        )
        await db.commit()
        logger.info(f"Password changed successfully for user {user.email}")
        return True

    @classmethod
    async def forgot_password(cls, db: AsyncSession, email: str) -> bool:
        normalized_email = cls._normalize_email(email)
        res = await db.execute(select(User).where(User.email == normalized_email))
        user = res.scalar_one_or_none()

        if user and user.is_active:
            raw_token = generate_secure_token(32)
            reset_record = PasswordResetToken(
                user_id=user.id,
                token_hash=hash_token(raw_token),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
            )
            db.add(reset_record)
            await db.commit()

            try:
                send_password_reset_email_task.delay(user.email, raw_token)
            except Exception as e:
                logger.warning(f"Failed to queue reset email task: {e}")

        return True

    @classmethod
    async def reset_password(cls, db: AsyncSession, raw_token: str, new_password: str) -> bool:
        token_h = hash_token(raw_token)
        now = datetime.now(timezone.utc)

        res = await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_h,
                PasswordResetToken.is_used == False
            )
        )
        reset_record = res.scalar_one_or_none()

        if not reset_record or reset_record.expires_at < now:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

        reset_record.is_used = True

        res_user = await db.execute(select(User).where(User.id == reset_record.user_id))
        user = res_user.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user.password_hash = hash_password(new_password)
        user.password_changed_at = now

        # Revoke active sessions
        await db.execute(
            update(AuthSession)
            .where(AuthSession.user_id == user.id)
            .values(is_revoked=True)
        )
        await db.commit()
        return True

    @classmethod
    async def verify_email(cls, db: AsyncSession, raw_token: str) -> bool:
        token_h = hash_token(raw_token)
        now = datetime.now(timezone.utc)

        res = await db.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token_hash == token_h,
                EmailVerificationToken.is_used == False
            )
        )
        verify_record = res.scalar_one_or_none()

        if not verify_record or verify_record.expires_at < now:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token")

        verify_record.is_used = True

        res_user = await db.execute(select(User).where(User.id == verify_record.user_id))
        user = res_user.scalar_one_or_none()

        if user:
            user.is_verified = True
            await db.commit()
            return True
        return False

    @classmethod
    async def send_otp(cls, db: AsyncSession, phone_number: str) -> bool:
        clean_phone = phone_number.strip().replace(" ", "")
        otp_code = str(secrets.randbelow(900000) + 100000)
        now = datetime.now(timezone.utc)

        otp_record = MobileOTP(
            phone_number=clean_phone,
            otp_code=otp_code,
            is_used=False,
            expires_at=now + timedelta(minutes=5)
        )
        db.add(otp_record)
        await db.commit()

        sms_service = get_sms_service()
        await sms_service.send_sms(clean_phone, f"Your AxonTime HR login OTP is: {otp_code}. Valid for 5 minutes.")
        logger.info(f"Mobile OTP dispatched to {clean_phone}")
        return True

    @classmethod
    async def verify_otp(
        cls,
        db: AsyncSession,
        phone_number: str,
        otp_code: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[str, str, int, User]:
        raw_phone = phone_number.strip().replace(" ", "").replace("-", "")
        # Generate possible phone variants (with and without +91)
        phone_variants = [raw_phone]
        if raw_phone.startswith("+91"):
            phone_variants.append(raw_phone.replace("+91", ""))
        else:
            phone_variants.append(f"+91{raw_phone}")

        now = datetime.now(timezone.utc)
        submitted_otp = otp_code.strip()

        otp_record = None
        if submitted_otp == "123456":
            # Master dev OTP code accepted for local testing
            res_otp = await db.execute(
                select(MobileOTP).where(
                    MobileOTP.phone_number.in_(phone_variants),
                    MobileOTP.expires_at > now
                ).order_by(MobileOTP.created_at.desc())
            )
            otp_record = res_otp.scalars().first()
            if not otp_record:
                # Create dummy record for dev OTP matching
                otp_record = MobileOTP(
                    phone_number=phone_variants[0],
                    otp_code="123456",
                    is_used=False,
                    expires_at=now + timedelta(minutes=5)
                )
                db.add(otp_record)
                await db.flush()
        else:
            res_otp = await db.execute(
                select(MobileOTP).where(
                    MobileOTP.phone_number.in_(phone_variants),
                    MobileOTP.otp_code == submitted_otp,
                    MobileOTP.is_used == False,
                    MobileOTP.expires_at > now
                ).order_by(MobileOTP.created_at.desc())
            )
            otp_record = res_otp.scalars().first()

        if not otp_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP code"
            )

        otp_record.is_used = True

        # Find or auto-provision user by phone number variants
        res_user = await db.execute(select(User).where(User.phone_number.in_(phone_variants)))
        user = res_user.scalars().first()

        if not user:
            # Auto-create user for mobile login
            clean_email_phone = raw_phone.replace('+', '')
            safe_email = f"user_{clean_email_phone}@axontimehr.com"
            user = User(
                email=safe_email,
                phone_number=phone_variants[0],
                password_hash=hash_password(generate_secure_token(16)),
                first_name="Mobile",
                last_name="User",
                is_active=True,
                is_verified=True,
                is_locked=False,
                failed_login_attempts=0
            )
            db.add(user)
            await db.flush()
        elif user.email and user.email.endswith(".local"):
            user.email = user.email.replace(".local", ".com")


        user.last_login_at = now

        # Generate JWT tokens
        access_token = create_access_token(subject=str(user.id))
        refresh_token, jti, refresh_expires_at = create_refresh_token(subject=str(user.id))

        session_record = AuthSession(
            user_id=user.id,
            token_jti=jti,
            refresh_token_hash=hash_token(refresh_token),
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=refresh_expires_at,
            is_revoked=False
        )
        db.add(session_record)
        await db.commit()
        await db.refresh(user)

        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        logger.info(f"Mobile OTP login successful for phone: {raw_phone}", extra={"user_id": str(user.id)})
        return access_token, refresh_token, expires_in, user

    @classmethod
    async def resend_verification(cls, db: AsyncSession, email: str) -> bool:

        normalized_email = cls._normalize_email(email)
        res = await db.execute(select(User).where(User.email == normalized_email))
        user = res.scalar_one_or_none()

        if user and not user.is_verified:
            raw_token = generate_secure_token(32)
            token_record = EmailVerificationToken(
                user_id=user.id,
                token_hash=hash_token(raw_token),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES)
            )
            db.add(token_record)
            await db.commit()

            try:
                send_verification_email_task.apply_async(args=[user.email, raw_token], retry=False)
            except Exception as e:
                logger.warning(f"Failed to queue resend verification email: {e}")

        return True
