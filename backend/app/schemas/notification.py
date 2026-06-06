from datetime import datetime
from typing import Literal

from pydantic import BaseModel

NotificationScope = Literal["dashboard", "audit", "all"]


class NotificationRead(BaseModel):
    id: str
    title: str
    description: str
    created_at: datetime
    scope: Literal["dashboard", "audit"]
    kind: str
    target_id: str | None = None
