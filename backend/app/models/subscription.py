# app/models/subscription.py
"""
ユーザーサブスクリプションモデル
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class SubscriptionStatus(str, enum.Enum):
    """サブスクリプションステータス"""
    ACTIVE = "active"  # 有効
    CANCELED = "canceled"  # 解約済み（期間終了まで有効）
    PAST_DUE = "past_due"  # 支払い遅延
    PAUSED = "paused"  # 一時停止
    TRIALING = "trialing"  # トライアル中


class Subscription(Base):
    """サブスクリプションテーブル"""
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    plan_id = Column(String(36), ForeignKey("subscription_plans.id"), nullable=False)

    # ステータス
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)

    # GMOペイメント関連
    gmo_member_id = Column(String(100), nullable=True)  # GMO会員ID
    gmo_subscription_id = Column(String(100), nullable=True, unique=True)  # GMO継続課金ID

    # 期間
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)

    # 解約関連
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)

    # トライアル
    trial_end = Column(DateTime(timezone=True), nullable=True)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション
    user = relationship("User", backref="subscriptions")
    plan = relationship("SubscriptionPlan", backref="subscriptions")

    def __repr__(self):
        return f"<Subscription {self.user_id} - {self.status}>"
