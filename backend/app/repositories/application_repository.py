# app/repositories/application_repository.py
"""
応募リポジトリ
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.application import Application, ApplicationStatus


class ApplicationRepository(BaseRepository[Application]):
    """応募リポジトリ"""

    def __init__(self, db: Session):
        super().__init__(Application, db)

    def get_by_seeker(self, seeker_id: str, skip: int = 0, limit: int = 100) -> List[Application]:
        """求職者の応募一覧を取得"""
        return (
            self.db.query(Application)
            .filter(Application.seeker_id == seeker_id)
            .order_by(Application.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_job(self, job_id: str, skip: int = 0, limit: int = 100) -> List[Application]:
        """求人への応募一覧を取得"""
        return (
            self.db.query(Application)
            .filter(Application.job_id == job_id)
            .order_by(Application.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_seeker_and_job(self, seeker_id: str, job_id: str) -> Optional[Application]:
        """求職者と求人の組み合わせで取得"""
        return (
            self.db.query(Application)
            .filter(Application.seeker_id == seeker_id)
            .filter(Application.job_id == job_id)
            .first()
        )

    def count_by_seeker(self, seeker_id: str) -> int:
        """求職者の応募件数"""
        return self.db.query(Application).filter(Application.seeker_id == seeker_id).count()

    def count_by_job(self, job_id: str) -> int:
        """求人への応募件数"""
        return self.db.query(Application).filter(Application.job_id == job_id).count()

    def count_by_employer(self, employer_id: str) -> int:
        """企業への応募件数（全求人合計）"""
        from app.models.job import Job
        return (
            self.db.query(Application)
            .join(Job)
            .filter(Job.employer_id == employer_id)
            .count()
        )

    def count_by_employer_and_status(self, employer_id: str, status: ApplicationStatus) -> int:
        """企業のステータス別応募件数"""
        from app.models.job import Job
        return (
            self.db.query(Application)
            .join(Job)
            .filter(Job.employer_id == employer_id)
            .filter(Application.status == status)
            .count()
        )

    def get_by_employer(self, employer_id: str, skip: int = 0, limit: int = 100) -> List[Application]:
        """企業への応募一覧を取得"""
        from app.models.job import Job
        return (
            self.db.query(Application)
            .join(Job)
            .filter(Job.employer_id == employer_id)
            .order_by(Application.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def exists(self, seeker_id: str, job_id: str) -> bool:
        """既に応募済みか確認"""
        return self.get_by_seeker_and_job(seeker_id, job_id) is not None
