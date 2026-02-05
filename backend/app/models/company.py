# app/models/company.py
"""
企業モデル（company_date テーブル）
"""
from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Company(Base):
    """企業基本情報"""
    __tablename__ = "company_date"

    company_id = Column(String(36), primary_key=True)
    company_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    industry = Column(String(100))
    company_size = Column(String(50))
    founded_year = Column(Integer)
    website_url = Column(String(500))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
