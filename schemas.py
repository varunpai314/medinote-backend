import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class DoctorSignup(BaseModel):
    name: str
    email: EmailStr
    specialization: Optional[str] = None
    password: str

class DoctorLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class PatientCreate(BaseModel):
    doctor_id: uuid.UUID
    name: str
    email: EmailStr
    # TODO: Add these fields after running migration_add_dob_gender.sql
    # date_of_birth: Optional[datetime.date] = None
    # gender: str
    pronouns: Optional[str] = None                 # Optional as per frontend
    background: Optional[str] = None
    medical_history: Optional[str] = None
    family_history: Optional[str] = None
    social_history: Optional[str] = None
    previous_treatment: Optional[str] = None

class PatientResponse(BaseModel):
    id: str
    doctor_id: str
    name: str
    email: str
    date_of_birth: Optional[str] = None  # ISO date string
    gender: str
    pronouns: Optional[str] = None
    background: Optional[str] = None
    medical_history: Optional[str] = None
    family_history: Optional[str] = None
    social_history: Optional[str] = None
    previous_treatment: Optional[str] = None
