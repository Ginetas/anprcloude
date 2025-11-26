from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from ..core.database import Base


class Exporter(Base):
    __tablename__ = "exporters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    exporter_type = Column(String, nullable=False)  # "webhook", "rest", "mqtt", etc.
    endpoint_url = Column(String)
    enabled = Column(Boolean, default=True)
    config = Column(JSON)  # Additional configuration (headers, auth, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
