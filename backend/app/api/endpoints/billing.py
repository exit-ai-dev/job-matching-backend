# app/api/endpoints/billing.py
"""
課金・サブスクリプション管理エンドポイント
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import json

from app.core.dependencies import get_db, get_current_user, get_settings_dependency
from app.core.config import Settings
from jose import jwt, JWTError
from app.models.user import User
from app.models.subscription_plan import SubscriptionPlan
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.usage_tracking import UsageTracking
from app.models.payment_history import PaymentHistory
from app.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

router = APIRouter()
optional_security = HTTPBearer(auto_error=False)


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db=Depends(get_db),
    settings: Settings = Depends(get_settings_dependency),
) -> Optional[User]:
    """認証があればユーザーを返し、なければNoneを返す"""
    if not credentials:
        return None

    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if not user_id:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        return None
    return user


# === リクエスト/レスポンスモデル ===

class PlanResponse(BaseModel):
    """プランレスポンス"""
    id: str
    name: str
    display_name: str
    price_jpy: int
    features: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    """サブスクリプションレスポンス"""
    id: str
    plan_id: str
    plan_name: Optional[str] = None
    plan_display_name: Optional[str] = None
    status: str
    current_period_start: str
    current_period_end: str
    cancel_at_period_end: bool

    class Config:
        from_attributes = True


class UsageResponse(BaseModel):
    """使用量レスポンス"""
    period_start: str
    period_end: str
    ai_chat_count: int
    application_count: int
    scout_count: int
    job_posting_count: int
    candidate_view_count: int
    limits: Dict[str, int]

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    """決済履歴レスポンス"""
    id: str
    amount_jpy: int
    status: str
    description: Optional[str] = None
    paid_at: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class SubscribeRequest(BaseModel):
    """サブスクリプション開始リクエスト"""
    plan_id: str
    card_token: Optional[str] = None  # 有料プランの場合必須


class LimitCheckResponse(BaseModel):
    """制限チェックレスポンス"""
    allowed: bool
    current: int
    limit: int
    remaining: int


# === エンドポイント ===

@router.get("/plans", response_model=List[PlanResponse])
async def get_plans(
    current_user: Optional[User] = Depends(get_optional_user),
    db=Depends(get_db)
):
    """
    利用可能なプラン一覧を取得

    ユーザーのロール（求職者/企業）に応じたプランを返します。
    """
    try:
        service = SubscriptionService(db)
        if current_user:
            plans = service.get_plans_for_role(current_user.role)
        else:
            plans = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.is_active == True
            ).order_by(SubscriptionPlan.display_order).all()

        return [
            PlanResponse(
                id=plan.id,
                name=plan.name,
                display_name=plan.display_name,
                price_jpy=plan.price_jpy,
                features=json.loads(plan.features) if plan.features else None,
                description=plan.description,
            )
            for plan in plans
        ]

    except Exception as e:
        logger.error(f"Error getting plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscription", response_model=Optional[SubscriptionResponse])
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    現在のサブスクリプションを取得
    """
    try:
        service = SubscriptionService(db)
        subscription = service.get_user_subscription(current_user.id)

        if not subscription:
            return None

        return SubscriptionResponse(
            id=subscription.id,
            plan_id=subscription.plan_id,
            plan_name=subscription.plan.name if subscription.plan else None,
            plan_display_name=subscription.plan.display_name if subscription.plan else None,
            status=subscription.status.value,
            current_period_start=subscription.current_period_start.isoformat(),
            current_period_end=subscription.current_period_end.isoformat(),
            cancel_at_period_end=subscription.cancel_at_period_end,
        )

    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscribe", response_model=SubscriptionResponse)
async def subscribe(
    request: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    新規サブスクリプションを開始

    有料プランの場合はcard_tokenが必要です。
    """
    try:
        service = SubscriptionService(db)
        subscription = await service.create_subscription(
            user_id=current_user.id,
            plan_id=request.plan_id,
            card_token=request.card_token,
        )

        return SubscriptionResponse(
            id=subscription.id,
            plan_id=subscription.plan_id,
            plan_name=subscription.plan.name if subscription.plan else None,
            plan_display_name=subscription.plan.display_name if subscription.plan else None,
            status=subscription.status.value,
            current_period_start=subscription.current_period_start.isoformat(),
            current_period_end=subscription.current_period_end.isoformat(),
            cancel_at_period_end=subscription.cancel_at_period_end,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    サブスクリプションをキャンセル

    期間終了時に停止します（即時停止ではありません）。
    """
    try:
        service = SubscriptionService(db)
        subscription = await service.cancel_subscription(current_user.id)

        return SubscriptionResponse(
            id=subscription.id,
            plan_id=subscription.plan_id,
            plan_name=subscription.plan.name if subscription.plan else None,
            plan_display_name=subscription.plan.display_name if subscription.plan else None,
            status=subscription.status.value,
            current_period_start=subscription.current_period_start.isoformat(),
            current_period_end=subscription.current_period_end.isoformat(),
            cancel_at_period_end=subscription.cancel_at_period_end,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume", response_model=SubscriptionResponse)
async def resume_subscription(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    キャンセルしたサブスクリプションを再開
    """
    try:
        service = SubscriptionService(db)
        subscription = await service.resume_subscription(current_user.id)

        return SubscriptionResponse(
            id=subscription.id,
            plan_id=subscription.plan_id,
            plan_name=subscription.plan.name if subscription.plan else None,
            plan_display_name=subscription.plan.display_name if subscription.plan else None,
            status=subscription.status.value,
            current_period_start=subscription.current_period_start.isoformat(),
            current_period_end=subscription.current_period_end.isoformat(),
            cancel_at_period_end=subscription.cancel_at_period_end,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error resuming subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    当月の使用量を取得
    """
    try:
        service = SubscriptionService(db)
        usage = service.get_or_create_usage(current_user.id)
        limits = service.get_user_limits(current_user.id)

        return UsageResponse(
            period_start=usage.period_start.isoformat(),
            period_end=usage.period_end.isoformat(),
            ai_chat_count=usage.ai_chat_count,
            application_count=usage.application_count,
            scout_count=usage.scout_count,
            job_posting_count=usage.job_posting_count,
            candidate_view_count=usage.candidate_view_count,
            limits=limits,
        )

    except Exception as e:
        logger.error(f"Error getting usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage/check/{limit_type}", response_model=LimitCheckResponse)
async def check_limit(
    limit_type: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    特定の機能の制限をチェック

    limit_type: ai_chat_limit, application_limit, scout_limit, job_posting_limit, candidate_view_limit
    """
    try:
        # TODO: 一時的にハードコーディングで全ユーザー許可（デバッグ用）
        # 本番では以下のコメントを外してサービスを使用する
        # service = SubscriptionService(db)
        # result = service.check_limit(current_user.id, limit_type)
        # return LimitCheckResponse(**result)

        # 一時的に全員許可
        return LimitCheckResponse(
            allowed=True,
            current=0,
            limit=-1,
            remaining=-1
        )

    except Exception as e:
        logger.error(f"Error checking limit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payments", response_model=List[PaymentResponse])
async def get_payments(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    決済履歴を取得
    """
    try:
        service = SubscriptionService(db)
        payments = service.get_payment_history(current_user.id, limit, offset)

        return [
            PaymentResponse(
                id=payment.id,
                amount_jpy=payment.amount_jpy,
                status=payment.status.value,
                description=payment.description,
                paid_at=payment.paid_at.isoformat() if payment.paid_at else None,
                created_at=payment.created_at.isoformat(),
            )
            for payment in payments
        ]

    except Exception as e:
        logger.error(f"Error getting payments: {e}")
        raise HTTPException(status_code=500, detail=str(e))
