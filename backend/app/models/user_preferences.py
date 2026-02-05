# app/models/user_preferences.py
"""
ユーザー希望条件プロフィールモデル（user_preferences_profile テーブル）
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class UserPreferencesProfile(Base):
    """ユーザー希望条件プロフィール"""
    __tablename__ = "user_preferences_profile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), unique=True, nullable=False)  # usersテーブルと連携
    job_title = Column(String(200))
    location_prefecture = Column(String(50))
    location_city = Column(String(100))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    remote_work_preference = Column(String(50))
    employment_type = Column(String(50))
    industry_preferences = Column(JSON)  # Array stored as JSON for SQLite compatibility
    work_hours_preference = Column(String(100))
    company_size_preference = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
