# app/models/subscription_plan.py
"""
サブスクリプションプラン定義モデル
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, Enum
from sqlalchemy.sql import func
import enum
from app.db.base import Base
from app.models.user import UserRole


class PlanTier(str, enum.Enum):
    """プラン階層"""
    # 求職者向け
    SEEKER_FREE = "seeker_free"
    SEEKER_STANDARD = "seeker_standard"
    SEEKER_PREMIUM = "seeker_premium"
    # 企業向け
    EMPLOYER_FREE = "employer_free"
    EMPLOYER_STARTER = "employer_starter"
    EMPLOYER_BUSINESS = "employer_business"


class SubscriptionPlan(Base):
    """サブスクリプションプランテーブル"""
    __tablename__ = "subscription_plans"

    id = Column(String(36), primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # 内部名: seeker_free, employer_business等
    display_name = Column(String(100), nullable=False)  # 表示名: フリープラン, ビジネス等
    user_role = Column(Enum(UserRole), nullable=False)  # 対象ユーザーロール
    tier = Column(Enum(PlanTier), nullable=False)  # プラン階層

    # 価格
    price_jpy = Column(Integer, nullable=False, default=0)  # 月額（税込）

    # 機能制限 (JSON)
    # 例: {"ai_chat_limit": 3, "application_limit": 5, "scout_limit": 3, "job_posting_limit": 1}
    features = Column(Text, nullable=True)

    # 説明
    description = Column(Text, nullable=True)

    # 表示順序
    display_order = Column(Integer, default=0)

    # 有効フラグ
    is_active = Column(Boolean, default=True, nullable=False)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<SubscriptionPlan {self.name} ({self.price_jpy}円)>"
