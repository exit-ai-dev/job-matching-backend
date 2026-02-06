# app/api/endpoints/conversation.py
"""
会話型AIマッチング - エンドポイント
Iizumiロジック移植版 + 企業向け候補者検索
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
from app.models.user import User, UserRole
from app.services.chat_service import ChatService
from app.services.employer_chat_service import EmployerChatService

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
    
    求職者: 求人条件を抽出して最適な求人を提案
    企業: 候補者要件を抽出して最適な候補者を提案
    """
    try:
        # サブスクリプション制限チェック（AIチャット）
        await verify_subscription_limit("ai_chat_limit", db, current_user, increment=True)

        # ユーザーの役割に応じてサービスを切り替え
        if current_user.role == UserRole.EMPLOYER:
            # 企業の場合: 候補者検索サービス
            logger.info(f"[Employer Chat] Processing message for employer: {current_user.id}")
            chat_service = EmployerChatService()
        else:
            # 求職者の場合: 求人検索サービス
            logger.info(f"[Seeker Chat] Processing message for seeker: {current_user.id}")
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
            if current_user.role == UserRole.EMPLOYER:
                # 企業向け: 候補者リスト
                recommendations = [
                    JobRecommendationResponse(
                        id=candidate.get("id", ""),
                        title=candidate.get("job_title", "職種未設定"),
                        company=candidate.get("name", "名前未設定"),  # 候補者名をcompanyフィールドに
                        matchScore=int(candidate.get("matchScore", 0)),
                        matchReasoning=candidate.get("matchReasoning", ""),
                        salaryMin=None,
                        salaryMax=None,
                        location=candidate.get("location", "未設定"),
                        remoteOption=candidate.get("remote_option", "未設定")
                    )
                    for candidate in result.jobs
                ]
            else:
                # 求職者向け: 求人リスト
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
    求職者: 求人検索
    企業: 候補者検索
    """
    try:
        # サブスクリプション制限チェック
        await verify_subscription_limit("ai_chat_limit", db, current_user, increment=True)

        # ユーザーの役割に応じてサービスを切り替え
        if current_user.role == UserRole.EMPLOYER:
            # 企業の場合: 候補者検索サービス
            logger.info(f"[Employer Chat] Starting chat for employer: {current_user.id}")
            chat_service = EmployerChatService()
        else:
            # 求職者の場合: 求人検索サービス
            logger.info(f"[Seeker Chat] Starting chat for seeker: {current_user.id}")
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