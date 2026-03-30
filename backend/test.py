from dotenv import load_dotenv

load_dotenv()
import uuid

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User

db = SessionLocal()
user = User(
    id=uuid.uuid4(),
    email="evaluator@test.com",
    hashed_password=hash_password("password123"),
    role="evaluator",
)
db.add(user)
db.commit()
print("Evaluator created")
db.close()
