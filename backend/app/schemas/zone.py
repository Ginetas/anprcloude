from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ZoneBase(BaseModel):
    name: str
    description: Optional[str] = None


class ZoneCreate(ZoneBase):
    pass


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Zone(ZoneBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
