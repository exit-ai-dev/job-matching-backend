# app/core/subscription.py
"""
サブスクリプション機能制限チェック
"""
from functools import wraps
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)


class SubscriptionLimitExceeded(HTTPException):
    """使用量制限超過エラー"""
    def __init__(self, limit_type: str, current: int, limit: int):
        limit_name = self._get_limit_name(limit_type)

        # 制限が0の場合（機能自体が利用不可）
        if limit == 0:
            message = f"{limit_name}機能は有料プランでのみ利用可能です。プランをアップグレードしてください。"
        else:
            message = f"月間の{limit_name}上限（{limit}回）に達しました。プランをアップグレードしてください。"

        detail = {
            "error": "subscription_limit_exceeded",
            "limit_type": limit_type,
            "current": current,
            "limit": limit,
            "message": message
        }
        super().__init__(status_code=403, detail=detail)

    @staticmethod
    def _get_limit_name(limit_type: str) -> str:
        names = {
            "ai_chat_limit": "AIチャット",
            "application_limit": "応募",
            "scout_limit": "スカウト",
            "job_posting_limit": "求人掲載",
            "candidate_view_limit": "候補者閲覧",
        }
        return names.get(limit_type, limit_type)


def check_subscription_limit(limit_type: str, auto_increment: bool = True):
    """
    サブスクリプション制限をチェックするデコレータ

    Args:
        limit_type: 制限タイプ（ai_chat_limit, application_limit, scout_limit等）
        auto_increment: チェック後に自動的に使用量をインクリメントするか

    Usage:
        @router.post("/chat")
        @check_subscription_limit("ai_chat_limit")
        async def chat(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 依存性から取得
            db: Session = kwargs.get("db")
            current_user: User = kwargs.get("current_user")

            if not db or not current_user:
                # 依存性が見つからない場合はスキップ
                logger.warning(f"Subscription check skipped: missing dependencies")
                return await func(*args, **kwargs)

            service = SubscriptionService(db)
            result = service.check_limit(current_user.id, limit_type)

            if not result["allowed"]:
                raise SubscriptionLimitExceeded(
                    limit_type=limit_type,
                    current=result["current"],
                    limit=result["limit"],
                )

            # 関数を実行
            response = await func(*args, **kwargs)

            # 成功した場合のみ使用量をインクリメント
            if auto_increment:
                usage_type = limit_type.replace("_limit", "")
                service.increment_usage(current_user.id, usage_type)

            return response

        return wrapper
    return decorator


async def verify_subscription_limit(
    limit_type: str,
    db: Session,
    user: User,
    increment: bool = True
) -> dict:
    """
    サブスクリプション制限を検証

    Args:
        limit_type: 制限タイプ
        db: データベースセッション
        user: ユーザー
        increment: 使用量をインクリメントするか

    Returns:
        制限チェック結果

    Raises:
        SubscriptionLimitExceeded: 制限超過時
    """
    service = SubscriptionService(db)
    result = service.check_limit(user.id, limit_type)

    if not result["allowed"]:
        raise SubscriptionLimitExceeded(
            limit_type=limit_type,
            current=result["current"],
            limit=result["limit"],
        )

    if increment:
        usage_type = limit_type.replace("_limit", "")
        service.increment_usage(user.id, usage_type)

    return result


def get_subscription_checker(limit_type: str, auto_increment: bool = True):
    """
    サブスクリプション制限チェック用の依存性を生成

    Usage:
        @router.post("/chat")
        async def chat(
            ...,
            _limit_check: dict = Depends(get_subscription_checker("ai_chat_limit"))
        ):
            ...
    """
    async def checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> dict:
        return await verify_subscription_limit(
            limit_type=limit_type,
            db=db,
            user=current_user,
            increment=auto_increment
        )

    return checker
