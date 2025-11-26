from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class PlateEvent(Base):
    __tablename__ = "plate_events"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    plate_text = Column(String, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    detection_confidence = Column(Float)
    ocr_confidence = Column(Float)
    bbox = Column(JSON)  # {"x": 100, "y": 200, "width": 300, "height": 100}
    timestamp = Column(DateTime(timezone=True), nullable=False)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    image_path = Column(String)  # Optional: path to saved plate image
    metadata = Column(JSON)  # Additional metadata from edge processing

    # Relationships
    camera = relationship("Camera", back_populates="plate_events")
