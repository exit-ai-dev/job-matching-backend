# app/api/endpoints/applications.py
"""
応募管理API
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationItem,
    ApplicationDetail,
    ApplicationListResponse,
)
from app.models.application import Application, ApplicationStatus
from app.models.job import Job
from app.models.user import UserRole
from app.db.session import get_db
from app.core.dependencies import CurrentUser

router = APIRouter()


def get_status_color(status: ApplicationStatus) -> str:
    """ステータスに対応する色を取得"""
    colors = {
        ApplicationStatus.PENDING: "yellow",
        ApplicationStatus.SCREENING: "yellow",
        ApplicationStatus.INTERVIEW: "blue",
        ApplicationStatus.OFFERED: "green",
        ApplicationStatus.REJECTED: "red",
        ApplicationStatus.WITHDRAWN: "gray",
        ApplicationStatus.ACCEPTED: "green",
    }
    return colors.get(status, "gray")


def application_to_item(application: Application, job: Job) -> ApplicationItem:
    """ApplicationモデルをApplicationItemに変換"""
    # 給与情報を文字列化
    salary = job.salary_text or ""
    if not salary and job.salary_min and job.salary_max:
        salary = f"{job.salary_min}万円～{job.salary_max}万円"

    return ApplicationItem(
        id=application.id,
        jobId=application.job_id,
        jobTitle=job.title,
        company=job.company,
        location=job.location,
        salary=salary,
        matchScore=application.match_score,
        status=application.status_detail or application.status.value,
        statusColor=application.status_color or get_status_color(application.status),
        appliedDate=application.applied_at.strftime("%Y-%m-%d") if application.applied_at else "",
        lastUpdate=application.updated_at.strftime("%Y-%m-%d") if application.updated_at else "",
        nextStep=application.next_step,
        interviewDate=application.interview_date.isoformat() if application.interview_date else None,
        documents={
            "resume": application.resume_submitted == "true",
            "portfolio": application.portfolio_submitted == "true",
            "coverLetter": bool(application.cover_letter),
        }
    )


def application_to_detail(application: Application, job: Job) -> ApplicationDetail:
    """ApplicationモデルをApplicationDetailに変換"""
    # 給与情報を文字列化
    salary = job.salary_text or ""
    if not salary and job.salary_min and job.salary_max:
        salary = f"{job.salary_min}万円～{job.salary_max}万円"

    return ApplicationDetail(
        id=application.id,
        jobId=application.job_id,
        jobTitle=job.title,
        company=job.company,
        location=job.location,
        salary=salary,
        matchScore=application.match_score,
        status=application.status_detail or application.status.value,
        statusColor=application.status_color or get_status_color(application.status),
        statusDetail=application.status_detail,
        appliedDate=application.applied_at.strftime("%Y-%m-%d") if application.applied_at else "",
        lastUpdate=application.updated_at.strftime("%Y-%m-%d") if application.updated_at else "",
        nextStep=application.next_step,
        interviewDate=application.interview_date.isoformat() if application.interview_date else None,
        message=application.message,
        notes=application.notes,
        documents={
            "resume": application.resume_submitted == "true",
            "portfolio": application.portfolio_submitted == "true",
            "coverLetter": bool(application.cover_letter),
        }
    )


@router.get("/", response_model=ApplicationListResponse)
async def get_applications(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    自分の応募一覧を取得

    Args:
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        応募一覧
    """
    if current_user.role != UserRole.SEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="求職者のみアクセス可能です"
        )

    # 応募を取得
    applications = db.query(Application).filter(
        Application.seeker_id == current_user.id
    ).order_by(Application.applied_at.desc()).all()

    # 求人情報を結合
    items = []
    for application in applications:
        job = db.query(Job).filter(Job.id == application.job_id).first()
        if job:
            items.append(application_to_item(application, job))

    return ApplicationListResponse(
        applications=items,
        total=len(items),
    )


@router.post("/", response_model=ApplicationDetail, status_code=status.HTTP_201_CREATED)
async def create_application(
    request: ApplicationCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    応募する

    Args:
        request: 応募作成リクエスト
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        作成した応募
    """
    if current_user.role != UserRole.SEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="求職者のみ応募できます"
        )

    # 求人が存在するか確認
    job = db.query(Job).filter(Job.id == request.jobId).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="求人が見つかりません"
        )

    # 既に応募済みか確認
    existing = db.query(Application).filter(
        Application.seeker_id == current_user.id,
        Application.job_id == request.jobId
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="既にこの求人に応募済みです"
        )

    # 応募を作成
    application = Application(
        id=str(uuid.uuid4()),
        seeker_id=current_user.id,
        job_id=request.jobId,
        status=ApplicationStatus.PENDING,
        status_detail="書類選考中",
        status_color="yellow",
        message=request.message,
        resume_submitted="true" if request.resumeSubmitted else "false",
        portfolio_submitted="true" if request.portfolioSubmitted else "false",
        cover_letter=request.coverLetter,
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application_to_detail(application, job)


@router.get("/{application_id}", response_model=ApplicationDetail)
async def get_application(
    application_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    応募詳細を取得

    Args:
        application_id: 応募ID
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        応募詳細
    """
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="応募が見つかりません"
        )

    # 求職者本人または求人の企業のみアクセス可能
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="求人が見つかりません"
        )

    if application.seeker_id != current_user.id and job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この応募へのアクセス権限がありません"
        )

    return application_to_detail(application, job)


@router.put("/{application_id}", response_model=ApplicationDetail)
async def update_application(
    application_id: str,
    request: ApplicationUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    応募を更新

    Args:
        application_id: 応募ID
        request: 更新内容
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        更新後の応募
    """
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="応募が見つかりません"
        )

    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="求人が見つかりません"
        )

    # 求職者本人または求人の企業のみ更新可能
    if application.seeker_id != current_user.id and job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この応募の更新権限がありません"
        )

    # 更新
    if request.status:
        try:
            application.status = ApplicationStatus(request.status)
            application.status_color = get_status_color(application.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無効なステータスです"
            )

    if request.notes is not None:
        application.notes = request.notes

    db.commit()
    db.refresh(application)

    return application_to_detail(application, job)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def withdraw_application(
    application_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    応募を取り下げる

    Args:
        application_id: 応募ID
        current_user: 認証済みユーザー
        db: データベースセッション
    """
    if current_user.role != UserRole.SEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="求職者のみ応募を取り下げできます"
        )

    application = db.query(Application).filter(
        Application.id == application_id,
        Application.seeker_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="応募が見つかりません"
        )

    # 取り下げステータスに更新
    application.status = ApplicationStatus.WITHDRAWN
    application.status_detail = "応募取り下げ"
    application.status_color = "gray"

    db.commit()
