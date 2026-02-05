# app/api/endpoints/conversation.py
"""
会話型AIマッチング - エンドポイント
Iizumiロジック移植版
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import logging

from app.core.dependencies import (
    ConversationStorageDep,
    SettingsDep,
    get_db,
    get_current_user
)
from app.core.exceptions import StorageError, NotFoundError
from app.core.subscription import verify_subscription_limit
from app.models.user import User
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Iizumi形式のリクエスト・レスポンスモデル
# =============================================================================

class ChatRequest(BaseModel):
    """チャットリクエスト"""
    user_id: str
    message: str
    conversation_id: Optional[str] = None  # session_idとして使用


class JobRecommendationResponse(BaseModel):
    """求人推薦レスポンス"""
    id: str
    title: str
    company: str
    matchScore: int
    matchReasoning: str
    salaryMin: Optional[int] = None
    salaryMax: Optional[int] = None
    location: str
    remoteOption: str


class ChatResponse(BaseModel):
    """チャットレスポンス（Iizumi形式）"""
    ai_message: str
    recommendations: Optional[List[JobRecommendationResponse]] = None
    conversation_id: str
    turn_number: int
    current_score: float


class ConversationHistoryResponse(BaseModel):
    conversations: List[Dict[str, Any]]


# =============================================================================
# チャットエンドポイント（Iizumiロジック使用）
# =============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    storage: ConversationStorageDep,
    settings: SettingsDep,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    会話型AIマッチング - チャットエンドポイント
    Iizumiロジック移植版

    ユーザーとの会話を通じて求人条件を抽出し、最適な求人を提案します。
    """
    try:
        # サブスクリプション制限チェック（AIチャット）
        # TODO: 一時的にハードコーディングで全ユーザー許可中
        await verify_subscription_limit("ai_chat_limit", db, current_user, increment=True)

        # ChatServiceのインスタンス作成
        chat_service = ChatService()

        # メッセージ処理
        result = chat_service.process_message(
            user_id=request.user_id,
            user_message=request.message,
            session_id=request.conversation_id
        )

        # レスポンス変換
        recommendations = None
        if result.should_show_jobs and result.jobs:
            recommendations = [
                JobRecommendationResponse(
                    id=job.job_id,
                    title=job.job_title,
                    company=job.company_name,
                    matchScore=int(job.match_score),
                    matchReasoning=job.match_reasoning,
                    salaryMin=job.salary_min,
                    salaryMax=job.salary_max,
                    location=job.location,
                    remoteOption=job.remote_option
                )
                for job in result.jobs
            ]

        return ChatResponse(
            ai_message=result.ai_message,
            recommendations=recommendations,
            conversation_id=result.session_id,
            turn_number=result.turn_count,
            current_score=result.current_score
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# チャット開始エンドポイント（新規追加）
# =============================================================================

class StartChatRequest(BaseModel):
    """チャット開始リクエスト"""
    user_id: str


@router.post("/chat/start", response_model=ChatResponse)
async def start_chat(
    request: StartChatRequest,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    チャット開始エンドポイント

    新しいセッションを作成し、初回メッセージを返します。
    """
    try:
        # サブスクリプション制限チェック
        await verify_subscription_limit("ai_chat_limit", db, current_user, increment=True)

        # ChatServiceのインスタンス作成
        chat_service = ChatService()

        # チャット開始
        result = chat_service.start_chat(user_id=request.user_id)

        return ChatResponse(
            ai_message=result.ai_message,
            recommendations=None,
            conversation_id=result.session_id,
            turn_number=result.turn_count,
            current_score=result.current_score
        )

    except Exception as e:
        logger.error(f"Error in start_chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 既存エンドポイント（互換性維持）
# =============================================================================

@router.get("/conversations/{user_id}", response_model=ConversationHistoryResponse)
async def get_conversations(
    user_id: str,
    storage: ConversationStorageDep
):
    """
    ユーザーの会話履歴を取得
    """
    try:
        conversations = storage.get_user_conversations(user_id)
        return ConversationHistoryResponse(conversations=conversations)

    except StorageError as e:
        logger.error(f"Storage error getting conversations: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{user_id}/{conversation_id}")
async def delete_conversation(
    user_id: str,
    conversation_id: str,
    storage: ConversationStorageDep
):
    """
    会話を削除
    """
    try:
        success = storage.delete_conversation(user_id, conversation_id)

        if not success:
            raise NotFoundError("Conversation not found")

        return {"message": "Conversation deleted successfully"}

    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except StorageError as e:
        logger.error(f"Storage error deleting conversation: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
