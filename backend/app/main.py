from app.routers.auth import router as auth_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Scholar Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # scholar web dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}
