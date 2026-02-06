# app/api/endpoints/conversation.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import logging
import uuid
from datetime import datetime
import json
from pathlib import Path

from app.core.dependencies import (
    OpenAIServiceDep,
    ConversationStorageDep,
    VectorSearchServiceDep,
    SettingsDep,
    get_db,
    get_current_user
)
from app.core.exceptions import OpenAIError, StorageError, NotFoundError
from app.core.subscription import verify_subscription_limit
from app.models.user import User, UserRole
from app.services.chat_service import ChatService
from app.services.employer_chat_service import EmployerChatService

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None


class JobRecommendationResponse(BaseModel):
    """求人推薦レスポンス"""
    id: str
    title: str
    company: str
    matchScore: int
    matchReasoning: str = ""
    salaryMin: Optional[int] = None
    salaryMax: Optional[int] = None
    location: str = ""
    remoteOption: str = ""


class ChatResponse(BaseModel):
    ai_message: str
    recommendations: Optional[List[JobRecommendationResponse]] = None
    conversation_id: str
    turn_number: int
    current_score: float


class ConversationHistoryResponse(BaseModel):
    conversations: List[Dict[str, Any]]


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


@router.get("/conversations/{user_id}", response_model=ConversationHistoryResponse)
async def get_conversations(
    user_id: str,
    storage: ConversationStorageDep,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ユーザーの会話履歴を取得
    履歴がない場合は動的な初回メッセージを含む新規会話を作成
    """
    try:
        conversations = storage.get_user_conversations(user_id)
        
        # 履歴がない場合、動的な初回メッセージを生成
        if not conversations or len(conversations) == 0:
            try:
                # ユーザーの役割に応じてサービスを切り替え
                if current_user.role == UserRole.EMPLOYER:
                    logger.info(f"[Employer Chat] Starting chat for employer: {current_user.id}")
                    chat_service = EmployerChatService()
                else:
                    logger.info(f"[Seeker Chat] Starting chat for seeker: {current_user.id}")
                    chat_service = ChatService()
                
                result = chat_service.start_chat(user_id=user_id)
                
                # 新規会話オブジェクトを作成
                new_conversation = {
                    "id": result.session_id,
                    "conversation_id": result.session_id,
                    "messages": [{
                        "role": "assistant",
                        "content": result.ai_message,  # 動的メッセージ
                        "turn": "1"
                    }],
                    "createdAt": datetime.now().isoformat(),
                    "updatedAt": datetime.now().isoformat()
                }
                
                conversations = [new_conversation]
                
            except Exception as e:
                logger.error(f"Error generating initial message: {e}")
                # エラーの場合はフォールバック（空の配列を返す）
                conversations = []
        
        return ConversationHistoryResponse(conversations=conversations)

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


class ExtractPreferencesRequest(BaseModel):
    user_id: str
    conversation_id: str


class ExtractPreferencesResponse(BaseModel):
    preferences: Dict[str, Any]
    recommendations: List[Dict[str, Any]]


@router.post("/extract-preferences", response_model=ExtractPreferencesResponse)
async def extract_preferences(
    request: ExtractPreferencesRequest,
    openai_service: OpenAIServiceDep,
    storage: ConversationStorageDep,
    settings: SettingsDep
):
    """
    会話から条件を抽出し、求人を検索
    """
    try:

        # 会話履歴を読み込み
        conversation_data = storage.load_conversation(
            request.user_id,
            request.conversation_id
        )

        if not conversation_data:
            raise NotFoundError("Conversation not found")

        messages = conversation_data.get("messages", [])

        # 条件を抽出
        preferences = openai_service.extract_job_preferences(messages)

        # 求人を検索
        recommendations = await _search_jobs_by_preferences(
            openai_service,
            storage,
            request.user_id,
            preferences
        )

        return ExtractPreferencesResponse(
            preferences=preferences,
            recommendations=recommendations
        )

    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except (OpenAIError, StorageError) as e:
        logger.error(f"Service error extracting preferences: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error extracting preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _extract_and_search_jobs(
    openai_service,
    storage,
    user_id: str,
    messages: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    """会話から条件を抽出して求人を検索"""
    try:
        # 条件を抽出
        preferences = openai_service.extract_job_preferences(messages)

        # 求人を検索
        return await _search_jobs_by_preferences(
            openai_service,
            storage,
            user_id,
            preferences
        )

    except Exception as e:
        logger.error(f"Error in _extract_and_search_jobs: {e}")
        return []


async def _search_jobs_by_preferences(
    openai_service,
    storage,
    user_id: str,
    preferences: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """条件に基づいて求人を検索"""
    try:
        from app.services.vector_search import VectorSearchService

        # 検索クエリのエンベディングを作成
        query_embedding = openai_service.create_search_query_embedding(preferences)

        # すべての求人エンベディングを取得
        job_embeddings = storage.get_all_job_embeddings()

        if not job_embeddings:
            logger.warning("No job embeddings found. Initializing job embeddings...")
            await _initialize_job_embeddings(openai_service, storage)
            job_embeddings = storage.get_all_job_embeddings()

        # 求人データを読み込み
        job_data_list = _load_job_data()

        # ベクトル検索
        vector_search = VectorSearchService()
        results = vector_search.weighted_search(
            query_embedding=query_embedding,
            job_embeddings=job_embeddings,
            job_data_list=job_data_list,
            preferences=preferences,
            top_k=10
        )

        return _to_front_recommendations(results)

    except Exception as e:
        logger.error(f"Error in _search_jobs_by_preferences: {e}")
        return []


async def _initialize_job_embeddings(openai_service, storage):
    """求人エンベディングを初期化"""
    try:
        from app.services.vector_search import VectorSearchService

        job_data_list = _load_job_data()

        for job in job_data_list:
            # エンベディング用テキストを作成
            text = VectorSearchService.create_job_embedding_text(job)

            # エンベディングを生成
            embedding = openai_service.create_embedding(text)

            # 保存
            storage.save_job_embedding(
                job_id=job["id"],
                embedding=embedding,
                text=text
            )

        logger.info(f"Initialized embeddings for {len(job_data_list)} jobs")

    except Exception as e:
        logger.error(f"Error initializing job embeddings: {e}")


def _load_job_data() -> List[Dict[str, Any]]:
    """求人データを読み込み"""
    try:
        data_file = Path("data/jobs.json")

        if not data_file.exists():
            logger.warning("jobs.json not found")
            return []

        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("jobs", [])

    except Exception as e:
        logger.error(f"Error loading job data: {e}")
        return []
    
def _to_front_recommendations(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in results or []:
        out.append({
            "id": str(r.get("id") or r.get("job_id") or ""),
            "title": r.get("title") or r.get("job_title") or "",
            "company": r.get("company") or r.get("company_name") or "非公開",
            "matchScore": int(r.get("matchScore") or r.get("match_score") or 0),
        })
    return [x for x in out if x["id"] and x["title"]]