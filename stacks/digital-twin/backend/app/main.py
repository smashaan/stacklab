import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select

from .api.auth import router as auth_router
from .api.router import router as api_router
from .database import Base, SessionLocal, engine
from .models import User
from .security import hash_password, validate_security_settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    validate_security_settings()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        username = os.environ.get("ADMIN_USER", "admin")
        user = db.scalar(select(User).where(User.username == username))
        if user is None:
            db.add(
                User(
                    username=username,
                    hashed_password=hash_password(os.environ["ADMIN_PASSWORD"]),
                    is_active=True,
                    is_admin=True,
                )
            )
            db.commit()
    yield


app = FastAPI(
    title="Stacklab Digital Twin API",
    description="Inventory and telemetry API for the Digital twin stack.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    return {"status": "ok"}
