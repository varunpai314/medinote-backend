from typing import List
from routers.doctor import router as doctor_router
from routers.patient import router as patient_router
from routers.session import router as session_router
from routers.cloud import router as cloud_router
from routers.audio import router as audio_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

app = FastAPI(title="MediNote API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def on_startup():
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(doctor_router)
app.include_router(patient_router)
app.include_router(session_router)
app.include_router(cloud_router)
app.include_router(audio_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
