from fastapi import APIRouter, HTTPException, Depends, Body
from routers.utils import get_current_doctor
from database import AsyncSessionLocal
from models import AudioChunk, ChunkUploadNotification
import uuid
from sqlalchemy.future import select

router = APIRouter(prefix="/v1", tags=["audio"])

@router.post("/notify-chunk-uploaded")
async def notify_chunk_uploaded(
    payload: dict = Body(...),
    token: str = Depends(get_current_doctor)
):
    session_id = payload.get("sessionId")
    gcs_path = payload.get("gcsPath")
    chunk_number = payload.get("chunkNumber")
    is_last = payload.get("isLast")
    total_chunks_client = payload.get("totalChunksClient")
    public_url = payload.get("publicUrl")
    mime_type = payload.get("mimeType")
    selected_template_id = payload.get("selectedTemplateId")
    model = payload.get("model")

    # Validate required fields
    if not all([
        session_id, gcs_path, chunk_number is not None, is_last is not None,
        total_chunks_client is not None, public_url, mime_type, selected_template_id, model
    ]):
        raise HTTPException(status_code=400, detail="Missing required fields.")

    async with AsyncSessionLocal() as session:
        # Insert into audio_chunk table
        audio_chunk = AudioChunk(
            id=uuid.uuid4(),
            session_id=session_id,
            chunk_number=chunk_number,
            gcs_path=gcs_path,
            public_url=public_url,
            mime_type=mime_type
        )
        session.add(audio_chunk)

        # Insert into chunk_upload_notification table
        notification = ChunkUploadNotification(
            id=uuid.uuid4(),
            session_id=session_id,
            chunk_number=chunk_number,
            total_chunks_client=total_chunks_client,
            is_last=is_last,
            selected_template_id=selected_template_id,
            model=model
        )
        session.add(notification)

        await session.commit()
    # Trigger processing pipeline here if needed (async task, etc.)
    return {}
