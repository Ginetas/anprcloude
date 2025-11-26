from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.sql import func
from ..core.database import Base


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    model_type = Column(String, nullable=False)  # "detection" or "ocr"
    file_path = Column(String, nullable=False)
    version = Column(String)
    enabled = Column(Boolean, default=True)
    confidence_threshold = Column(Float, default=0.5)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
