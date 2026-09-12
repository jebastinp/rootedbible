import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.exceptions import AppException
from app.api.v1 import (
    auth,
    home,
    progress,
    community,
    profile,
    admin_members,
    admin_reading_plan,
    admin_settings,
    admin_csv_import,
    admin_reports,
    bible_content,
    bible_engagement,
    quiz,
    notes,
    admin_plan_generator,
    admin_challenges,
    admin_audit_logs,
    admin_community,
    notifications,
    admin_quiz,
    org_admin,
)

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("rooted")

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Rooted - a daily Bible reading tracker for churches.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Defense-in-depth: nginx already gzips /api/ responses in production, but
# this keeps responses compressed for any deployment that talks to uvicorn
# directly (local `uvicorn` runs, tests, a future non-nginx host).
app.add_middleware(GZipMiddleware, minimum_size=512)


# ---------------------------------------------------------------------
# Central exception handling
# ---------------------------------------------------------------------
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.warning(f"AppException on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.message, "details": exc.details},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "An unexpected error occurred. Please try again."},
    )


# ---------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------
API_PREFIX = settings.API_V1_PREFIX

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(home.router, prefix=API_PREFIX)
app.include_router(progress.router, prefix=API_PREFIX)
app.include_router(community.router, prefix=API_PREFIX)
app.include_router(profile.router, prefix=API_PREFIX)
app.include_router(admin_members.router, prefix=API_PREFIX)
app.include_router(admin_reading_plan.router, prefix=API_PREFIX)
app.include_router(admin_settings.router, prefix=API_PREFIX)
app.include_router(admin_csv_import.router, prefix=API_PREFIX)
app.include_router(admin_reports.router, prefix=API_PREFIX)
app.include_router(bible_content.router, prefix=API_PREFIX)
app.include_router(bible_engagement.router, prefix=API_PREFIX)
app.include_router(quiz.router, prefix=API_PREFIX)
app.include_router(notes.router, prefix=API_PREFIX)
app.include_router(admin_plan_generator.router, prefix=API_PREFIX)
app.include_router(admin_challenges.router, prefix=API_PREFIX)
app.include_router(admin_audit_logs.router, prefix=API_PREFIX)
app.include_router(admin_community.router, prefix=API_PREFIX)
app.include_router(notifications.router, prefix=API_PREFIX)
app.include_router(admin_quiz.router, prefix=API_PREFIX)
app.include_router(org_admin.router, prefix=API_PREFIX)


@app.get("/", tags=["Health"])
def root():
    return {"app": settings.APP_NAME, "status": "running", "docs": "/api/docs"}


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
