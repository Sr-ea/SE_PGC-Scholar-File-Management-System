import app.models
from app.routers.academic_records import router as academic_records_router
from app.routers.auth import router as auth_router
from app.routers.documents import router as documents_router
from app.routers.pending_changes import router as pending_changes_router
from app.routers.scholars import router as scholars_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="Scholar Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # scholar web dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(auth_router)
app.include_router(scholars_router)
app.include_router(academic_records_router)
app.include_router(pending_changes_router)


@app.get("/health")
def health():
    return {"status": "ok"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title="Scholar Management System",
        version="1.0.0",
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
