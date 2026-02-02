# app/models/resume.py
"""
履歴書モデル
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class Resume(Base):
    """履歴書テーブル"""
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # 基本情報
    last_name = Column(String(50), nullable=True)
    first_name = Column(String(50), nullable=True)
    last_name_kana = Column(String(50), nullable=True)
    first_name_kana = Column(String(50), nullable=True)
    birth_date = Column(String(20), nullable=True)
    gender = Column(String(20), nullable=True)

    # 連絡先
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)

    # 学歴・職歴
    education = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    experience_roles = Column(String(500), nullable=True)
    current_salary = Column(String(50), nullable=True)

    # スキル・資格
    skills = Column(Text, nullable=True)
    qualifications = Column(Text, nullable=True)

    # 語学
    native_language = Column(String(50), nullable=True)
    spoken_languages = Column(String(200), nullable=True)
    language_skills = Column(Text, nullable=True)

    # 自己PR・転職理由
    summary = Column(Text, nullable=True)
    career_change_reason = Column(Text, nullable=True)
    future_vision = Column(Text, nullable=True)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Resume {self.user_id}>"
