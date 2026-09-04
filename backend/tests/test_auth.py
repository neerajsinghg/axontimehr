import uuid
import secrets
import os
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings

def get_latest_otp(phone_number: str) -> str:
    db_url = settings.DATABASE_URL
    if "postgresql" in db_url:
        import psycopg2
        conn = psycopg2.connect(
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT
        )
        cur = conn.cursor()
        cur.execute("SELECT otp_code FROM mobile_otps WHERE phone_number = %s ORDER BY created_at DESC LIMIT 1", (phone_number,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else ""
    else:
        import sqlite3
        sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "axontimehr.db")
        conn = sqlite3.connect(sqlite_path)
        cur = conn.cursor()
        cur.execute("SELECT otp_code FROM mobile_otps WHERE phone_number = ? ORDER BY created_at DESC LIMIT 1", (phone_number,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else ""

@pytest.mark.asyncio
async def test_register_and_login_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_email = f"test.user_{uuid.uuid4().hex[:8]}@axontime.com"
        
        # 1. Register User
        reg_payload = {
            "email": unique_email,
            "password": "Password123!",
            "first_name": "Test",
            "last_name": "User"
        }
        res_reg = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code == 201
        data_reg = res_reg.json()
        assert data_reg["email"] == unique_email
        assert data_reg["is_active"] is True

        # 2. Duplicate Registration Rejection
        res_dup = await ac.post("/api/v1/auth/register", json=reg_payload)
        assert res_dup.status_code == 400

        # 3. Login User
        login_payload = {
            "email": unique_email,
            "password": "Password123!"
        }
        res_login = await ac.post("/api/v1/auth/login", json=login_payload)
        assert res_login.status_code == 200
        data_login = res_login.json()
        assert data_login["success"] is True
        access_token = data_login["data"]["access_token"]
        refresh_token = data_login["data"]["refresh_token"]
        assert access_token is not None
        assert refresh_token is not None

        # 4. Fetch Current User via /auth/me
        headers = {"Authorization": f"Bearer {access_token}"}
        res_me = await ac.get("/api/v1/auth/me", headers=headers)
        assert res_me.status_code == 200
        data_me = res_me.json()
        assert data_me["email"] == unique_email

        # 5. Rotate Refresh Token via /auth/refresh
        res_refresh = await ac.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert res_refresh.status_code == 200
        data_ref = res_refresh.json()
        new_refresh_token = data_ref["data"]["refresh_token"]
        assert new_refresh_token != refresh_token

        # 6. Verify Old Revoked Refresh Token Rejection
        res_old_ref = await ac.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert res_old_ref.status_code == 401

        # 7. Logout User
        res_logout = await ac.post("/api/v1/auth/logout", json={"refresh_token": new_refresh_token})
        assert res_logout.status_code == 200

@pytest.mark.asyncio
async def test_mobile_otp_login_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        phone = f"+9198{secrets.randbelow(90000000):08d}"

        # 1. Send Mobile OTP
        res_send = await ac.post("/api/v1/auth/otp/send", json={"phone_number": phone})
        assert res_send.status_code == 200
        assert res_send.json()["success"] is True

        # 2. Verify invalid OTP rejection
        res_invalid = await ac.post("/api/v1/auth/otp/verify", json={"phone_number": phone, "otp_code": "000000"})
        assert res_invalid.status_code == 400

        # 3. Verify valid OTP login & JWT token issuance (using dev master OTP 123456)
        res_verify = await ac.post("/api/v1/auth/otp/verify", json={"phone_number": phone, "otp_code": "123456"})
        assert res_verify.status_code == 200
        data_otp = res_verify.json()
        assert data_otp["success"] is True
        assert data_otp["data"]["access_token"] is not None
        assert data_otp["data"]["user"]["email"] is not None
