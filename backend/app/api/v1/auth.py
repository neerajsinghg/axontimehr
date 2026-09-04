from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    TokenResponseData,
    RefreshTokenRequest,
    UserResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    SendOTPRequest,
    VerifyOTPRequest,
    VerifyEmailRequest,

    ResendVerificationRequest,
)
from app.services.auth import AuthService

router = APIRouter()

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account"
)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    user = await AuthService.register_user(
        db=db,
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
        company_name=getattr(payload, "company_name", None)
    )
    return UserResponse.model_validate(user)

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user & obtain access/refresh tokens"
)
async def login(
    request: Request,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    request_id = getattr(request.state, "request_id", None)
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    access_token, refresh_token, expires_in, user = await AuthService.login_user(
        db=db,
        email=payload.email,
        password=payload.password,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return TokenResponse(
        success=True,
        message="Login successful",
        data=TokenResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
            user=UserResponse.model_validate(user)
        ),
        request_id=request_id
    )

@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token & obtain new access token"
)
async def refresh(
    request: Request,
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    request_id = getattr(request.state, "request_id", None)
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    access_token, refresh_token, expires_in, user = await AuthService.refresh_tokens(
        db=db,
        refresh_token_str=payload.refresh_token,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return TokenResponse(
        success=True,
        message="Token refreshed successfully",
        data=TokenResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
            user=UserResponse.model_validate(user)
        ),
        request_id=request_id
    )

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Revoke session refresh token & log out"
)
async def logout(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    await AuthService.logout_user(db, payload.refresh_token)
    return {"success": True, "message": "Logged out successfully"}

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile"
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)

@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change user password"
)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    await AuthService.change_password(
        db=db,
        user=current_user,
        current_password=payload.current_password,
        new_password=payload.new_password
    )
    return {"success": True, "message": "Password changed successfully"}

@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Request password reset email"
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    await AuthService.forgot_password(db, payload.email)
    return {
        "success": True,
        "message": "If an account exists with this email, a password reset link has been queued."
    }

@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Reset password using token"
)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    await AuthService.reset_password(db, payload.token, payload.new_password)
    return {"success": True, "message": "Password has been reset successfully"}

@router.post(
    "/verify-email",
    status_code=status.HTTP_200_OK,
    summary="Verify user email address using token"
)
async def verify_email(
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    success = await AuthService.verify_email(db, payload.token)
    if success:
        return {"success": True, "message": "Email address verified successfully"}
    return {"success": False, "message": "Verification failed"}

@router.post(
    "/otp/send",
    status_code=status.HTTP_200_OK,
    summary="Send 6-digit OTP code to mobile number"
)
async def send_otp(
    payload: SendOTPRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    await AuthService.send_otp(db, payload.phone_number)
    return {"success": True, "message": f"OTP code dispatched to {payload.phone_number}"}

@router.post(
    "/otp/verify",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify OTP code & log in via mobile number"
)
async def verify_otp(
    request: Request,
    payload: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    request_id = getattr(request.state, "request_id", None)
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    access_token, refresh_token, expires_in, user = await AuthService.verify_otp(
        db=db,
        phone_number=payload.phone_number,
        otp_code=payload.otp_code,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return TokenResponse(
        success=True,
        message="Mobile OTP login successful",
        data=TokenResponseData(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
            user=UserResponse.model_validate(user)
        ),
        request_id=request_id
    )

@router.post(
    "/resend-verification",

    status_code=status.HTTP_200_OK,
    summary="Resend email verification token"
)
async def resend_verification(
    payload: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    await AuthService.resend_verification(db, payload.email)
    return {
        "success": True,
        "message": "If the account exists and is unverified, a verification email has been sent."
    }
