from sqlalchemy import Column, Integer, String, CHAR, DateTime, Index, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base
from datetime import datetime


class ProcessedFile(Base):
    __tablename__ = "processed_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    full_path = Column(String(1024), nullable=False)
    processed = Column(Boolean, default=False, index=True)
    error = Column(String(1024), nullable=True)
    mtime = Column(DateTime, nullable=True)   # file modified time
    created_at = Column(DateTime, server_default=func.now())

    folder_id = Column(Integer, ForeignKey("folders.id", ondelete="CASCADE"), nullable=False, index=True)
    folder = relationship("Folder", back_populates="processed_files")

    __table_args__ = (
        # unique constraint so a file isn't inserted twice
        UniqueConstraint("folder_id", "full_path", name="uq_folder_file"),
    )
