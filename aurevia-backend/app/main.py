import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, users, journal, chat
from app.core.config import settings
from app.middleware.error_handler import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware
#from app.api.websocket import router as websocket_router
#from app.cache.redis_client import redis_manager
logging.basicConfig(level=logging.INFO if not settings.debug else logging.DEBUG)

# NOTE: table creation is now handled by Alembic migrations (see alembic/),
# not by Base.metadata.create_all(). Run `alembic upgrade head` after pulling
# new models instead of relying on auto-create.

app = FastAPI(
    title=f"{settings.app_name} API",
    description="Backend API for the Aurevia mental health app.",
    version="0.1.0",
)
@app.on_event("startup")
async def startup_event():
    await redis_manager.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await redis_manager.disconnect()

# Yeh line app define hone ke baad aani chahiye
#app.include_router(websocket_router, prefix="/api/v1")

# --- Middleware ---
# allow_origins: exact matches only (safe with allow_credentials=True).
# allow_origin_regex: optional, lets every Vercel *preview* deployment for
# your project through too (e.g. aurevia-git-feature-x-yourteam.vercel.app)
# without you having to add each preview URL to CORS_ORIGINS by hand.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.cors_origin_regex or None,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(RequestLoggingMiddleware)
register_exception_handlers(app)

# --- Routes ---
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(journal.router)
app.include_router(chat.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "app": settings.app_name}
