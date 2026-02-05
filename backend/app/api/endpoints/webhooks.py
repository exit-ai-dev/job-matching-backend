# app/api/endpoints/webhooks.py
"""
外部サービスからのWebhook受信エンドポイント
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from app.core.dependencies import get_db
from app.services.gmo_service import get_gmo_service

logger = logging.getLogger(__name__)

router = APIRouter()


class GMOWebhookPayload(BaseModel):
    """GMO Webhookペイロード"""
    OrderID: Optional[str] = None
    Status: Optional[str] = None
    Amount: Optional[str] = None
    Tax: Optional[str] = None
    TranID: Optional[str] = None
    TranDate: Optional[str] = None
    ErrCode: Optional[str] = None
    ErrInfo: Optional[str] = None


@router.post("/gmo/payment-result")
async def gmo_payment_result(request: Request):
    """
    GMOペイメント決済結果通知

    GMOペイメントから決済結果が通知されます。
    """
    try:
        # リクエストボディを取得
        body = await request.body()
        body_str = body.decode("utf-8")

        logger.info(f"GMO Webhook received: {body_str}")

        # パラメータをパース
        params = {}
        for item in body_str.split("&"):
            if "=" in item:
                key, value = item.split("=", 1)
                params[key] = value

        order_id = params.get("OrderID")
        status = params.get("Status")
        err_code = params.get("ErrCode")

        if not order_id:
            logger.warning("GMO Webhook: Missing OrderID")
            return {"status": "error", "message": "Missing OrderID"}

        # エラーチェック
        if err_code:
            logger.error(f"GMO Webhook error: {err_code} - {params.get('ErrInfo')}")
            # TODO: 決済失敗処理（サブスクリプションステータス更新等）
            return {"status": "error", "error_code": err_code}

        # 決済成功処理
        if status == "CAPTURE" or status == "AUTH":
            logger.info(f"GMO Webhook: Payment successful for {order_id}")
            # TODO: 決済成功処理（決済履歴更新等）

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"GMO Webhook processing error: {e}")
        # Webhookはエラーでも200を返すのが一般的
        return {"status": "error", "message": str(e)}


@router.get("/gmo/test")
async def gmo_webhook_test():
    """
    Webhook疎通テスト用エンドポイント
    """
    return {"status": "ok", "message": "GMO Webhook endpoint is working"}
