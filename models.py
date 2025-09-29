from datetime import date
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base

class Doctor(Base):
    __tablename__ = "doctor"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    specialization = Column(String(100))
    password_hash = Column(Text, nullable=False)

from sqlalchemy import UniqueConstraint

class Patient(Base):
    __tablename__ = "patient"
    __table_args__ = (UniqueConstraint('doctor_id', 'email', name='uix_doctor_email'),)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctor.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    date_of_birth = Column(date, nullable=True)  # Made optional to match frontend
    gender = Column(String(20), nullable=False)   # Required as per frontend
    pronouns = Column(String(20))                 # Optional as per frontend
    background = Column(Text)
    medical_history = Column(Text)
    family_history = Column(Text)
    social_history = Column(Text)
    previous_treatment = Column(Text)


# Template Table
class Template(Base):
    __tablename__ = "template"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctor.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # 'default', 'predefined', 'custom'


# Session Table
class Session(Base):
    __tablename__ = "session"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctor.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patient.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("template.id"), nullable=True)
    session_title = Column(String(150))
    session_summary = Column(Text)
    transcript_status = Column(String(20))
    transcript = Column(Text)
    status = Column(String(20))
    date = Column(String(10))  # Use String for date, or Date if imported
    start_time = Column(String(30))  # Use String for timestamp, or DateTime if imported
    end_time = Column(String(30))
    duration = Column(String(50))  # Use String for interval, or Interval if imported


# Audio Chunk Table
class AudioChunk(Base):
    __tablename__ = "audio_chunk"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("session.id", ondelete="CASCADE"), nullable=False)
    chunk_number = Column(String(10), nullable=False)
    gcs_path = Column(Text, nullable=False)
    public_url = Column(Text)
    mime_type = Column(String(50))
    upload_time = Column(String(30))


# Chunk Upload Notification Table
class ChunkUploadNotification(Base):
    __tablename__ = "chunk_upload_notification"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("session.id", ondelete="CASCADE"), nullable=False)
    chunk_number = Column(String(10), nullable=False)
    total_chunks_client = Column(String(10))
    is_last = Column(String(5))
    selected_template_id = Column(UUID(as_uuid=True), ForeignKey("template.id"), nullable=True)
    model = Column(String(50))
    notified_at = Column(String(30))
