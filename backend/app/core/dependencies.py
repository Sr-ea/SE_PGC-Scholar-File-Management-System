from app.core.security import verify_token
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        return verify_token(token)
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_evaluator(user=Depends(get_current_user)):
    if user.get("role") != "evaluator":
        raise HTTPException(status_code=403, detail="Evaluators only")
    return user


def get_current_scholar(user=Depends(get_current_user)):
    if user.get("role") != "scholar":
        raise HTTPException(status_code=403, detail="Scholars only")
    return user
