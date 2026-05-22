from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kostreet_ai.api.v1.router import api_router
from kostreet_ai.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="KoStreet AI Service",
        version="0.1.0",
        description="Vision classification and street audit pipeline for KoStreet.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["health"])
    def health() -> dict:
        return {
            "status": "ok",
            "service": "kostreet-ai",
            "model": settings.model_name,
        }

    return app


app = create_app()
