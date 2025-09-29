from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
import uuid
from datetime import datetime

from database import AsyncSessionLocal
from models import Session, Doctor, Patient
from schemas import SessionCreate, SessionUpdate, SessionResponse
from routers.utils import get_current_doctor

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    doctor_id: str = Depends(get_current_doctor)
):
    """Create a new session"""
    async with AsyncSessionLocal() as db:
        try:
            # Verify the doctor owns the patient
            patient_result = await db.execute(
                select(Patient).where(
                    Patient.id == session_data.patient_id,
                    Patient.doctor_id == uuid.UUID(doctor_id)
                )
            )
            patient = patient_result.scalar_one_or_none()
            
            if not patient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found or not accessible"
                )

            # Create session
            new_session = Session(
                id=uuid.uuid4(),
                doctor_id=uuid.UUID(doctor_id),
                patient_id=session_data.patient_id,
                template_id=session_data.template_id,
                session_title=session_data.session_title,
                status=session_data.status or "created",
                date=session_data.date or datetime.now().strftime("%Y-%m-%d"),
                start_time=session_data.start_time
            )

            db.add(new_session)
            await db.commit()
            await db.refresh(new_session)

            return SessionResponse(
                id=str(new_session.id),
                doctor_id=str(new_session.doctor_id),
                patient_id=str(new_session.patient_id),
                template_id=str(new_session.template_id) if new_session.template_id else None,
                session_title=new_session.session_title,
                session_summary=new_session.session_summary,
                transcript_status=new_session.transcript_status,
                transcript=new_session.transcript,
                status=new_session.status,
                date=new_session.date,
                start_time=new_session.start_time,
                end_time=new_session.end_time,
                duration=new_session.duration
            )

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create session: {str(e)}"
            )

@router.get("/doctor/{doctor_id}", response_model=List[SessionResponse])
async def get_doctor_sessions(
    doctor_id: uuid.UUID,
    current_doctor_id: str = Depends(get_current_doctor)
):
    """Get all sessions for a doctor"""
    # Verify the doctor is requesting their own sessions
    if str(doctor_id) != current_doctor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these sessions"
        )

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Session).where(Session.doctor_id == doctor_id)
            )
            sessions = result.scalars().all()

            return [
                SessionResponse(
                    id=str(session.id),
                    doctor_id=str(session.doctor_id),
                    patient_id=str(session.patient_id),
                    template_id=str(session.template_id) if session.template_id else None,
                    session_title=session.session_title,
                    session_summary=session.session_summary,
                    transcript_status=session.transcript_status,
                    transcript=session.transcript,
                    status=session.status,
                    date=session.date,
                    start_time=session.start_time,
                    end_time=session.end_time,
                    duration=session.duration
                )
                for session in sessions
            ]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get sessions: {str(e)}"
            )

@router.get("/patient/{patient_id}", response_model=List[SessionResponse])
async def get_patient_sessions(
    patient_id: uuid.UUID,
    doctor_id: str = Depends(get_current_doctor)
):
    """Get all sessions for a patient"""
    async with AsyncSessionLocal() as db:
        try:
            # Verify the doctor owns the patient
            patient_result = await db.execute(
                select(Patient).where(
                    Patient.id == patient_id,
                    Patient.doctor_id == uuid.UUID(doctor_id)
                )
            )
            patient = patient_result.scalar_one_or_none()
            
            if not patient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Patient not found or not accessible"
                )

            result = await db.execute(
                select(Session).where(Session.patient_id == patient_id)
            )
            sessions = result.scalars().all()

            return [
                SessionResponse(
                    id=str(session.id),
                    doctor_id=str(session.doctor_id),
                    patient_id=str(session.patient_id),
                    template_id=str(session.template_id) if session.template_id else None,
                    session_title=session.session_title,
                    session_summary=session.session_summary,
                    transcript_status=session.transcript_status,
                    transcript=session.transcript,
                    status=session.status,
                    date=session.date,
                    start_time=session.start_time,
                    end_time=session.end_time,
                    duration=session.duration
                )
                for session in sessions
            ]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get patient sessions: {str(e)}"
            )

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: uuid.UUID,
    doctor_id: str = Depends(get_current_doctor)
):
    """Get a specific session by ID"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Session).where(
                    Session.id == session_id,
                    Session.doctor_id == uuid.UUID(doctor_id)
                )
            )
            session = result.scalar_one_or_none()

            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )

            return SessionResponse(
                id=str(session.id),
                doctor_id=str(session.doctor_id),
                patient_id=str(session.patient_id),
                template_id=str(session.template_id) if session.template_id else None,
                session_title=session.session_title,
                session_summary=session.session_summary,
                transcript_status=session.transcript_status,
                transcript=session.transcript,
                status=session.status,
                date=session.date,
                start_time=session.start_time,
                end_time=session.end_time,
                duration=session.duration
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get session: {str(e)}"
            )

@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: uuid.UUID,
    session_data: SessionUpdate,
    doctor_id: str = Depends(get_current_doctor)
):
    """Update a session"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Session).where(
                    Session.id == session_id,
                    Session.doctor_id == uuid.UUID(doctor_id)
                )
            )
            session = result.scalar_one_or_none()

            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )

            # Update only provided fields
            update_data = session_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(session, field, value)

            await db.commit()
            await db.refresh(session)

            return SessionResponse(
                id=str(session.id),
                doctor_id=str(session.doctor_id),
                patient_id=str(session.patient_id),
                template_id=str(session.template_id) if session.template_id else None,
                session_title=session.session_title,
                session_summary=session.session_summary,
                transcript_status=session.transcript_status,
                transcript=session.transcript,
                status=session.status,
                date=session.date,
                start_time=session.start_time,
                end_time=session.end_time,
                duration=session.duration
            )

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update session: {str(e)}"
            )

@router.delete("/{session_id}", status_code=status.HTTP_200_OK)
async def delete_session(
    session_id: uuid.UUID,
    doctor_id: str = Depends(get_current_doctor)
):
    """Delete a session"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Session).where(
                    Session.id == session_id,
                    Session.doctor_id == uuid.UUID(doctor_id)
                )
            )
            session = result.scalar_one_or_none()

            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )

            await db.delete(session)
            await db.commit()

            return {"message": "Session deleted successfully"}

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete session: {str(e)}"
            )