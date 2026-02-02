# app/repositories/scout_repository.py
"""
スカウトリポジトリ
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.scout import Scout, ScoutStatus


class ScoutRepository(BaseRepository[Scout]):
    """スカウトリポジトリ"""

    def __init__(self, db: Session):
        super().__init__(Scout, db)

    def get_by_seeker(
        self,
        seeker_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Scout]:
        """求職者のスカウト一覧を取得"""
        query = self.db.query(Scout).filter(Scout.seeker_id == seeker_id)

        if status:
            query = query.filter(Scout.status == status)

        return query.order_by(Scout.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_employer(
        self,
        employer_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Scout]:
        """企業のスカウト一覧を取得"""
        query = self.db.query(Scout).filter(Scout.employer_id == employer_id)

        if status:
            query = query.filter(Scout.status == status)

        return query.order_by(Scout.created_at.desc()).offset(skip).limit(limit).all()

    def count_by_seeker(self, seeker_id: str) -> int:
        """求職者のスカウト件数"""
        return self.db.query(Scout).filter(Scout.seeker_id == seeker_id).count()

    def count_by_seeker_and_status(self, seeker_id: str, status: ScoutStatus) -> int:
        """求職者のステータス別スカウト件数"""
        return (
            self.db.query(Scout)
            .filter(Scout.seeker_id == seeker_id)
            .filter(Scout.status == status)
            .count()
        )

    def count_by_employer(self, employer_id: str) -> int:
        """企業のスカウト件数"""
        return self.db.query(Scout).filter(Scout.employer_id == employer_id).count()

    def count_new_by_seeker(self, seeker_id: str) -> int:
        """求職者の未読スカウト件数"""
        return (
            self.db.query(Scout)
            .filter(Scout.seeker_id == seeker_id)
            .filter(Scout.status == ScoutStatus.NEW)
            .count()
        )
