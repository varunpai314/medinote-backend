from fastapi import APIRouter, HTTPException, Depends, Body
from routers.utils import get_current_doctor
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/v1", tags=["cloud"])

# Init Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET", "medinote-audio")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

@router.post("/get-presigned-url")
async def get_presigned_url(
    payload: dict = Body(...),
    token: str = Depends(get_current_doctor)
):
    session_id = payload.get("sessionId")
    chunk_number = payload.get("chunkNumber")
    mime_type = payload.get("mimeType")

    if not all([session_id, chunk_number, mime_type]):
        raise HTTPException(status_code=400, detail="Missing required fields.")

    ext = mime_type.split("/")[-1]
    supabase_path = f"sessions/{session_id}/chunk_{chunk_number}.{ext}"

    try:
        # Generate signed upload URL (valid 15 minutes)
        signed_url_data = supabase.storage.from_(BUCKET_NAME).create_signed_upload_url(
            supabase_path
        )

        if not signed_url_data:
            raise Exception("Could not generate signed URL")

        return {
            "url": signed_url_data["signedUrl"],
            "supabasePath": supabase_path,
            "publicUrl": supabase.storage.from_(BUCKET_NAME).get_public_url(supabase_path)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
