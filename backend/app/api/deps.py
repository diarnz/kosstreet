import os

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


async def require_admin(x_admin_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    admin_secret = settings.admin_secret or os.getenv("KOSTREET_ADMIN_SECRET", "")
    if not admin_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin access is not configured",
        )
    if not x_admin_key or x_admin_key != admin_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key",
        )
