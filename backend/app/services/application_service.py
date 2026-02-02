# app/services/application_service.py
"""
応募サービス
"""
from typing import Optional, List, Dict, Any
import uuid
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.job import Job
from app.models.user import User
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository


class ApplicationService:
    """応募サービス"""

    def __init__(self, db: Session):
        self.db = db
        self.app_repo = ApplicationRepository(db)
        self.job_repo = JobRepository(db)

    def get_seeker_applications(self, seeker_id: str) -> Dict[str, Any]:
        """求職者の応募一覧を取得"""
        applications = self.app_repo.get_by_seeker(seeker_id)
        total = self.app_repo.count_by_seeker(seeker_id)

        return {
            "applications": applications,
            "total": total,
        }

    def get_application_detail(self, application_id: str) -> Optional[Application]:
        """応募詳細を取得"""
        return self.app_repo.get_by_id(application_id)

    def create_application(
        self,
        seeker: User,
        job_id: str,
        message: Optional[str] = None,
        resume_submitted: bool = False,
        portfolio_submitted: bool = False,
        cover_letter: Optional[str] = None,
    ) -> Application:
        """応募を作成"""
        # 求人の存在確認
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError("求人が見つかりません")

        # 既に応募済みか確認
        if self.app_repo.exists(seeker.id, job_id):
            raise ValueError("既に応募済みです")

        application = Application(
            id=str(uuid.uuid4()),
            job_id=job_id,
            seeker_id=seeker.id,
            status=ApplicationStatus.SCREENING,
            message=message,
            resume_submitted=resume_submitted,
            portfolio_submitted=portfolio_submitted,
            cover_letter_submitted=bool(cover_letter),
        )

        return self.app_repo.create(application)

    def update_application(
        self,
        application: Application,
        status: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Application:
        """応募を更新"""
        if status is not None:
            application.status = ApplicationStatus(status)
        if notes is not None:
            application.notes = notes

        return self.app_repo.update(application)

    def get_status_color(self, status: str) -> str:
        """ステータスに対応する色を取得"""
        status_colors = {
            "screening": "blue",
            "interview": "yellow",
            "offered": "green",
            "rejected": "red",
            "withdrawn": "gray",
        }
        return status_colors.get(status, "gray")

    def application_to_item(self, application: Application, job: Job, employer: Optional[User] = None) -> Dict[str, Any]:
        """応募をリストアイテム形式に変換"""
        salary = ""
        if job.salary_min and job.salary_max:
            salary = f"{job.salary_min}万円〜{job.salary_max}万円"
        elif job.salary_min:
            salary = f"{job.salary_min}万円〜"

        return {
            "id": application.id,
            "jobId": job.id,
            "jobTitle": job.title,
            "company": employer.company_name if employer else "企業名非公開",
            "location": job.location,
            "salary": salary,
            "matchScore": application.match_score,
            "status": application.status.value,
            "statusColor": self.get_status_color(application.status.value),
            "appliedDate": application.created_at.isoformat() if application.created_at else None,
            "lastUpdate": application.updated_at.isoformat() if application.updated_at else None,
            "documents": {
                "resume": application.resume_submitted,
                "portfolio": application.portfolio_submitted,
                "coverLetter": application.cover_letter_submitted,
            },
        }

    def application_to_detail(self, application: Application, job: Job, employer: Optional[User] = None) -> Dict[str, Any]:
        """応募を詳細形式に変換"""
        item = self.application_to_item(application, job, employer)
        item.update({
            "message": application.message,
            "notes": application.notes,
            "interviewDate": application.interview_date.isoformat() if application.interview_date else None,
        })
        return item

    def get_employer_stats(self, employer_id: str) -> Dict[str, int]:
        """企業の応募統計を取得"""
        return {
            "total": self.app_repo.count_by_employer(employer_id),
            "screening": self.app_repo.count_by_employer_and_status(employer_id, ApplicationStatus.SCREENING),
            "interview": self.app_repo.count_by_employer_and_status(employer_id, ApplicationStatus.INTERVIEW),
            "offered": self.app_repo.count_by_employer_and_status(employer_id, ApplicationStatus.OFFERED),
        }
