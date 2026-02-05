# app/services/gmo_service.py
"""
GMOペイメント連携サービス
"""
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class GMOPaymentError(Exception):
    """GMOペイメントエラー"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class GMOPaymentService:
    """GMOペイメント連携サービス"""

    def __init__(self):
        settings = get_settings()
        self.site_id = settings.gmo_site_id
        self.site_pass = settings.gmo_site_pass
        self.shop_id = settings.gmo_shop_id
        self.shop_pass = settings.gmo_shop_pass
        self.api_url = settings.gmo_api_url

    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """GMOレスポンスをパース"""
        result = {}
        for item in response_text.split("&"):
            if "=" in item:
                key, value = item.split("=", 1)
                result[key] = value
        return result

    def _check_error(self, response: Dict[str, str]) -> None:
        """エラーチェック"""
        if "ErrCode" in response:
            error_code = response.get("ErrCode", "")
            error_info = response.get("ErrInfo", "")
            raise GMOPaymentError(
                f"GMO Error: {error_code} - {error_info}",
                error_code=error_code
            )

    async def register_member(self, user_id: str) -> str:
        """
        GMO会員登録

        Args:
            user_id: ユーザーID

        Returns:
            GMO会員ID
        """
        member_id = f"member_{user_id}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/payment/SaveMember.idPass",
                data={
                    "SiteID": self.site_id,
                    "SitePass": self.site_pass,
                    "MemberID": member_id,
                    "MemberName": "",
                }
            )

            result = self._parse_response(response.text)
            self._check_error(result)

            logger.info(f"GMO member registered: {member_id}")
            return member_id

    async def register_card(
        self,
        member_id: str,
        card_token: str,
        default_flag: str = "1"
    ) -> Dict[str, Any]:
        """
        カード登録

        Args:
            member_id: GMO会員ID
            card_token: カードトークン（フロントエンドで取得）
            default_flag: デフォルトカードフラグ

        Returns:
            カード情報
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/payment/SaveCard.idPass",
                data={
                    "SiteID": self.site_id,
                    "SitePass": self.site_pass,
                    "MemberID": member_id,
                    "Token": card_token,
                    "DefaultFlag": default_flag,
                }
            )

            result = self._parse_response(response.text)
            self._check_error(result)

            logger.info(f"Card registered for member: {member_id}")
            return {
                "card_seq": result.get("CardSeq"),
                "card_no": result.get("CardNo"),
                "forward": result.get("Forward"),
            }

    async def create_subscription(
        self,
        member_id: str,
        amount: int,
        tax: int = 0,
        order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        継続課金登録（初回決済）

        Args:
            member_id: GMO会員ID
            amount: 金額（税抜）
            tax: 税額
            order_id: 取引ID（省略時は自動生成）

        Returns:
            継続課金情報
        """
        if order_id is None:
            order_id = f"sub_{uuid.uuid4().hex[:16]}"

        # 1. 取引登録
        async with httpx.AsyncClient() as client:
            entry_response = await client.post(
                f"{self.api_url}/payment/EntryTran.idPass",
                data={
                    "ShopID": self.shop_id,
                    "ShopPass": self.shop_pass,
                    "OrderID": order_id,
                    "JobCd": "CAPTURE",  # 即時売上
                    "Amount": str(amount),
                    "Tax": str(tax),
                }
            )

            entry_result = self._parse_response(entry_response.text)
            self._check_error(entry_result)

            access_id = entry_result.get("AccessID")
            access_pass = entry_result.get("AccessPass")

        # 2. 決済実行（会員のデフォルトカードで決済）
        async with httpx.AsyncClient() as client:
            exec_response = await client.post(
                f"{self.api_url}/payment/ExecTran.idPass",
                data={
                    "AccessID": access_id,
                    "AccessPass": access_pass,
                    "OrderID": order_id,
                    "SiteID": self.site_id,
                    "SitePass": self.site_pass,
                    "MemberID": member_id,
                    "SeqMode": "0",  # デフォルトカード使用
                    "Method": "1",  # 一括払い
                }
            )

            exec_result = self._parse_response(exec_response.text)
            self._check_error(exec_result)

            logger.info(f"Subscription payment created: {order_id}")
            return {
                "order_id": order_id,
                "access_id": access_id,
                "access_pass": access_pass,
                "tran_id": exec_result.get("TranID"),
                "tran_date": exec_result.get("TranDate"),
                "forward": exec_result.get("Forward"),
                "approve": exec_result.get("Approve"),
            }

    async def charge_recurring(
        self,
        member_id: str,
        amount: int,
        tax: int = 0,
        order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        継続課金（月次決済）

        Args:
            member_id: GMO会員ID
            amount: 金額
            tax: 税額
            order_id: 取引ID

        Returns:
            決済結果
        """
        # create_subscriptionと同じ処理（継続課金の場合も同様）
        return await self.create_subscription(member_id, amount, tax, order_id)

    async def cancel_subscription(
        self,
        order_id: str,
        access_id: str,
        access_pass: str
    ) -> Dict[str, Any]:
        """
        取引取消（返金）

        Args:
            order_id: 取引ID
            access_id: アクセスID
            access_pass: アクセスパス

        Returns:
            取消結果
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/payment/AlterTran.idPass",
                data={
                    "ShopID": self.shop_id,
                    "ShopPass": self.shop_pass,
                    "AccessID": access_id,
                    "AccessPass": access_pass,
                    "JobCd": "VOID",  # 取消
                }
            )

            result = self._parse_response(response.text)
            self._check_error(result)

            logger.info(f"Subscription canceled: {order_id}")
            return {
                "order_id": order_id,
                "status": "canceled",
            }

    async def get_member_cards(self, member_id: str) -> list:
        """
        会員のカード一覧取得

        Args:
            member_id: GMO会員ID

        Returns:
            カード情報リスト
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/payment/SearchCard.idPass",
                data={
                    "SiteID": self.site_id,
                    "SitePass": self.site_pass,
                    "MemberID": member_id,
                    "SeqMode": "0",
                }
            )

            result = self._parse_response(response.text)

            # カードが見つからない場合は空リストを返す
            if "ErrCode" in result and "E01" in result.get("ErrCode", ""):
                return []

            self._check_error(result)

            # カード情報をパース
            cards = []
            card_seq = result.get("CardSeq", "").split("|")
            card_no = result.get("CardNo", "").split("|")

            for i, seq in enumerate(card_seq):
                if seq:
                    cards.append({
                        "card_seq": seq,
                        "card_no": card_no[i] if i < len(card_no) else "",
                    })

            return cards

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Webhook署名検証

        Note: GMOのWebhook検証方法に応じて実装
        """
        # GMOペイメントの場合、IPアドレス制限やその他の検証方法を使用
        # 実装はGMOの仕様に従う
        return True


# シングルトンインスタンス
_gmo_service: Optional[GMOPaymentService] = None


def get_gmo_service() -> GMOPaymentService:
    """GMOサービスのシングルトンインスタンスを取得"""
    global _gmo_service
    if _gmo_service is None:
        _gmo_service = GMOPaymentService()
    return _gmo_service
