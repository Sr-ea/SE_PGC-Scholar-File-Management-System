import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

BUCKET = "scholar-documents"


def upload_file(path: str, file_bytes: bytes, mime_type: str) -> str:
    supabase.storage.from_(BUCKET).upload(
        path=path, file=file_bytes, file_options={"content-type": mime_type}
    )
    return path


def get_signed_url(path: str, expires_in: int = 60) -> str:
    res = supabase.storage.from_(BUCKET).create_signed_url(path, expires_in)
    return res["signedURL"]


def delete_file(path: str):
    supabase.storage.from_(BUCKET).remove([path])
