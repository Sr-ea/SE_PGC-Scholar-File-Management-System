from app.core.database import get_db
from app.core.security import create_token, verify_password
from app.models.user import User
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])


# --- Evaluator login (username + password) ---
@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.role != "evaluator":
        raise HTTPException(status_code=403, detail="Evaluators only")
    token = create_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


# --- Scholar login (Google OAuth) ---
class GoogleTokenRequest(BaseModel):
    token: str


@router.post("/google")
def google_login(body: GoogleTokenRequest, db: Session = Depends(get_db)):
    import os

    from google.auth.transport import requests as grequests
    from google.oauth2 import id_token

    try:
        info = id_token.verify_oauth2_token(
            body.token, grequests.Request(), os.getenv("GOOGLE_CLIENT_ID")
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    email = info.get("email")
    user = db.query(User).filter(User.email == email).first()
    if not user or user.role != "scholar":
        raise HTTPException(status_code=403, detail="Not a registered scholar")

    token = create_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
