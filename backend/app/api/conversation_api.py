from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from services.chat_service import ChatService

router = APIRouter(prefix="/conversation", tags=["Conversation"])

class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None

class Recommendation(BaseModel):
    id: str
    title: str
    company: str
    matchScore: float  # 0〜100

class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    recommendations: List[Recommendation] = []

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    service = ChatService()

    if not req.conversation_id:
        result = service.start_chat(req.user_id)
    else:
        result = service.process_message(
            user_id=req.user_id,
            user_message=req.message,
            session_id=req.conversation_id
        )

    recommendations = []
    for job in result.jobs or []:
        recommendations.append({
            "id": str(job.job_id),
            "title": job.job_title,
            "company": job.company_name or "非公開",
            # job.match_score is already a 0-100-ish score in this system.
            # The frontend expects 0-100.
            "matchScore": max(0, min(100, int(round(job.match_score or 0)))),
        })

    return {
        "conversation_id": result.session_id,
        "message": result.ai_message,
        "recommendations": recommendations
    }
