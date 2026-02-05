# app/api/endpoints/employer.py
"""
企業向けAPIエンドポイント
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import json

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.job import Job, JobStatus, EmploymentType
from app.models.application import Application, ApplicationStatus
from app.core.dependencies import CurrentUser
from app.services.auth_service import AuthService
from app.services.openai_service import get_openai_service

router = APIRouter()


# === リクエスト/レスポンスモデル ===

class EmployerRegisterRequest(BaseModel):
    """企業登録リクエスト"""
    name: str
    email: str
    password: str
    companyName: str
    industry: Optional[str] = None


class EmployerResponse(BaseModel):
    """企業情報レスポンス"""
    id: str
    name: str
    email: str
    companyName: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    companySize: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    logoUrl: Optional[str] = None
    createdAt: str
    updatedAt: str


class EmployerRegisterResponse(BaseModel):
    """企業登録レスポンス"""
    employer: EmployerResponse
    token: str


class JobCreateRequest(BaseModel):
    """求人作成リクエスト"""
    title: str
    description: str
    location: str
    employmentType: str = Field(..., pattern="^(full-time|part-time|contract|internship)$")
    salaryMin: Optional[int] = None
    salaryMax: Optional[int] = None
    requiredSkills: Optional[List[str]] = None
    preferredSkills: Optional[List[str]] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    status: str = Field(default="draft", pattern="^(draft|published|closed)$")


class JobUpdateRequest(BaseModel):
    """求人更新リクエスト"""
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    employmentType: Optional[str] = None
    salaryMin: Optional[int] = None
    salaryMax: Optional[int] = None
    requiredSkills: Optional[List[str]] = None
    preferredSkills: Optional[List[str]] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    status: Optional[str] = None


class JobResponse(BaseModel):
    """求人レスポンス"""
    id: str
    employerId: str
    title: str
    description: str
    location: str
    employmentType: str
    salaryMin: Optional[int] = None
    salaryMax: Optional[int] = None
    requiredSkills: Optional[List[str]] = None
    preferredSkills: Optional[List[str]] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    status: str
    createdAt: str
    updatedAt: str
    applicationsCount: int = 0


class JobListResponse(BaseModel):
    """求人一覧レスポンス"""
    items: List[JobResponse]
    total: int
    page: int
    totalPages: int


class ChatRequest(BaseModel):
    """AI対話型ヒアリングリクエスト"""
    jobId: Optional[str] = None
    message: str
    sessionId: Optional[str] = None


class ChatMessage(BaseModel):
    """チャットメッセージ"""
    id: str
    role: str
    content: str
    timestamp: str


class ChatResponse(BaseModel):
    """AI対話型ヒアリングレスポンス"""
    sessionId: str
    message: ChatMessage
    isComplete: bool = False


class DashboardStats(BaseModel):
    """ダッシュボード統計"""
    totalJobs: int
    publishedJobs: int
    draftJobs: int
    closedJobs: int
    totalApplications: int
    pendingApplications: int
    interviewApplications: int
    offerApplications: int


# === ヘルパー関数 ===

def job_to_response(job: Job, applications_count: int = 0) -> JobResponse:
    """JobモデルをJobResponseに変換"""
    required_skills = None
    preferred_skills = None

    if job.required_skills:
        try:
            required_skills = json.loads(job.required_skills)
        except:
            pass

    if job.preferred_skills:
        try:
            preferred_skills = json.loads(job.preferred_skills)
        except:
            pass

    return JobResponse(
        id=job.id,
        employerId=job.employer_id,
        title=job.title,
        description=job.description,
        location=job.location,
        employmentType=job.employment_type.value if job.employment_type else "full-time",
        salaryMin=job.salary_min,
        salaryMax=job.salary_max,
        requiredSkills=required_skills,
        preferredSkills=preferred_skills,
        requirements=job.requirements,
        benefits=job.benefits,
        status=job.status.value if job.status else "draft",
        createdAt=job.created_at.isoformat() if job.created_at else "",
        updatedAt=job.updated_at.isoformat() if job.updated_at else "",
        applicationsCount=applications_count
    )


def user_to_employer_response(user: User) -> EmployerResponse:
    """UserモデルをEmployerResponseに変換"""
    return EmployerResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        companyName=user.company_name,
        description=user.company_description,
        industry=user.industry,
        companySize=user.company_size,
        website=user.company_website,
        location=user.company_location,
        logoUrl=user.company_logo_url,
        createdAt=user.created_at.isoformat() if user.created_at else "",
        updatedAt=user.updated_at.isoformat() if user.updated_at else ""
    )


# === エンドポイント ===

@router.post("/register", response_model=EmployerRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_employer(
    request: EmployerRegisterRequest,
    db: Session = Depends(get_db)
):
    """企業登録"""
    auth_service = AuthService(db)

    try:
        user = auth_service.register(
            email=request.email,
            password=request.password,
            name=request.name,
            role="employer",
            company_name=request.companyName,
            industry=request.industry
        )

        token, _ = auth_service.create_access_token(user.id)

        employer = user_to_employer_response(user)

        return EmployerRegisterResponse(employer=employer, token=token)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=EmployerResponse)
async def get_current_employer(current_user: CurrentUser):
    """現在の企業情報を取得"""
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="企業ユーザーのみアクセス可能です"
        )

    return user_to_employer_response(current_user)


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    request: JobCreateRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """求人を作成"""
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="企業ユーザーのみ求人を作成できます"
        )

    job = Job(
        id=str(uuid.uuid4()),
        employer_id=current_user.id,
        title=request.title,
        description=request.description,
        company=current_user.company_name or "",
        location=request.location,
        employment_type=EmploymentType(request.employmentType),
        salary_min=request.salaryMin,
        salary_max=request.salaryMax,
        required_skills=json.dumps(request.requiredSkills) if request.requiredSkills else None,
        preferred_skills=json.dumps(request.preferredSkills) if request.preferredSkills else None,
        requirements=request.requirements,
        benefits=request.benefits,
        status=JobStatus(request.status),
        posted_date=datetime.utcnow() if request.status == "published" else None
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job_to_response(job)


@router.get("/jobs", response_model=JobListResponse)
async def get_employer_jobs(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 10
):
    """自社の求人一覧を取得"""
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="企業ユーザーのみアクセス可能です"
        )

    query = db.query(Job).filter(Job.employer_id == current_user.id)

    if status:
        query = query.filter(Job.status == JobStatus(status))

    total = query.count()
    total_pages = (total + limit - 1) // limit

    jobs = query.order_by(Job.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    items = []
    for job in jobs:
        app_count = db.query(Application).filter(Application.job_id == job.id).count()
        items.append(job_to_response(job, app_count))

    return JobListResponse(
        items=items,
        total=total,
        page=page,
        totalPages=total_pages
    )


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """求人詳細を取得"""
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="求人が見つかりません"
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この求人へのアクセス権限がありません"
        )

    app_count = db.query(Application).filter(Application.job_id == job.id).count()

    return job_to_response(job, app_count)


@router.put("/jobs/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    request: JobUpdateRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """求人を更新"""
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="求人が見つかりません"
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この求人の更新権限がありません"
        )

    if request.title is not None:
        job.title = request.title
    if request.description is not None:
        job.description = request.description
    if request.location is not None:
        job.location = request.location
    if request.employmentType is not None:
        job.employment_type = EmploymentType(request.employmentType)
    if request.salaryMin is not None:
        job.salary_min = request.salaryMin
    if request.salaryMax is not None:
        job.salary_max = request.salaryMax
    if request.requiredSkills is not None:
        job.required_skills = json.dumps(request.requiredSkills)
    if request.preferredSkills is not None:
        job.preferred_skills = json.dumps(request.preferredSkills)
    if request.requirements is not None:
        job.requirements = request.requirements
    if request.benefits is not None:
        job.benefits = request.benefits
    if request.status is not None:
        old_status = job.status
        job.status = JobStatus(request.status)
        if old_status != JobStatus.PUBLISHED and job.status == JobStatus.PUBLISHED:
            job.posted_date = datetime.utcnow()

    db.commit()
    db.refresh(job)

    app_count = db.query(Application).filter(Application.job_id == job.id).count()

    return job_to_response(job, app_count)


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """求人を削除"""
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="求人が見つかりません"
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この求人の削除権限がありません"
        )

    db.delete(job)
    db.commit()


@router.post("/jobs/chat", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """AI対話型ヒアリング - メッセージを送信"""
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="企業ユーザーのみアクセス可能です"
        )

    session_id = request.sessionId or str(uuid.uuid4())

    openai_service = get_openai_service()

    if openai_service.client:
        try:
            system_prompt = """あなたは求人作成をサポートするAIアシスタントです。
企業の採用担当者から求人内容についてヒアリングを行い、魅力的な求人票の作成をサポートしてください。
以下の点について質問しながら情報を収集してください：
- 募集職種と仕事内容
- 必要なスキルと経験
- 勤務地と勤務形態
- 給与・待遇
- 会社の魅力や文化

回答は簡潔に、200文字程度でお願いします。"""

            response = openai_service.client.chat.completions.create(
                model=openai_service.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": request.message}
                ],
                max_tokens=500,
                temperature=0.7
            )

            reply_content = response.choices[0].message.content.strip()

        except Exception as e:
            reply_content = f"申し訳ございません。AIとの通信でエラーが発生しました。"
    else:
        reply_content = "OpenAI APIが設定されていません。管理者にお問い合わせください。"

    response_message = ChatMessage(
        id=str(uuid.uuid4()),
        role="assistant",
        content=reply_content,
        timestamp=datetime.utcnow().isoformat()
    )

    return ChatResponse(
        sessionId=session_id,
        message=response_message,
        isComplete=False
    )


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """ダッシュボードの統計情報を取得"""
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="企業ユーザーのみアクセス可能です"
        )

    # 求人統計
    total_jobs = db.query(Job).filter(Job.employer_id == current_user.id).count()
    published_jobs = db.query(Job).filter(
        Job.employer_id == current_user.id,
        Job.status == JobStatus.PUBLISHED
    ).count()
    draft_jobs = db.query(Job).filter(
        Job.employer_id == current_user.id,
        Job.status == JobStatus.DRAFT
    ).count()
    closed_jobs = db.query(Job).filter(
        Job.employer_id == current_user.id,
        Job.status == JobStatus.CLOSED
    ).count()

    # 応募統計（自社の求人への応募）
    employer_job_ids = [j.id for j in db.query(Job.id).filter(Job.employer_id == current_user.id).all()]

    if employer_job_ids:
        total_applications = db.query(Application).filter(
            Application.job_id.in_(employer_job_ids)
        ).count()
        pending_applications = db.query(Application).filter(
            Application.job_id.in_(employer_job_ids),
            Application.status == ApplicationStatus.PENDING
        ).count()
        interview_applications = db.query(Application).filter(
            Application.job_id.in_(employer_job_ids),
            Application.status == ApplicationStatus.INTERVIEW
        ).count()
        offer_applications = db.query(Application).filter(
            Application.job_id.in_(employer_job_ids),
            Application.status == ApplicationStatus.OFFERED
        ).count()
    else:
        total_applications = 0
        pending_applications = 0
        interview_applications = 0
        offer_applications = 0

    return DashboardStats(
        totalJobs=total_jobs,
        publishedJobs=published_jobs,
        draftJobs=draft_jobs,
        closedJobs=closed_jobs,
        totalApplications=total_applications,
        pendingApplications=pending_applications,
        interviewApplications=interview_applications,
        offerApplications=offer_applications
    )
