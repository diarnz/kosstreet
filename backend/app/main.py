from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.engine import AsyncSessionLocal
from app.seeds.demo import seed_demo_data
from app.storage.factory import get_file_storage
from app.storage.local import migrate_legacy_upload_dirs
from app.storage.supabase import SupabaseStorage, migrate_local_report_images

logger = logging.getLogger(__name__)

UPLOAD_DIR = settings.upload_path


@asynccontextmanager
async def lifespan(app: FastAPI):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    moved = migrate_legacy_upload_dirs(UPLOAD_DIR)
    if moved:
        logger.info("Migrated %s report image(s) into %s", moved, UPLOAD_DIR)

    storage = get_file_storage()
    if isinstance(storage, SupabaseStorage):
        migrated = migrate_local_report_images(storage)
        if migrated:
            logger.info("Uploaded %s local report image(s) to Supabase storage", migrated)
        logger.info("Report images served from Supabase bucket %s", settings.supabase_storage_bucket)

    async with AsyncSessionLocal() as db:
        await seed_demo_data(db)
        await db.commit()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="KoStreet API",
        version="0.1.0",
        description="Backend API for KoStreet civic issue reporting and street audit workflows.",
        lifespan=lifespan,
    )

    cors_kwargs: dict[str, object] = {
        "allow_origins": settings.cors_origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
    if settings.env == "development":
        # Vite may fall back to 5174, 5175, etc. when the default port is taken.
        cors_kwargs["allow_origin_regex"] = r"http://(localhost|127\.0\.0\.1):\d+"

    app.add_middleware(CORSMiddleware, **cors_kwargs)

    app.mount(
        "/uploads",
        StaticFiles(directory=UPLOAD_DIR, check_dir=False),
        name="uploads",
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "kostreet-backend"}

    return app


app = create_app()

