import asyncio
import random
import uuid
from datetime import datetime, timezone, time, date, timedelta
from sqlalchemy import select, and_, text
from app.db.session import AsyncSessionLocal
from app.models.organization import Company
from app.models.employee import Employee
from app.models.user import User
from app.models.attendance import (
    Attendance,
    AttendanceEvent,
    Shift,
    EmployeeShiftAssignment,
    AttendanceStatus,
    AttendanceSource,
    AttendanceEventType,
    ShiftType,
    ShiftStatus
)
from app.services.organization_service import OrganizationService

FIRST_NAMES = ["Aarav", "Aditi", "Rohan", "Priya", "Vikram", "Ananya", "Rahul", "Sneha", "Karan", "Pooja", "Siddharth", "Neha"]
LAST_NAMES = ["Sharma", "Patel", "Verma", "Rao", "Gupta", "Singh", "Joshi", "Nair", "Kulkarni", "Deshmukh"]

async def seed_attendance_data():
    async with AsyncSessionLocal() as db:
        print("[+] Starting Attendance Dummy Data Generation...")

        # Ensure updated_at column exists on attendance_events table
        await db.execute(text("ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();"))
        await db.commit()

        # 1. Get or Create Default Tenant/Company
        tenant = await OrganizationService.get_or_create_default_company(db)
        tenant_id = tenant.id
        print(f"[+] Using Tenant: {tenant.name} ({tenant_id})")

        # 2. Get or Create Default Shift
        shift_res = await db.execute(select(Shift).where(Shift.tenant_id == tenant_id))
        shift = shift_res.scalars().first()
        if not shift:
            shift = Shift(
                tenant_id=tenant_id,
                code="SHIFT-GEN",
                name="General Shift",
                shift_type=ShiftType.FIXED,
                start_time=time(9, 0),
                end_time=time(18, 0),
                grace_period_minutes=15,
                late_threshold_minutes=30,
                early_exit_threshold_minutes=15,
                minimum_work_minutes=480,
                break_duration_minutes=60,
                is_overnight=False,
                status=ShiftStatus.ACTIVE
            )
            db.add(shift)
            await db.commit()
            await db.refresh(shift)
            print(f"[+] Created Default Shift: {shift.name}")
        else:
            print(f"[+] Using Existing Shift: {shift.name}")

        # 3. Get or Create Employees
        emp_res = await db.execute(select(Employee).where(Employee.organization_id == tenant_id))
        employees = list(emp_res.scalars().all())

        if len(employees) < 8:
            num_to_create = 10 - len(employees)
            print(f"[+] Creating {num_to_create} dummy employees...")
            for i in range(num_to_create):
                fn = random.choice(FIRST_NAMES)
                ln = random.choice(LAST_NAMES)
                emp_code = f"EMP-{random.randint(1000, 9999)}"
                email = f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@axontime.local"
                
                emp = Employee(
                    organization_id=tenant_id,
                    user_id=None,
                    employee_id=emp_code,
                    first_name=fn,
                    last_name=ln,
                    display_name=f"{fn} {ln}",
                    email=email,
                    joining_date=date(2024, 1, 15)
                )
                db.add(emp)
            await db.commit()
            emp_res = await db.execute(select(Employee).where(Employee.organization_id == tenant_id))
            employees = list(emp_res.scalars().all())

        print(f"[+] Total Employees available: {len(employees)}")

        # 4. Generate ~100 Attendance Records spanning past 15-20 days
        today = date(2026, 9, 1)
        num_days = 15 # 15 days x ~8 employees = ~120 records
        
        start_date = today - timedelta(days=num_days)
        total_created = 0
        total_events = 0

        for day_offset in range(num_days + 1):
            att_date = start_date + timedelta(days=day_offset)
            is_weekend = att_date.weekday() == 6 # Sunday

            for emp in employees:
                # Check if attendance record already exists for this day
                existing = await db.execute(
                    select(Attendance).where(
                        and_(
                            Attendance.tenant_id == tenant_id,
                            Attendance.employee_id == emp.id,
                            Attendance.attendance_date == att_date
                        )
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                if is_weekend:
                    status = AttendanceStatus.WEEK_OFF
                    first_in = None
                    last_out = None
                    worked_mins = 0
                    late_mins = 0
                    early_mins = 0
                else:
                    # Randomize realistic attendance scenario
                    rand_val = random.random()

                    if rand_val < 0.68: # 68% Present
                        status = AttendanceStatus.PRESENT
                        in_minute = random.randint(-10, 10) # 08:50 AM to 09:10 AM
                        out_minute = random.randint(0, 30) # 18:00 PM to 18:30 PM
                        
                        first_in = datetime.combine(att_date, time(9, 0), tzinfo=timezone.utc) + timedelta(minutes=in_minute)
                        last_out = datetime.combine(att_date, time(18, 0), tzinfo=timezone.utc) + timedelta(minutes=out_minute)
                        
                        gross = int((last_out - first_in).total_seconds() // 60)
                        worked_mins = max(0, gross - 60)
                        late_mins = max(0, in_minute - 15)
                        early_mins = 0

                    elif rand_val < 0.82: # 14% Late
                        status = AttendanceStatus.LATE
                        in_minute = random.randint(20, 50) # 09:20 AM to 09:50 AM
                        first_in = datetime.combine(att_date, time(9, 0), tzinfo=timezone.utc) + timedelta(minutes=in_minute)
                        last_out = datetime.combine(att_date, time(18, 0), tzinfo=timezone.utc) + timedelta(minutes=random.randint(0, 15))
                        
                        gross = int((last_out - first_in).total_seconds() // 60)
                        worked_mins = max(0, gross - 60)
                        late_mins = in_minute
                        early_mins = 0

                    elif rand_val < 0.90: # 8% Early Exit
                        status = AttendanceStatus.EARLY_EXIT
                        first_in = datetime.combine(att_date, time(8, 55), tzinfo=timezone.utc)
                        last_out = datetime.combine(att_date, time(16, 30), tzinfo=timezone.utc) # Left 1.5 hrs early
                        
                        gross = int((last_out - first_in).total_seconds() // 60)
                        worked_mins = max(0, gross - 60)
                        late_mins = 0
                        early_mins = 90

                    elif rand_val < 0.95: # 5% Work From Home
                        status = AttendanceStatus.WORK_FROM_HOME
                        first_in = datetime.combine(att_date, time(9, 0), tzinfo=timezone.utc)
                        last_out = datetime.combine(att_date, time(18, 0), tzinfo=timezone.utc)
                        worked_mins = 480
                        late_mins = 0
                        early_mins = 0

                    else: # 5% On Leave / Absent
                        status = AttendanceStatus.ON_LEAVE
                        first_in = None
                        last_out = None
                        worked_mins = 0
                        late_mins = 0
                        early_mins = 0

                att = Attendance(
                    tenant_id=tenant_id,
                    employee_id=emp.id,
                    shift_id=shift.id if status != AttendanceStatus.WEEK_OFF else None,
                    attendance_date=att_date,
                    status=status,
                    first_check_in=first_in,
                    last_check_out=last_out,
                    worked_minutes=worked_mins,
                    total_work_minutes=worked_mins,
                    total_break_minutes=60 if first_in else 0,
                    late_minutes=late_mins,
                    early_exit_minutes=early_mins,
                    attendance_source=AttendanceSource.WEB,
                    remarks=f"Seeded dummy record ({status.value})"
                )
                db.add(att)
                await db.flush()
                total_created += 1

                # Create raw events for check-in and check-out
                if first_in:
                    evt_in = AttendanceEvent(
                        tenant_id=tenant_id,
                        employee_id=emp.id,
                        attendance_id=att.id,
                        event_type=AttendanceEventType.CHECK_IN,
                        event_time=first_in,
                        source=AttendanceSource.WEB,
                        device_reference="Chrome (Windows 11)",
                        location_reference="HQ Main Office Gate",
                        remarks="Check-in event"
                    )
                    db.add(evt_in)
                    total_events += 1

                if last_out:
                    evt_out = AttendanceEvent(
                        tenant_id=tenant_id,
                        employee_id=emp.id,
                        attendance_id=att.id,
                        event_type=AttendanceEventType.CHECK_OUT,
                        event_time=last_out,
                        source=AttendanceSource.WEB,
                        device_reference="Chrome (Windows 11)",
                        location_reference="HQ Main Office Gate",
                        remarks="Check-out event"
                    )
                    db.add(evt_out)
                    total_events += 1

        await db.commit()
        print(f"[SUCCESS] Successfully seeded {total_created} Attendance records!")
        print(f"[SUCCESS] Created {total_events} Raw Punch Events!")

if __name__ == "__main__":
    asyncio.run(seed_attendance_data())
