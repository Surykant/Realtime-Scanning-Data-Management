from sqlalchemy import Column, Integer, String, DateTime, func
from app.database.connection import Base

class RevokedToken(Base):
    __tablename__ = "revokedtokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(255), unique=True, nullable=False)  # JWT ID
    created_at = Column(DateTime, server_default=func.now())
