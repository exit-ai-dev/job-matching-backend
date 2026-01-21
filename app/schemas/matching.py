# app/schemas/matching.py
"""
マッチング関連のPydanticスキーマ
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class SeekerProfileRequest(BaseModel):
    """求職者プロフィール（リクエスト）"""
    name: Optional[str] = None
    skills: List[str] = Field(default_factory=list, description="保有スキル")
    experience: Optional[str] = Field(None, description="職務経歴")
    education: Optional[str] = Field(None, description="学歴")
    location: Optional[str] = Field(None, description="希望勤務地")
    desired_salary_min: Optional[int] = Field(None, description="希望最低年収")
    preferred_employment_types: List[str] = Field(default_factory=list, description="希望雇用形態")


class JobData(BaseModel):
    """求人データ"""
    model_config = {"populate_by_name": True}

    id: str
    employer_id: Optional[str] = Field(None, alias="employerId")
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = Field(None, alias="salaryMin")
    salary_max: Optional[int] = Field(None, alias="salaryMax")
    employment_type: Optional[str] = Field(None, alias="employmentType")
    tags: List[str] = Field(default_factory=list)
    status: str = "published"
    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")


class JobRecommendationResponse(BaseModel):
    """求人レコメンデーション結果"""
    job_id: str
    job: JobData
    match_score: float = Field(..., description="マッチスコア (0-100)")
    match_reasons: List[str] = Field(default_factory=list, description="マッチング理由")


class MatchingRequest(BaseModel):
    """マッチングリクエスト"""
    seeker_profile: SeekerProfileRequest
    available_jobs: List[JobData]
    top_k: int = Field(10, ge=1, le=100, description="返却する求人の最大数")


class MatchingResponse(BaseModel):
    """マッチングレスポンス"""
    recommendations: List[JobRecommendationResponse]
    total_jobs: int = Field(..., description="処理した求人総数")
    filtered_jobs: int = Field(..., description="フィルタリング後の求人数")


class JobAnalysisRequest(BaseModel):
    """求人分析リクエスト"""
    seeker_profile: SeekerProfileRequest
    job: JobData
    match_score: float


class JobAnalysisResponse(BaseModel):
    """求人分析レスポンス"""
    analysis: str = Field(..., description="AI生成の分析テキスト")


class CareerChatMessage(BaseModel):
    """会話メッセージ"""
    role: str = Field(..., description="role: 'user' or 'assistant'")
    content: str = Field(..., description="メッセージ内容")


class CareerChatRequest(BaseModel):
    """キャリア相談リクエスト"""
    message: str = Field(..., description="ユーザーのメッセージ")
    conversation_history: List[CareerChatMessage] = Field(default_factory=list, description="会話履歴")
    seeker_profile: SeekerProfileRequest


class CareerChatResponse(BaseModel):
    """キャリア相談レスポンス"""
    reply: str = Field(..., description="AIの返答")


class MatchingExplanationRequest(BaseModel):
    """マッチング説明リクエスト"""
    seeker_profile: SeekerProfileRequest
    recommendations: List[JobRecommendationResponse]


class MatchingExplanationResponse(BaseModel):
    """マッチング説明レスポンス"""
    explanation: str = Field(..., description="マッチング結果の説明")
