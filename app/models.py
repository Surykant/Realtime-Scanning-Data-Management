from sqlalchemy import Column, Integer, String, CHAR, DateTime, Index, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime



class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(500), unique=True, nullable=False)  # folder path
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    processed_files = relationship("ProcessedFile", back_populates="folder", cascade="all, delete")


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


class Upcs(Base):
    __tablename__ = "upcs"

    Sno = Column(Integer, primary_key=True, autoincrement=True, index=True)
    csvSno = Column(Integer, nullable=False, index=True)

    Leitho = Column(String(45))
    Booklet1 = Column(String(45))
    Subject = Column(String(45), index=True)
    Roll = Column(String(45), index=True)

    Q1 = Column(String(4))
    Q2 = Column(CHAR(1))
    Q3 = Column(CHAR(1))
    Q4 = Column(CHAR(1))
    Q5 = Column(CHAR(1))
    Q6 = Column(CHAR(1))
    Q7 = Column(CHAR(1))
    Q8 = Column(CHAR(1))
    Q9 = Column(CHAR(1))
    Q10 = Column(CHAR(1))
    Q11 = Column(CHAR(1))
    Q12 = Column(CHAR(1))
    Q13 = Column(CHAR(1))
    Q14 = Column(CHAR(1))
    Q15 = Column(CHAR(1))
    Q16 = Column(CHAR(1))
    Q17 = Column(CHAR(1))
    Q18 = Column(CHAR(1))
    Q19 = Column(CHAR(1))
    Q20 = Column(CHAR(1))
    Q21 = Column(CHAR(1))
    Q22 = Column(CHAR(1))
    Q23 = Column(CHAR(1))
    Q24 = Column(CHAR(1))
    Q25 = Column(CHAR(1))
    Q26 = Column(CHAR(1))
    Q27 = Column(CHAR(1))
    Q28 = Column(CHAR(1))
    Q29 = Column(CHAR(1))
    Q30 = Column(CHAR(1))
    Q31 = Column(CHAR(1))
    Q32 = Column(CHAR(1))
    Q33 = Column(CHAR(1))
    Q34 = Column(CHAR(1))
    Q35 = Column(CHAR(1))
    Q36 = Column(CHAR(1))
    Q37 = Column(CHAR(1))
    Q38 = Column(CHAR(1))
    Q39 = Column(CHAR(1))
    Q40 = Column(CHAR(1))
    Q41 = Column(CHAR(1))
    Q42 = Column(CHAR(1))
    Q43 = Column(CHAR(1))
    Q44 = Column(CHAR(1))
    Q45 = Column(CHAR(1))
    Q46 = Column(CHAR(1))
    Q47 = Column(CHAR(1))
    Q48 = Column(CHAR(1))
    Q49 = Column(CHAR(1))
    Q50 = Column(CHAR(1))
    Q51 = Column(CHAR(1))
    Q52 = Column(CHAR(1))
    Q53 = Column(CHAR(1))
    Q54 = Column(CHAR(1))
    Q55 = Column(CHAR(1))
    Q56 = Column(CHAR(1))
    Q57 = Column(CHAR(1))
    Q58 = Column(CHAR(1))
    Q59 = Column(CHAR(1))
    Q60 = Column(CHAR(1))

    entryAt = Column(DateTime, server_default=func.now(), index=True)
    csvPath = Column(String(450))

# Additional composite indexes (optional but useful)
Index("idx_roll_subject", Upcs.Roll, Upcs.Subject)
Index("idx_csv_entry", Upcs.csvSno, Upcs.entryAt)
