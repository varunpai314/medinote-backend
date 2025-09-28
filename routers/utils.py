from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_doctor(token: str = Depends(oauth2_scheme)):
    from auth import SECRET_KEY, ALGORITHM
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        doctor_id: str = payload.get("doctor_id")
        if doctor_id is None:
            raise credentials_exception
        return doctor_id
    except JWTError:
        raise credentials_exception
