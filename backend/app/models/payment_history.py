# app/models/payment_history.py
"""
決済履歴モデル
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class PaymentStatus(str, enum.Enum):
    """決済ステータス"""
    PENDING = "pending"  # 処理中
    SUCCESS = "success"  # 成功
    FAILED = "failed"  # 失敗
    REFUNDED = "refunded"  # 返金済み


class PaymentHistory(Base):
    """決済履歴テーブル"""
    __tablename__ = "payment_history"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    subscription_id = Column(String(36), ForeignKey("subscriptions.id"), nullable=True)

    # GMOペイメント関連
    gmo_order_id = Column(String(100), nullable=True, unique=True)  # GMO取引ID
    gmo_tran_id = Column(String(100), nullable=True)  # GMOトランザクションID

    # 金額
    amount_jpy = Column(Integer, nullable=False)  # 金額（税込）
    currency = Column(String(3), default="JPY", nullable=False)

    # ステータス
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)

    # 決済方法
    payment_method = Column(String(50), nullable=True)  # card, konbini等

    # 詳細
    description = Column(String(500), nullable=True)  # 説明（プラン名等）
    error_message = Column(Text, nullable=True)  # エラーメッセージ

    # 領収書
    receipt_url = Column(String(500), nullable=True)

    # 決済日時
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # タイムスタンプ
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # リレーション
    user = relationship("User", backref="payments")
    subscription = relationship("Subscription", backref="payments")

    def __repr__(self):
        return f"<PaymentHistory {self.gmo_order_id} - {self.amount_jpy}円 ({self.status})>"
