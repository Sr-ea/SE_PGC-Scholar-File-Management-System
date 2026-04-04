import uuid
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_evaluator, get_current_scholar
from app.core.storage import delete_file, get_signed_url, upload_file
from app.models.document import Document
from app.models.pending_change import PendingChange
from app.models.scholar import Scholar
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg", "application/pdf"}

ALLOWED_DOC_TYPES = {"COR", "ROG", "explanation_letter", "completion_form", "other"}


# ── Scholar uploads a document ────────────────────────────────────


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    academic_record_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_scholar),
):
    # Validate doc type
    if doc_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid doc type. Must be one of: {', '.join(ALLOWED_DOC_TYPES)}",
        )

    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400, detail="Only JPEG, PNG, and PDF files are allowed"
        )

    # Validate file size — 10MB max
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400, detail="File too large. Maximum size is 10MB"
        )

    scholar = db.query(Scholar).filter(Scholar.user_id == user["sub"]).first()
    if not scholar:
        raise HTTPException(status_code=404, detail="Scholar not found")

    # Build storage path: scholars/{scholar_id}/{doc_type}/{uuid}_{filename}
    file_ext = file.filename.split(".")[-1]
    storage_path = f"scholars/{scholar.id}/{doc_type}/{uuid.uuid4()}_{file.filename}"

    # Upload to Supabase Storage
    try:
        upload_file(storage_path, file_bytes, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    # Parse academic_record_id safely
    parsed_record_id = None
    if academic_record_id and academic_record_id.strip():
        try:
            parsed_record_id = uuid.UUID(academic_record_id.strip())
        except ValueError:
            pass

    # Save record to database
    doc = Document(
        id=uuid.uuid4(),
        scholar_id=scholar.id,
        academic_record_id=parsed_record_id,
        doc_type=doc_type,
        file_name=file.filename,
        storage_path=storage_path,
        file_size=len(file_bytes),
        mime_type=file.content_type,
        is_verified=False,
    )
    db.add(doc)

    # Add to pending changes queue
    pending = PendingChange(
        id=uuid.uuid4(),
        scholar_id=scholar.id,
        submitted_by=user["sub"],
        change_type="documents",
        payload={
            "document_id": str(doc.id),
            "doc_type": doc_type,
            "file_name": file.filename,
            "academic_record_id": academic_record_id,
        },
        status="pending",
    )
    db.add(pending)
    db.commit()

    return {
        "message": "Document uploaded successfully",
        "document_id": str(doc.id),
        "file_name": file.filename,
    }


# ── Scholar views their own documents ────────────────────────────


@router.get("/me")
def get_my_documents(
    academic_record_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_scholar),
):
    scholar = db.query(Scholar).filter(Scholar.user_id == user["sub"]).first()
    if not scholar:
        raise HTTPException(status_code=404, detail="Scholar not found")

    query = db.query(Document).filter(Document.scholar_id == scholar.id)

    if academic_record_id:
        query = query.filter(
            Document.academic_record_id == uuid.UUID(academic_record_id)
        )

    return query.order_by(Document.uploaded_at.desc()).all()


# ── Get a signed URL to view a file ──────────────────────────────
# Both scholar (own files only) and evaluator can access this


@router.get("/{document_id}/view")
def view_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_scholar),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    scholar = db.query(Scholar).filter(Scholar.user_id == user["sub"]).first()

    # Scholar can only view their own files
    if str(doc.scholar_id) != str(scholar.id):
        raise HTTPException(status_code=403, detail="Access denied")

    signed_url = get_signed_url(doc.storage_path, expires_in=120)
    return {"url": signed_url, "expires_in": 120, "file_name": doc.file_name}


# ── Evaluator views any document ─────────────────────────────────


@router.get("/{document_id}/view-evaluator")
def view_document_evaluator(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_evaluator),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    signed_url = get_signed_url(doc.storage_path, expires_in=120)
    return {"url": signed_url, "expires_in": 120, "file_name": doc.file_name}


# ── Evaluator marks a document as verified ───────────────────────


@router.patch("/{document_id}/verify")
def verify_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_evaluator),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.is_verified = True
    db.commit()

    return {"message": "Document marked as verified"}


# ── Evaluator views all documents for a scholar ───────────────────


@router.get("/scholar/{scholar_id}")
def get_scholar_documents(
    scholar_id: uuid.UUID,
    doc_type: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_evaluator),
):
    query = db.query(Document).filter(Document.scholar_id == scholar_id)

    if doc_type:
        query = query.filter(Document.doc_type == doc_type)

    return query.order_by(Document.uploaded_at.desc()).all()
