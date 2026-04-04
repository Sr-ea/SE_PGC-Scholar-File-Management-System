import uuid
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_evaluator, get_current_scholar
from app.models.pending_change import PendingChange
from app.models.scholar import Scholar
from app.models.user import User
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

router = APIRouter(prefix="/scholars", tags=["scholars"])


# ── Pydantic schemas ──────────────────────────────────────────────


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    place_of_birth: Optional[str] = None
    sex: Optional[str] = None
    civil_status: Optional[str] = None
    religion: Optional[str] = None
    address: Optional[str] = None
    contact_number: Optional[str] = None
    batch_number: Optional[str] = None
    year_level: Optional[str] = None
    course: Optional[str] = None
    school: Optional[str] = None
    student_type: Optional[str] = None


# ── Scholar reads their own profile ──────────────────────────────


@router.get("/me")
def get_my_profile(db: Session = Depends(get_db), user=Depends(get_current_scholar)):
    scholar = db.query(Scholar).filter(Scholar.user_id == user["sub"]).first()

    if not scholar:
        raise HTTPException(status_code=404, detail="Scholar profile not found")

    return scholar


# ── Scholar submits a profile update for approval ────────────────


@router.post("/me/update")
def submit_profile_update(
    changes: ProfileUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_scholar),
):
    scholar = db.query(Scholar).filter(Scholar.user_id == user["sub"]).first()

    if not scholar:
        raise HTTPException(status_code=404, detail="Scholar profile not found")

    # Check if scholar already has a pending profile change
    existing = (
        db.query(PendingChange)
        .filter(
            PendingChange.scholar_id == scholar.id,
            PendingChange.change_type == "profile",
            PendingChange.status == "pending",
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="You already have a pending profile update. Wait for it to be reviewed first.",
        )

    # Build the payload — only include fields that actually changed
    current = {
        "first_name": scholar.first_name,
        "last_name": scholar.last_name,
        "middle_name": scholar.middle_name,
        "date_of_birth": str(scholar.date_of_birth) if scholar.date_of_birth else None,
        "place_of_birth": scholar.place_of_birth,
        "sex": scholar.sex,
        "civil_status": scholar.civil_status,
        "religion": scholar.religion,
        "address": scholar.address,
        "contact_number": scholar.contact_number,
        "batch_number": scholar.batch_number,
        "year_level": scholar.year_level,
        "course": scholar.course,
        "school": scholar.school,
        "student_type": scholar.student_type,
    }

    updates = changes.model_dump(exclude_none=True)
    diff = {
        k: {"from": current.get(k), "to": v}
        for k, v in updates.items()
        if current.get(k) != v
    }

    if not diff:
        raise HTTPException(status_code=400, detail="No changes detected")

    pending = PendingChange(
        id=uuid.uuid4(),
        scholar_id=scholar.id,
        submitted_by=user["sub"],
        change_type="profile",
        payload=diff,
        status="pending",
    )
    db.add(pending)
    db.commit()

    return {"message": "Profile update submitted for review", "changes": diff}


# ── Evaluator reads any scholar's profile ────────────────────────


@router.get("/{scholar_id}")
def get_scholar(
    scholar_id: uuid.UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_evaluator),
):
    scholar = db.query(Scholar).filter(Scholar.id == scholar_id).first()
    if not scholar:
        raise HTTPException(status_code=404, detail="Scholar not found")
    return scholar


# ── Evaluator searches and filters scholars ──────────────────────


@router.get("/")
def list_scholars(
    batch: Optional[str] = None,
    school: Optional[str] = None,
    course: Optional[str] = None,
    status: Optional[str] = None,
    student_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_evaluator),
):
    query = db.query(Scholar)

    if batch:
        query = query.filter(Scholar.batch_number == batch)
    if school:
        query = query.filter(Scholar.school == school)
    if course:
        query = query.filter(Scholar.course == course)
    if status:
        query = query.filter(Scholar.status == status)
    if student_type:
        query = query.filter(Scholar.student_type == student_type)
    if search:
        query = query.filter(
            func.concat(Scholar.first_name, " ", Scholar.last_name).ilike(f"%{search}%")
        )

    return query.all()


# ── Evaluator directly edits a scholar's profile ─────────────────


@router.patch("/{scholar_id}")
def update_scholar(
    scholar_id: uuid.UUID,
    changes: ProfileUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_evaluator),
):
    scholar = db.query(Scholar).filter(Scholar.id == scholar_id).first()
    if not scholar:
        raise HTTPException(status_code=404, detail="Scholar not found")

    for field, value in changes.model_dump(exclude_none=True).items():
        setattr(scholar, field, value)

    db.commit()
    return {"message": "Scholar profile updated"}
