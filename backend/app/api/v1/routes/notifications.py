from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db
from app.schemas.notification import NotificationRead, NotificationScope
from app.services.notification_service import NotificationService

router = APIRouter()


def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


@router.get("", response_model=list[NotificationRead])
async def list_notifications(
    scope: Annotated[NotificationScope, Query()] = "all",
    limit: Annotated[int, Query(ge=1, le=100)] = 40,
    service: NotificationService = Depends(get_notification_service),
) -> list[NotificationRead]:
    return await service.list_notifications(scope=scope, limit=limit)
