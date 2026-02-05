# app/models/company_profile.py
"""
求人情報モデル（company_profile テーブル）
マッチングサービスで使用される求人データ
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, Float, ForeignKey, Time, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class CompanyProfile(Base):
    """求人情報（3層構造）"""
    __tablename__ = "company_profile"

    id = Column(String(36), primary_key=True)
    company_id = Column(String(36), ForeignKey("company_date.company_id", ondelete="CASCADE"))

    # Layer 1: 基本情報（必須）
    job_title = Column(String(200), nullable=False)
    job_description = Column(Text, nullable=False)
    location_prefecture = Column(String(50), nullable=False)
    location_city = Column(String(100))
    salary_min = Column(Integer, nullable=False)
    salary_max = Column(Integer, nullable=False)
    employment_type = Column(String(50), default="正社員")

    # Layer 2: 構造化データ（オプション）
    remote_option = Column(String(50))
    flex_time = Column(Boolean, default=False)
    latest_start_time = Column(Time)
    side_job_allowed = Column(Boolean, default=False)
    team_size = Column(String(50))
    development_method = Column(String(100))
    tech_stack = Column(JSON)
    required_skills = Column(JSON)  # TEXT[] -> JSON for compatibility
    preferred_skills = Column(JSON)
    benefits = Column(JSON)

    # Layer 3: 自由記述（AI抽出対象）
    work_style_details = Column(Text)
    team_culture_details = Column(Text)
    growth_opportunities_details = Column(Text)
    benefits_details = Column(Text)
    office_environment_details = Column(Text)
    project_details = Column(Text)
    company_appeal_text = Column(Text)

    # AI処理済みデータ
    ai_extracted_features = Column(JSON)
    additional_questions = Column(JSON)
    # embedding = Column(VECTOR(1536))  # pgvector extension required

    # メタデータ
    status = Column(String(20), default="active")
    view_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    apply_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
