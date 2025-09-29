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
    
# GET /fetch-session-by-patient/{patient_id}
@router.get("/fetch-session-by-patient/{patient_id}")
async def fetch_sessions_by_patient(patient_id: str, doctor_id: str = Depends(get_current_doctor)):
    """
    Returns all sessions for a given patientId, only for the authenticated doctor.
    """
    from sqlalchemy.future import select
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Session).where(Session.patient_id == patient_id, Session.doctor_id == doctor_id)
        )
        sessions = [
            {
                "id": str(s.id),
                "date": s.date,
                "session_title": s.session_title,
                "session_summary": s.session_summary,
                "duration": s.duration
            }
            for s in result.scalars()
        ]
        return {"sessions": sessions}


# GET /all-session?userId={userId}

@router.get("/all-session")
async def get_all_sessions(userId: str, token_doctor_id: str = Depends(get_current_doctor)):
    """
    Returns all sessions for a given doctor (userId), with patient details and patientMap.
    """
    if userId != token_doctor_id:
        raise HTTPException(status_code=403, detail="Doctor ID mismatch or unauthorized")
    from sqlalchemy.future import select
    from sqlalchemy.orm import joinedload
    async with AsyncSessionLocal() as session:
        # Join Session and Patient
        result = await session.execute(
            select(Session, Patient)
            .join(Patient, Session.patient_id == Patient.id)
            .where(Session.doctor_id == userId)
        )
        sessions = []
        patient_map = {}
        for s, p in result.all():
            session_obj = {
                "id": str(s.id),
                "user_id": str(s.doctor_id),
                "patient_id": str(p.id),
                "session_title": s.session_title,
                "session_summary": s.session_summary,
                "transcript_status": s.transcript_status,
                "transcript": s.transcript,
                "status": s.status,
                "date": s.date,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "patient_name": p.name,
                "pronouns": p.pronouns,
                "email": p.email,
                # TODO: Add these fields after running migration_add_dob_gender.sql
                # "gender": p.gender,
                # "date_of_birth": p.date_of_birth.isoformat() if p.date_of_birth else None,
                "background": p.background,
                "duration": s.duration,
                "medical_history": p.medical_history,
                "family_history": p.family_history,
                "social_history": p.social_history,
                "previous_treatment": p.previous_treatment,
                "patient_pronouns": p.pronouns,
                "clinical_notes": []  # Placeholder for future notes
            }
            sessions.append(session_obj)
            patient_map[str(p.id)] = {
                "name": p.name,
                "pronouns": p.pronouns,
                # TODO: Add these fields after running migration_add_dob_gender.sql
                # "gender": p.gender,
                # "date_of_birth": p.date_of_birth.isoformat() if p.date_of_birth else None,
                "email": p.email
            }
        return {"sessions": sessions, "patientMap": patient_map}
    
# GET /fetch-default-template-ext?userId={userId}
@router.get("/fetch-default-template-ext")
async def fetch_templates_by_user(userId: str, token_doctor_id: str = Depends(get_current_doctor)):
    """
    Returns all templates for a doctor (userId): both doctor-specific and global default templates.
    """
    if userId != token_doctor_id:
        raise HTTPException(status_code=403, detail="Doctor ID mismatch or unauthorized")
    from sqlalchemy.future import select
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Template).where(
                (Template.doctor_id == userId) | (Template.type == 'default')
            )
        )
        templates = [
            {
                "id": str(t.id),
                "doctor_id": str(t.doctor_id) if t.doctor_id else None,
                "title": t.title,
                "type": t.type
            }
            for t in result.scalars()
        ]
        return {"templates": templates}
    
# POST /upload-session
@router.post("/upload-session")
async def upload_session(
    payload: dict = Body(...),
    token_doctor_id: str = Depends(get_current_doctor)
):
    """
    Create a new session for a patient and doctor.
    """
    # Extract and validate fields
    patient_id = payload.get("patientId")
    doctor_id = payload.get("userId")
    patient_name = payload.get("patientName")  # Not stored in session, for display only
    status = payload.get("status")
    start_time = payload.get("startTime")
    template_id = payload.get("templateId")

    # Validate required fields
    if not all([patient_id, doctor_id, status, start_time, template_id]):
        raise HTTPException(status_code=400, detail="Missing required fields.")
    if doctor_id != token_doctor_id:
        raise HTTPException(status_code=403, detail="Doctor ID mismatch or unauthorized")

    # Validate status
    if status not in ("recording", "completed", "failed"):
        raise HTTPException(status_code=400, detail="Invalid status value.")

    # Create session
    from sqlalchemy.future import select
    async with AsyncSessionLocal() as session:
        new_session = Session(
            id=uuid.uuid4(),
            doctor_id=doctor_id,
            patient_id=patient_id,
            template_id=template_id,
            status=status,
            start_time=start_time,
            # Optional fields
            session_title=None,
            session_summary=None,
            transcript_status=None,
            transcript=None,
            date=None,
            end_time=None,
            duration=None
        )
        session.add(new_session)
        await session.commit()
        await session.refresh(new_session)
        return {"id": str(new_session.id)}