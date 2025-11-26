from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rtsp_url = Column(String, nullable=False)
    location = Column(String)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    enabled = Column(Boolean, default=True)
    fps = Column(Integer, default=15)
    resolution_width = Column(Integer, default=1920)
    resolution_height = Column(Integer, default=1080)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    zone = relationship("Zone", back_populates="cameras")
    plate_events = relationship("PlateEvent", back_populates="camera")
