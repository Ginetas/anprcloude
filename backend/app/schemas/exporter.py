from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any


class ExporterBase(BaseModel):
    name: str
    exporter_type: str  # "webhook", "rest", "mqtt", etc.
    endpoint_url: Optional[str] = None
    enabled: bool = True
    config: Optional[Dict[str, Any]] = None


class ExporterCreate(ExporterBase):
    pass


class ExporterUpdate(BaseModel):
    name: Optional[str] = None
    exporter_type: Optional[str] = None
    endpoint_url: Optional[str] = None
    enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class Exporter(ExporterBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
