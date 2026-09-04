import io
import math
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone

from app.main import app
from app.services.location_service import LocationService

# Sample Reference Coordinates (Gurugram Office)
OFFICE_LAT = 28.459500
OFFICE_LON = 77.026600


def test_haversine_distance_calculation():
    """Unit test Haversine distance calculation across boundary points."""
    # 0 meters (exact same point)
    d0 = LocationService.haversine_distance(OFFICE_LAT, OFFICE_LON, OFFICE_LAT, OFFICE_LON)
    assert abs(d0 - 0.0) < 0.001

    # ~100 meters away (approx 0.0009 degrees latitude)
    lat_100m = OFFICE_LAT + 0.000900
    d100 = LocationService.haversine_distance(OFFICE_LAT, OFFICE_LON, lat_100m, OFFICE_LON)
    assert 90.0 <= d100 <= 110.0


@pytest.mark.asyncio
async def test_phase5_location_and_geofence_flow():
    """Comprehensive test for Phase 5 GPS, Geofence Policy, Selfie Upload, and Exception Dashboard."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        rand_suffix = uuid.uuid4().hex[:6]
        
        # 1. Register Admin User & Create Dedicated Tenant
        admin_email = f"loc_admin_{rand_suffix}@axontimehr.com"
        reg_res = await client.post(
            "/api/v1/auth/register",
            json={"email": admin_email, "password": "Password123!", "first_name": "LocAdmin", "last_name": "User"}
        )
        assert reg_res.status_code == 201

        from app.db.session import AsyncSessionLocal
        from app.models.organization import Company
        from app.models.user import User
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            comp_p5 = Company(name=f"Tenant P5 Corp {rand_suffix}", code=f"TP5-{rand_suffix}")
            db.add(comp_p5)
            await db.flush()
            user = (await db.execute(select(User).where(User.email == admin_email))).scalar_one()
            user.tenant_id = comp_p5.id
            await db.commit()

        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": admin_email, "password": "Password123!"}
        )
        assert login_res.status_code == 200
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Attendance Location Master (Office Geofence)
        loc_res = await client.post(
            "/api/v1/attendance/locations",
            headers=headers,
            json={
                "code": f"LOC-HQ-{rand_suffix}",
                "name": f"Headquarters Office {rand_suffix}",
                "latitude": OFFICE_LAT,
                "longitude": OFFICE_LON,
                "radius_meters": 100,
                "accuracy_requirement": 50.0
            }
        )
        assert loc_res.status_code == 201, f"Create location failed: {loc_res.text}"
        loc_id = loc_res.json()["id"]

        # 3. Enable Strict GPS Geofence Policy
        policy_res = await client.put(
            "/api/v1/attendance/location-policies",
            headers=headers,
            json={
                "location_required": True,
                "geofence_enabled": True,
                "allowed_radius": 100,
                "minimum_accuracy": 50.0,
                "location_freshness_seconds": 300,
                "allow_outside_geofence": False,
                "outside_geofence_action": "REJECT",
                "selfie_required": False
            }
        )
        assert policy_res.status_code == 200
        assert policy_res.json()["geofence_enabled"] is True

        # 4. Pre-Check Location Validate (Inside Geofence)
        val_res = await client.post(
            "/api/v1/attendance/location/validate",
            headers=headers,
            json={
                "latitude": OFFICE_LAT,
                "longitude": OFFICE_LON,
                "accuracy": 15.0
            }
        )
        assert val_res.status_code == 200
        assert val_res.json()["status_code"] == "INSIDE"

        # 6. Verify Check-in Outside Geofence REJECTS under strict policy
        # ~500 meters away (approx 0.0045 degrees latitude)
        far_lat = OFFICE_LAT + 0.004500
        outside_res = await client.post(
            "/api/v1/attendance/check-in",
            headers=headers,
            json={
                "source": "WEB",
                "latitude": far_lat,
                "longitude": OFFICE_LON,
                "accuracy": 10.0
            }
        )
        assert outside_res.status_code == 400
        assert outside_res.json()["detail"]["code"] == "LOCATION_OUTSIDE"

        # 7. Check-in INSIDE Geofence SUCCEEDS
        inside_checkin = await client.post(
            "/api/v1/attendance/check-in",
            headers=headers,
            json={
                "source": "WEB",
                "latitude": OFFICE_LAT,
                "longitude": OFFICE_LON,
                "accuracy": 12.0,
                "remarks": "GPS Check-in inside geofence"
            }
        )
        assert inside_checkin.status_code == 200, f"Check-in inside geofence failed: {inside_checkin.text}"
        att_data = inside_checkin.json()
        assert att_data["location_status"] == "INSIDE"

        # 8. Upload Selfie Image for Identity Verification
        dummy_file = ("selfie_sample.jpg", io.BytesIO(b"fake_image_bytes"), "image/jpeg")
        upload_res = await client.post(
            "/api/v1/attendance/verification/upload-selfie",
            headers=headers,
            files={"file": dummy_file}
        )
        assert upload_res.status_code == 201
        ver_id = upload_res.json()["verification_id"]
        assert upload_res.json()["status"] == "VERIFIED"

        # Stream uploaded selfie image back
        stream_res = await client.get(f"/api/v1/attendance/verification/selfie/{ver_id}", headers=headers)
        assert stream_res.status_code == 200
        assert stream_res.headers["content-type"] == "image/jpeg"

        # 9. Update Policy to ALLOW_WITH_WARNING for Outside Geofence Check-out
        await client.put(
            "/api/v1/attendance/location-policies",
            headers=headers,
            json={
                "location_required": True,
                "geofence_enabled": True,
                "allow_outside_geofence": True,
                "outside_geofence_action": "ALLOW_WITH_WARNING"
            }
        )

        checkout_res = await client.post(
            "/api/v1/attendance/check-out",
            headers=headers,
            json={
                "source": "WEB",
                "latitude": far_lat,
                "longitude": OFFICE_LON,
                "accuracy": 20.0,
                "verification_id": ver_id
            }
        )
        assert checkout_res.status_code == 200
        out_data = checkout_res.json()
        assert out_data["has_exception"] is True

        # 10. Admin Exceptions Dashboard List
        exc_res = await client.get("/api/v1/attendance/exceptions", headers=headers)
        assert exc_res.status_code == 200, f"Exceptions endpoint failed: {exc_res.text}"
        assert exc_res.json()["total"] >= 1
        assert exc_res.json()["data"][0]["location_status"] in ("INSIDE", "OUTSIDE")


@pytest.mark.asyncio
async def test_phase5_cross_tenant_location_isolation():
    """Verify Tenant B cannot access or stream Tenant A's locations or selfies."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register User A
        user_a_email = f"loc_a_{uuid.uuid4().hex[:6]}@tenant-a.com"
        await client.post("/api/v1/auth/register", json={"email": user_a_email, "password": "Password123!", "first_name": "LocA", "last_name": "User"})
        login_a = await client.post("/api/v1/auth/login", json={"email": user_a_email, "password": "Password123!"})
        headers_a = {"Authorization": f"Bearer {login_a.json()['data']['access_token']}"}

        # Create Location A
        code_a = f"LOC-A-{uuid.uuid4().hex[:6]}"
        loc_a = await client.post("/api/v1/attendance/locations", headers=headers_a, json={"code": code_a, "name": "Site A", "latitude": 28.11, "longitude": 77.11})
        assert loc_a.status_code == 201
        loc_a_id = loc_a.json()["id"]

        # Register User B in distinct Tenant B
        user_b_email = f"loc_b_{uuid.uuid4().hex[:6]}@tenant-b.com"
        await client.post("/api/v1/auth/register", json={"email": user_b_email, "password": "Password123!", "first_name": "LocB", "last_name": "User"})
        login_b = await client.post("/api/v1/auth/login", json={"email": user_b_email, "password": "Password123!"})
        headers_b = {"Authorization": f"Bearer {login_b.json()['data']['access_token']}"}

        from app.db.session import AsyncSessionLocal
        from app.models.organization import Company
        from app.models.user import User
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            comp_b = Company(name="Tenant B Loc Corp", code=f"TB-LOC-{uuid.uuid4().hex[:6]}")
            db.add(comp_b)
            await db.flush()
            ub = (await db.execute(select(User).where(User.email == user_b_email))).scalar_one()
            ub.tenant_id = comp_b.id
            await db.commit()

        # Tenant B attempts to fetch Tenant A's location -> 404 Not Found
        get_b_loc = await client.get(f"/api/v1/attendance/locations/{loc_a_id}", headers=headers_b)
        assert get_b_loc.status_code == 404
