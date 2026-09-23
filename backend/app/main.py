import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

# Configure structured audit logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [AegisScan] %(message)s"
)
logger = logging.getLogger("aegisscan")

from app.core.config import settings
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import hash_password
from app.models.models import User
from app.api.v1.scan import router as scan_router
from app.api.v1.scans import router as scans_router
from app.api.v1.audits import router as audits_router
from app.api.v1.reports import router as reports_router
from app.api.v1.admin import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default Admin account if not present
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.email == settings.ADMIN_DEFAULT_EMAIL)
        res = await db.execute(stmt)
        admin_user = res.scalars().first()
        if not admin_user:
            admin_user = User(
                email=settings.ADMIN_DEFAULT_EMAIL,
                hashed_password=hash_password(settings.ADMIN_DEFAULT_PASSWORD),
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            await db.commit()
            print(f"[AegisScan] Initialized default admin user: {settings.ADMIN_DEFAULT_EMAIL}")
        elif os.getenv("ADMIN_PASSWORD") or os.getenv("ADMIN_DEFAULT_PASSWORD"):
            admin_user.hashed_password = hash_password(settings.ADMIN_DEFAULT_PASSWORD)
            await db.commit()

    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Privacy-First Static File Security Scanning & Website Audit Platform",
    lifespan=lifespan
)

# CORS configuration (supports explicit origins + automatic Vercel preview/production domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Defensive HTTP Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Mount API Routers
app.include_router(scans_router, prefix="/api/scans")
app.include_router(scans_router, prefix=f"{settings.API_V1_STR}/scans")
app.include_router(scan_router, prefix=settings.API_V1_STR)
app.include_router(audits_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/", tags=["System"])
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API. Visit /docs for OpenAPI documentation.",
        "version": settings.PROJECT_VERSION
    }
