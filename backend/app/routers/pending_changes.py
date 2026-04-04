import uuid
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_evaluator
from app.models.academic_record import AcademicRecord
from app.models.pending_change import PendingChange
from app.models.scholar import Scholar
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/pending-changes", tags=["pending changes"])


class ReviewDecision(BaseModel):
    status: str  # approved / rejected / more_info
    evaluator_note: Optional[str] = None


# ── List all pending submissions (evaluator queue) ────────────────


@router.get("/")
def list_pending(
    status: Optional[str] = "pending",
    change_type: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_evaluator),
):
    query = db.query(PendingChange)

    if status:
        query = query.filter(PendingChange.status == status)
    if change_type:
        query = query.filter(PendingChange.change_type == change_type)

    # Only show unclaimed OR claimed by this evaluator
    return query.order_by(PendingChange.submitted_at).all()


# ── Claim a submission before reviewing ──────────────────────────


@router.post("/{change_id}/claim")
def claim_submission(
    change_id: uuid.UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_evaluator),
):
    change = db.query(PendingChange).filter(PendingChange.id == change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="Submission not found")

    if change.status != "pending":
        raise HTTPException(status_code=400, detail="Submission is no longer pending")

    # Check if claimed by someone else within 30 minutes
    if change.claimed_by and str(change.claimed_by) != user["sub"]:
        if change.claimed_at:
            age = (datetime.utcnow() - change.claimed_at).total_seconds()
            if age < 1800:
                raise HTTPException(
                    status_code=409,
                    detail="This submission is currently being reviewed by another evaluator",
                )

    change.claimed_by = user["sub"]
    change.claimed_at = datetime.utcnow()
    db.commit()

    return {"claimed": True}


# ── Approve / reject / request more info ─────────────────────────


@router.post("/{change_id}/review")
def review_submission(
    change_id: uuid.UUID,
    decision: ReviewDecision,
    db: Session = Depends(get_db),
    user=Depends(get_current_evaluator),
):
    if decision.status not in ("approved", "rejected", "more_info"):
        raise HTTPException(status_code=400, detail="Invalid status")

    change = db.query(PendingChange).filter(PendingChange.id == change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="Submission not found")

    if change.status != "pending":
        raise HTTPException(status_code=400, detail="Submission already reviewed")

    # If approving a profile change — apply it to the scholar record
    if decision.status == "approved" and change.change_type == "profile":
        scholar = db.query(Scholar).filter(Scholar.id == change.scholar_id).first()
        if scholar:
            for field, diff in change.payload.items():
                setattr(scholar, field, diff["to"])

    # If approving a grades submission — mark it approved
    if decision.status == "approved" and change.change_type == "grades":
        record_id = change.payload.get("academic_record_id")
        if record_id:
            record = (
                db.query(AcademicRecord).filter(AcademicRecord.id == record_id).first()
            )
            if record:
                record.submission_status = "approved"
                record.reviewed_at = datetime.utcnow()
                record.reviewed_by = user["sub"]

    change.status = decision.status
    change.evaluator_note = decision.evaluator_note
    change.reviewed_by = user["sub"]
    change.reviewed_at = datetime.utcnow()
    change.claimed_by = None  # release the claim
    db.commit()

    return {"message": f"Submission {decision.status}"}
