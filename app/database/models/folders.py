from sqlalchemy import Column, Integer, String, CHAR, DateTime, Index, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base
from datetime import datetime



class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(500), unique=True, nullable=False)  # folder path
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    scanner_id = Column(Integer, nullable=False) 
    table_name = Column(String(100), nullable=False)
    
    processed_files = relationship("ProcessedFile", back_populates="folder", cascade="all, delete")
