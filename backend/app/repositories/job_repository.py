# app/repositories/job_repository.py
"""
求人リポジトリ
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.repositories.base import BaseRepository
from app.models.job import Job, JobStatus, EmploymentType


class JobRepository(BaseRepository[Job]):
    """求人リポジトリ"""

    def __init__(self, db: Session):
        super().__init__(Job, db)

    def get_published(self, skip: int = 0, limit: int = 100) -> List[Job]:
        """公開中の求人を取得"""
        return (
            self.db.query(Job)
            .filter(Job.status == JobStatus.PUBLISHED)
            .order_by(Job.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_employer(self, employer_id: str, skip: int = 0, limit: int = 100) -> List[Job]:
        """企業IDで求人を取得"""
        return (
            self.db.query(Job)
            .filter(Job.employer_id == employer_id)
            .order_by(Job.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_employer(self, employer_id: str) -> int:
        """企業の求人件数"""
        return self.db.query(Job).filter(Job.employer_id == employer_id).count()

    def count_published(self) -> int:
        """公開中の求人件数"""
        return self.db.query(Job).filter(Job.status == JobStatus.PUBLISHED).count()

    def count_by_employer_and_status(self, employer_id: str, status: JobStatus) -> int:
        """企業のステータス別求人件数"""
        return (
            self.db.query(Job)
            .filter(Job.employer_id == employer_id)
            .filter(Job.status == status)
            .count()
        )

    def search(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        employment_type: Optional[str] = None,
        remote_ok: Optional[bool] = None,
        salary_min: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Job]:
        """求人を検索"""
        db_query = self.db.query(Job).filter(Job.status == JobStatus.PUBLISHED)

        if query:
            search_pattern = f"%{query}%"
            db_query = db_query.filter(
                or_(
                    Job.title.ilike(search_pattern),
                    Job.description.ilike(search_pattern),
                    Job.required_skills.ilike(search_pattern),
                )
            )

        if location:
            db_query = db_query.filter(Job.location.ilike(f"%{location}%"))

        if employment_type:
            db_query = db_query.filter(Job.employment_type == employment_type)

        if remote_ok is not None:
            db_query = db_query.filter(Job.remote_ok == remote_ok)

        if salary_min is not None:
            db_query = db_query.filter(Job.salary_min >= salary_min)

        return db_query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

    def increment_view_count(self, job: Job) -> Job:
        """閲覧数をインクリメント"""
        job.view_count = (job.view_count or 0) + 1
        self.db.commit()
        self.db.refresh(job)
        return job
