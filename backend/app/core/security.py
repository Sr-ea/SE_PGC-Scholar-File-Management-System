import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"])


def create_token(data: dict, expires_minutes=480):
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode({**data, "exp": expire}, SECRET_KEY, ALGORITHM)


def verify_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def hash_password(pw):
    return pwd_context.hash(pw)


def verify_password(pw, hashed):
    return pwd_context.verify(pw, hashed)
