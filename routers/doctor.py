from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models import Doctor
from schemas import DoctorSignup, DoctorLogin
from database import AsyncSessionLocal
from auth import get_password_hash, verify_password, create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["doctor"])

@router.post("/signup")
async def doctor_signup(payload: DoctorSignup):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            Doctor.__table__.select().where(Doctor.email == payload.email)
        )
        if result.scalar():
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_pw = get_password_hash(payload.password)
        doctor = Doctor(
            name=payload.name,
            email=payload.email,
            specialization=payload.specialization,
            password_hash=hashed_pw,
        )
        session.add(doctor)
        await session.commit()
        await session.refresh(doctor)
        token_data = {"sub": doctor.email, "doctor_id": str(doctor.id)}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "doctor_id": str(doctor.id)
        }

@router.post("/login")
async def doctor_login(payload: DoctorLogin):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            Doctor.__table__.select().where(Doctor.email == payload.email)
        )
        doctor_row = result.first()
        if not doctor_row:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        doctor = Doctor(**doctor_row._mapping)
        if not verify_password(payload.password, doctor.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token_data = {"sub": doctor.email, "doctor_id": str(doctor.id)}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "doctor_id": str(doctor.id)
        }
