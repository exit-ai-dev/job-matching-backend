# app/repositories/resume_repository.py
"""
履歴書リポジトリ
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.resume import Resume


class ResumeRepository(BaseRepository[Resume]):
    """履歴書リポジトリ"""

    def __init__(self, db: Session):
        super().__init__(Resume, db)

    def get_by_user_id(self, user_id: str) -> Optional[Resume]:
        """ユーザーIDで履歴書を取得"""
        return self.db.query(Resume).filter(Resume.user_id == user_id).first()

    def exists_for_user(self, user_id: str) -> bool:
        """ユーザーの履歴書が存在するか確認"""
        return self.get_by_user_id(user_id) is not None
