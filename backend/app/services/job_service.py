# app/services/job_service.py
"""
求人サービス
"""
from typing import Optional, List, Dict, Any
import uuid
import json
from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus, EmploymentType
from app.models.user import User
from app.repositories.job_repository import JobRepository
from app.repositories.application_repository import ApplicationRepository


class JobService:
    """求人サービス"""

    def __init__(self, db: Session):
        self.db = db
        self.job_repo = JobRepository(db)
        self.app_repo = ApplicationRepository(db)

    def get_published_jobs(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """公開中の求人一覧を取得"""
        skip = (page - 1) * per_page
        jobs = self.job_repo.get_published(skip=skip, limit=per_page)
        total = self.job_repo.count_published()

        return {
            "jobs": jobs,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    def get_job_detail(self, job_id: str, increment_view: bool = True) -> Optional[Job]:
        """求人詳細を取得"""
        job = self.job_repo.get_by_id(job_id)
        if job and increment_view:
            self.job_repo.increment_view_count(job)
        return job

    def search_jobs(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        employment_type: Optional[str] = None,
        remote_ok: Optional[bool] = None,
        salary_min: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict[str, Any]:
        """求人を検索"""
        skip = (page - 1) * per_page
        jobs = self.job_repo.search(
            query=query,
            location=location,
            employment_type=employment_type,
            remote_ok=remote_ok,
            salary_min=salary_min,
            skip=skip,
            limit=per_page,
        )

        return {
            "jobs": jobs,
            "total": len(jobs),  # 簡易実装。正確にはcount queryが必要
            "page": page,
            "per_page": per_page,
        }

    def get_employer_jobs(self, employer_id: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """企業の求人一覧を取得"""
        skip = (page - 1) * per_page
        jobs = self.job_repo.get_by_employer(employer_id, skip=skip, limit=per_page)
        total = self.job_repo.count_by_employer(employer_id)

        # 各求人の応募数を取得
        jobs_with_counts = []
        for job in jobs:
            app_count = self.app_repo.count_by_job(job.id)
            jobs_with_counts.append({
                "job": job,
                "applications_count": app_count,
            })

        return {
            "jobs": jobs_with_counts,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    def create_job(
        self,
        employer: User,
        title: str,
        description: str,
        location: str,
        employment_type: str,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        required_skills: Optional[List[str]] = None,
        preferred_skills: Optional[List[str]] = None,
        requirements: Optional[str] = None,
        benefits: Optional[str] = None,
        remote_ok: bool = False,
        status: str = "draft",
    ) -> Job:
        """求人を作成"""
        job = Job(
            id=str(uuid.uuid4()),
            employer_id=employer.id,
            title=title,
            description=description,
            location=location,
            employment_type=employment_type,
            salary_min=salary_min,
            salary_max=salary_max,
            required_skills=json.dumps(required_skills) if required_skills else None,
            preferred_skills=json.dumps(preferred_skills) if preferred_skills else None,
            requirements=requirements,
            benefits=benefits,
            remote_ok=remote_ok,
            status=JobStatus(status) if status else JobStatus.DRAFT,
        )

        return self.job_repo.create(job)

    def update_job(
        self,
        job: Job,
        title: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        employment_type: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        required_skills: Optional[List[str]] = None,
        preferred_skills: Optional[List[str]] = None,
        requirements: Optional[str] = None,
        benefits: Optional[str] = None,
        remote_ok: Optional[bool] = None,
        status: Optional[str] = None,
    ) -> Job:
        """求人を更新"""
        if title is not None:
            job.title = title
        if description is not None:
            job.description = description
        if location is not None:
            job.location = location
        if employment_type is not None:
            job.employment_type = employment_type
        if salary_min is not None:
            job.salary_min = salary_min
        if salary_max is not None:
            job.salary_max = salary_max
        if required_skills is not None:
            job.required_skills = json.dumps(required_skills)
        if preferred_skills is not None:
            job.preferred_skills = json.dumps(preferred_skills)
        if requirements is not None:
            job.requirements = requirements
        if benefits is not None:
            job.benefits = benefits
        if remote_ok is not None:
            job.remote_ok = remote_ok
        if status is not None:
            job.status = JobStatus(status)

        return self.job_repo.update(job)

    def job_to_list_item(self, job: Job, employer: Optional[User] = None) -> Dict[str, Any]:
        """求人をリストアイテム形式に変換"""
        skills = []
        if job.required_skills:
            try:
                skills = json.loads(job.required_skills)
            except:
                pass

        salary = ""
        if job.salary_min and job.salary_max:
            salary = f"{job.salary_min}万円〜{job.salary_max}万円"
        elif job.salary_min:
            salary = f"{job.salary_min}万円〜"
        elif job.salary_max:
            salary = f"〜{job.salary_max}万円"
        elif job.salary_text:
            salary = job.salary_text

        return {
            "id": job.id,
            "title": job.title,
            "company": employer.company_name if employer else "企業名非公開",
            "location": job.location,
            "salary": salary,
            "employmentType": job.employment_type,
            "remote": job.remote_ok,
            "tags": skills[:5],
            "description": job.description[:200] + "..." if len(job.description) > 200 else job.description,
            "featured": False,
            "postedDate": job.created_at.isoformat() if job.created_at else None,
        }

    def job_to_detail(self, job: Job, employer: Optional[User] = None) -> Dict[str, Any]:
        """求人を詳細形式に変換"""
        item = self.job_to_list_item(job, employer)

        requirements = []
        if job.requirements:
            requirements = [r.strip() for r in job.requirements.split("\n") if r.strip()]

        benefits = []
        if job.benefits:
            benefits = [b.strip() for b in job.benefits.split("\n") if b.strip()]

        item.update({
            "description": job.description,
            "requirements": requirements,
            "benefits": benefits,
        })

        return item
