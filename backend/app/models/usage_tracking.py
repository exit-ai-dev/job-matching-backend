# app/models/usage_tracking.py
"""
使用量追跡モデル
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class UsageTracking(Base):
    """使用量追跡テーブル"""
    __tablename__ = "usage_tracking"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)

    # 期間（月単位）
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # 使用量カウント
    ai_chat_count = Column(Integer, default=0, nullable=False)  # AIチャット回数
    application_count = Column(Integer, default=0, nullable=False)  # 応募回数
    scout_count = Column(Integer, default=0, nullable=False)  # スカウト送信回数
    job_posting_count = Column(Integer, default=0, nullable=False)  # 求人掲載数
    candidate_view_count = Column(Integer, default=0, nullable=False)  # 候補者閲覧回数

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション
    user = relationship("User", backref="usage_records")

    def __repr__(self):
        return f"<UsageTracking {self.user_id} ({self.period_start} - {self.period_end})>"
