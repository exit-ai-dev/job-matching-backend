# app/services/subscription_service.py
"""
サブスクリプション管理サービス
"""
import logging
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import uuid

from sqlalchemy.orm import Session

from app.models.subscription import Subscription, SubscriptionStatus
from app.models.subscription_plan import SubscriptionPlan, PlanTier
from app.models.usage_tracking import UsageTracking
from app.models.payment_history import PaymentHistory, PaymentStatus
from app.models.user import User, UserRole
from app.services.gmo_service import get_gmo_service, GMOPaymentError

logger = logging.getLogger(__name__)


# プランごとの機能制限定義
PLAN_LIMITS = {
    # 求職者向け
    PlanTier.SEEKER_FREE: {
        "ai_chat_limit": 0,  # フリープランはAIチャット利用不可
        "application_limit": 5,
    },
    PlanTier.SEEKER_STANDARD: {
        "ai_chat_limit": 20,
        "application_limit": 30,
    },
    PlanTier.SEEKER_PREMIUM: {
        "ai_chat_limit": -1,  # 無制限
        "application_limit": -1,
    },
    # 企業向け
    PlanTier.EMPLOYER_FREE: {
        "scout_limit": 3,
        "job_posting_limit": 1,
        "candidate_view_limit": 5,
    },
    PlanTier.EMPLOYER_STARTER: {
        "scout_limit": 15,
        "job_posting_limit": 3,
        "candidate_view_limit": 30,
    },
    PlanTier.EMPLOYER_BUSINESS: {
        "scout_limit": 50,
        "job_posting_limit": 10,
        "candidate_view_limit": 100,
    },
}


class SubscriptionService:
    """サブスクリプション管理サービス"""

    def __init__(self, db: Session):
        self.db = db
        self.gmo_service = get_gmo_service()

    def get_plans_for_role(self, role: UserRole) -> List[SubscriptionPlan]:
        """ロールに応じたプラン一覧を取得"""
        return self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.user_role == role,
            SubscriptionPlan.is_active == True
        ).order_by(SubscriptionPlan.display_order).all()

    def get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        """ユーザーの現在のサブスクリプションを取得"""
        return self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status.in_([
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.TRIALING,
                SubscriptionStatus.CANCELED  # 期間終了まで有効
            ])
        ).order_by(Subscription.created_at.desc()).first()

    def get_current_usage(self, user_id: str) -> Optional[UsageTracking]:
        """現在の使用量を取得"""
        now = datetime.utcnow()
        return self.db.query(UsageTracking).filter(
            UsageTracking.user_id == user_id,
            UsageTracking.period_start <= now,
            UsageTracking.period_end > now
        ).first()

    def get_or_create_usage(self, user_id: str) -> UsageTracking:
        """使用量レコードを取得または作成"""
        usage = self.get_current_usage(user_id)

        if usage is None:
            # 新しい期間の使用量レコードを作成
            now = datetime.utcnow()
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = period_start + relativedelta(months=1)

            usage = UsageTracking(
                id=str(uuid.uuid4()),
                user_id=user_id,
                period_start=period_start,
                period_end=period_end,
            )
            self.db.add(usage)
            self.db.commit()
            self.db.refresh(usage)

        return usage

    def get_user_limits(self, user_id: str) -> Dict[str, int]:
        """ユーザーの機能制限を取得"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}

        # サブスクリプションから現在のプランを取得
        subscription = self.get_user_subscription(user_id)

        if subscription and subscription.plan:
            tier_value = subscription.plan.tier
            # DBがVARCHAR（文字列）の場合はEnumに変換
            if isinstance(tier_value, str):
                try:
                    plan_tier = PlanTier(tier_value)
                except ValueError:
                    plan_tier = PlanTier.SEEKER_FREE if user.role == UserRole.SEEKER else PlanTier.EMPLOYER_FREE
            else:
                plan_tier = tier_value
        else:
            # サブスクリプションがない場合はフリープラン
            if user.role == UserRole.SEEKER:
                plan_tier = PlanTier.SEEKER_FREE
            else:
                plan_tier = PlanTier.EMPLOYER_FREE

        return PLAN_LIMITS.get(plan_tier, {})

    def check_limit(self, user_id: str, limit_type: str) -> Dict[str, Any]:
        """
        制限をチェック

        Returns:
            {
                "allowed": bool,
                "current": int,
                "limit": int,
                "remaining": int
            }
        """
        limits = self.get_user_limits(user_id)
        limit_value = limits.get(limit_type, 0)

        # 無制限の場合
        if limit_value == -1:
            return {
                "allowed": True,
                "current": 0,
                "limit": -1,
                "remaining": -1,
            }

        usage = self.get_or_create_usage(user_id)

        # 使用量フィールドの対応
        usage_field_map = {
            "ai_chat_limit": "ai_chat_count",
            "application_limit": "application_count",
            "scout_limit": "scout_count",
            "job_posting_limit": "job_posting_count",
            "candidate_view_limit": "candidate_view_count",
        }

        usage_field = usage_field_map.get(limit_type)
        current_count = getattr(usage, usage_field, 0) if usage_field else 0

        return {
            "allowed": current_count < limit_value,
            "current": current_count,
            "limit": limit_value,
            "remaining": max(0, limit_value - current_count),
        }

    def increment_usage(self, user_id: str, usage_type: str) -> bool:
        """
        使用量をインクリメント

        Args:
            user_id: ユーザーID
            usage_type: 使用タイプ（ai_chat, application, scout, job_posting, candidate_view）

        Returns:
            成功したかどうか
        """
        usage = self.get_or_create_usage(user_id)

        field_map = {
            "ai_chat": "ai_chat_count",
            "application": "application_count",
            "scout": "scout_count",
            "job_posting": "job_posting_count",
            "candidate_view": "candidate_view_count",
        }

        field = field_map.get(usage_type)
        if field:
            current_value = getattr(usage, field, 0)
            setattr(usage, field, current_value + 1)
            self.db.commit()
            return True

        return False

    async def create_subscription(
        self,
        user_id: str,
        plan_id: str,
        card_token: Optional[str] = None
    ) -> Subscription:
        """
        サブスクリプションを作成

        Args:
            user_id: ユーザーID
            plan_id: プランID
            card_token: カードトークン（有料プランの場合必須）

        Returns:
            作成されたサブスクリプション
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        plan = self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == plan_id
        ).first()
        if not plan:
            raise ValueError("Plan not found")

        # 既存のアクティブなサブスクリプションをチェック
        existing = self.get_user_subscription(user_id)
        if existing and existing.status == SubscriptionStatus.ACTIVE:
            raise ValueError("User already has an active subscription")

        now = datetime.utcnow()
        period_end = now + relativedelta(months=1)

        # 有料プランの場合はGMO決済
        gmo_subscription_id = None
        if plan.price_jpy > 0:
            if not card_token:
                raise ValueError("Card token is required for paid plans")

            try:
                # GMO会員登録（まだない場合）
                if not user.gmo_member_id:
                    member_id = await self.gmo_service.register_member(user_id)
                    user.gmo_member_id = member_id
                    self.db.commit()

                # カード登録
                await self.gmo_service.register_card(user.gmo_member_id, card_token)

                # 初回決済
                payment_result = await self.gmo_service.create_subscription(
                    user.gmo_member_id,
                    plan.price_jpy
                )

                gmo_subscription_id = payment_result["order_id"]

                # 決済履歴を保存
                payment = PaymentHistory(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    gmo_order_id=payment_result["order_id"],
                    gmo_tran_id=payment_result.get("tran_id"),
                    amount_jpy=plan.price_jpy,
                    status=PaymentStatus.SUCCESS,
                    payment_method="card",
                    description=f"サブスクリプション: {plan.display_name}",
                    paid_at=now,
                )
                self.db.add(payment)

            except GMOPaymentError as e:
                logger.error(f"GMO Payment error: {e}")
                raise ValueError(f"Payment failed: {e.message}")

        # サブスクリプション作成
        subscription = Subscription(
            id=str(uuid.uuid4()),
            user_id=user_id,
            plan_id=plan_id,
            status=SubscriptionStatus.ACTIVE,
            gmo_member_id=user.gmo_member_id,
            gmo_subscription_id=gmo_subscription_id,
            current_period_start=now,
            current_period_end=period_end,
        )
        self.db.add(subscription)

        # ユーザーのサブスクリプション情報を更新
        user.subscription_tier = plan.tier.value
        self.db.commit()
        self.db.refresh(subscription)

        # 決済履歴にサブスクリプションIDを設定
        if gmo_subscription_id:
            payment.subscription_id = subscription.id
            self.db.commit()

        logger.info(f"Subscription created: {subscription.id} for user {user_id}")
        return subscription

    async def cancel_subscription(self, user_id: str) -> Subscription:
        """
        サブスクリプションをキャンセル（期間終了時に停止）

        Args:
            user_id: ユーザーID

        Returns:
            更新されたサブスクリプション
        """
        subscription = self.get_user_subscription(user_id)
        if not subscription:
            raise ValueError("No active subscription found")

        subscription.cancel_at_period_end = True
        subscription.canceled_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(subscription)

        logger.info(f"Subscription canceled: {subscription.id}")
        return subscription

    async def resume_subscription(self, user_id: str) -> Subscription:
        """
        キャンセルしたサブスクリプションを再開

        Args:
            user_id: ユーザーID

        Returns:
            更新されたサブスクリプション
        """
        subscription = self.get_user_subscription(user_id)
        if not subscription:
            raise ValueError("No subscription found")

        if not subscription.cancel_at_period_end:
            raise ValueError("Subscription is not scheduled for cancellation")

        subscription.cancel_at_period_end = False
        subscription.canceled_at = None
        self.db.commit()
        self.db.refresh(subscription)

        logger.info(f"Subscription resumed: {subscription.id}")
        return subscription

    def get_payment_history(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[PaymentHistory]:
        """決済履歴を取得"""
        return self.db.query(PaymentHistory).filter(
            PaymentHistory.user_id == user_id
        ).order_by(PaymentHistory.created_at.desc()).offset(offset).limit(limit).all()

    def process_subscription_renewal(self, subscription_id: str) -> bool:
        """
        サブスクリプション更新処理（バッチ処理用）

        Returns:
            成功したかどうか
        """
        subscription = self.db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()

        if not subscription:
            return False

        # キャンセル予定の場合は停止
        if subscription.cancel_at_period_end:
            subscription.status = SubscriptionStatus.CANCELED
            user = self.db.query(User).filter(User.id == subscription.user_id).first()
            if user:
                # フリープランに戻す
                if user.role == UserRole.SEEKER:
                    user.subscription_tier = PlanTier.SEEKER_FREE.value
                else:
                    user.subscription_tier = PlanTier.EMPLOYER_FREE.value
            self.db.commit()
            return True

        # 期間を更新
        now = datetime.utcnow()
        subscription.current_period_start = now
        subscription.current_period_end = now + relativedelta(months=1)
        self.db.commit()

        return True
