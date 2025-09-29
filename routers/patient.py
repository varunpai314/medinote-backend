from fastapi import Body
import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models import Patient, Session, Template
from schemas import PatientCreate
from database import AsyncSessionLocal
from routers.utils import get_current_doctor

router = APIRouter(prefix="/v1", tags=["patient"])

@router.post("/add-patient-ext")
async def add_patient_ext(
    patient: PatientCreate,
    doctor_id: str = Depends(get_current_doctor)
):
    async with AsyncSessionLocal() as session:
        if str(patient.doctor_id) != doctor_id:
            raise HTTPException(status_code=403, detail="Doctor ID mismatch or unauthorized")
        result = await session.execute(
            Patient.__table__.select().where(Patient.doctor_id == patient.doctor_id, Patient.email == patient.email)
        )
        if result.first():
            raise HTTPException(status_code=400, detail="Patient with this email already exists for this doctor.")
        new_patient = Patient(
            doctor_id=patient.doctor_id,
            name=patient.name,
            email=patient.email,
            # TODO: Add these fields after running migration_add_dob_gender.sql
            # date_of_birth=patient.date_of_birth,
            # gender=patient.gender,
            pronouns=patient.pronouns,
            background=patient.background,
            medical_history=patient.medical_history,
            family_history=patient.family_history,
            social_history=patient.social_history,
            previous_treatment=patient.previous_treatment,
        )
        session.add(new_patient)
        await session.commit()
        await session.refresh(new_patient)
        return {"patient": {
            "id": str(new_patient.id),
            "name": new_patient.name,
            "email": new_patient.email,
            "doctor_id": str(new_patient.doctor_id),
            # TODO: Add these fields after running migration_add_dob_gender.sql
            # "date_of_birth": new_patient.date_of_birth.isoformat() if new_patient.date_of_birth else None,
            # "gender": new_patient.gender,
            "pronouns": new_patient.pronouns,
            "background": new_patient.background,
            "medical_history": new_patient.medical_history,
            "family_history": new_patient.family_history,
            "social_history": new_patient.social_history,
            "previous_treatment": new_patient.previous_treatment
        }}

@router.get("/patients")
async def get_patients_by_doctor(doctor_id: str, token_doctor_id: str = Depends(get_current_doctor)):
    if doctor_id != token_doctor_id:
        raise HTTPException(status_code=403, detail="Doctor ID mismatch or unauthorized")
    async with AsyncSessionLocal() as session:
        from sqlalchemy.future import select
        result = await session.execute(select(Patient).where(Patient.doctor_id == doctor_id))
        patients = [
            {
                "id": str(patient.id),
                "name": patient.name,
                "email": patient.email,
                "doctor_id": str(patient.doctor_id),
                # TODO: Add these fields after running migration_add_dob_gender.sql
                # "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                # "gender": patient.gender,
                "pronouns": patient.pronouns,
                "background": patient.background,
                "medical_history": patient.medical_history,
                "family_history": patient.family_history,
                "social_history": patient.social_history,
                "previous_treatment": patient.previous_treatment
            }
            for patient in result.scalars()
        ]
        return {"patients": patients}

@router.get("/patient-id-by-email")
async def get_patient_id_by_email(email: str, doctor_id: str = Depends(get_current_doctor)):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            Patient.__table__.select().where(Patient.email == email, Patient.doctor_id == doctor_id)
        )
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Patient not found")
        return {"id": str(row.id)}

@router.get("/patient-details/{patient_id}")
async def get_patient_details(patient_id: str, doctor_id: str = Depends(get_current_doctor)):
    from sqlalchemy.future import select
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Patient).where(Patient.id == patient_id, Patient.doctor_id == doctor_id))
        patient = result.scalars().first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return {
            "id": str(patient.id),
            "name": patient.name,
            "email": patient.email,
            "doctor_id": str(patient.doctor_id),
            "pronouns": patient.pronouns,
            "background": patient.background,
            "medical_history": patient.medical_history,
            "family_history": patient.family_history,
            "social_history": patient.social_history,
            "previous_treatment": patient.previous_treatment
        }