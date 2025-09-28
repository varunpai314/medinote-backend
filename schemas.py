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
    email: Optional[EmailStr] = None
    pronouns: Optional[str] = None
    background: Optional[str] = None
    medical_history: Optional[str] = None
    family_history: Optional[str] = None
    social_history: Optional[str] = None
    previous_treatment: Optional[str] = None
