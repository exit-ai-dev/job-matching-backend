# app/repositories/user_repository.py
"""
ユーザーリポジトリ
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.user import User, UserRole


class UserRepository(BaseRepository[User]):
    """ユーザーリポジトリ"""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """メールアドレスで取得"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_line_user_id(self, line_user_id: str) -> Optional[User]:
        """LINE IDで取得"""
        return self.db.query(User).filter(User.line_user_id == line_user_id).first()

    def get_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """ロールで取得"""
        return (
            self.db.query(User)
            .filter(User.role == role)
            .filter(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_seekers(self, skip: int = 0, limit: int = 100) -> List[User]:
        """求職者一覧を取得"""
        return self.get_by_role(UserRole.SEEKER, skip, limit)

    def get_employers(self, skip: int = 0, limit: int = 100) -> List[User]:
        """企業一覧を取得"""
        return self.get_by_role(UserRole.EMPLOYER, skip, limit)

    def count_by_role(self, role: UserRole) -> int:
        """ロール別件数"""
        return (
            self.db.query(User)
            .filter(User.role == role)
            .filter(User.is_active == True)
            .count()
        )

    def search_seekers(
        self,
        skills: Optional[List[str]] = None,
        location: Optional[str] = None,
        experience_years: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """求職者を検索"""
        query = (
            self.db.query(User)
            .filter(User.role == UserRole.SEEKER)
            .filter(User.is_active == True)
        )

        if location:
            query = query.filter(User.desired_location.ilike(f"%{location}%"))

        if experience_years:
            query = query.filter(User.experience_years == experience_years)

        if skills:
            for skill in skills:
                query = query.filter(User.skills.ilike(f"%{skill}%"))

        return query.offset(skip).limit(limit).all()

    def email_exists(self, email: str) -> bool:
        """メールアドレスが既に存在するか確認"""
        return self.db.query(User).filter(User.email == email).first() is not None
