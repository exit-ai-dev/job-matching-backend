# app/repositories/candidate_repository.py
"""
候補者リポジトリ（企業向けの求職者閲覧用）
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User, UserRole
from app.models.resume import Resume


class CandidateRepository:
    """候補者リポジトリ（求職者を企業視点で取得）"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """全候補者を取得（アクティブな求職者のみ）"""
        return (
            self.db.query(User)
            .filter(User.role == UserRole.SEEKER)
            .filter(User.is_active == True)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, candidate_id: str) -> Optional[User]:
        """候補者IDで取得"""
        return (
            self.db.query(User)
            .filter(User.id == candidate_id)
            .filter(User.role == UserRole.SEEKER)
            .filter(User.is_active == True)
            .first()
        )

    def get_with_resume(self, candidate_id: str) -> Optional[dict]:
        """候補者と履歴書を取得"""
        user = self.get_by_id(candidate_id)
        if not user:
            return None

        resume = self.db.query(Resume).filter(Resume.user_id == candidate_id).first()

        return {
            "user": user,
            "resume": resume,
        }

    def count(self) -> int:
        """候補者総数"""
        return (
            self.db.query(User)
            .filter(User.role == UserRole.SEEKER)
            .filter(User.is_active == True)
            .count()
        )

    def search(
        self,
        query: Optional[str] = None,
        skills: Optional[List[str]] = None,
        location: Optional[str] = None,
        experience_years: Optional[str] = None,
        employment_type: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """候補者を検索"""
        db_query = (
            self.db.query(User)
            .filter(User.role == UserRole.SEEKER)
            .filter(User.is_active == True)
        )

        if query:
            search_pattern = f"%{query}%"
            db_query = db_query.filter(
                or_(
                    User.name.ilike(search_pattern),
                    User.skills.ilike(search_pattern),
                )
            )

        if skills:
            for skill in skills:
                db_query = db_query.filter(User.skills.ilike(f"%{skill}%"))

        if location:
            db_query = db_query.filter(User.desired_location.ilike(f"%{location}%"))

        if experience_years:
            db_query = db_query.filter(User.experience_years == experience_years)

        if employment_type:
            db_query = db_query.filter(User.desired_employment_type == employment_type)

        if salary_min is not None:
            db_query = db_query.filter(
                or_(
                    User.desired_salary_min.is_(None),
                    User.desired_salary_min.cast(db_query.column_descriptions[0]['type']) >= str(salary_min),
                )
            )

        return db_query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    def search_count(
        self,
        query: Optional[str] = None,
        skills: Optional[List[str]] = None,
        location: Optional[str] = None,
        experience_years: Optional[str] = None,
        employment_type: Optional[str] = None,
    ) -> int:
        """検索結果の件数"""
        db_query = (
            self.db.query(User)
            .filter(User.role == UserRole.SEEKER)
            .filter(User.is_active == True)
        )

        if query:
            search_pattern = f"%{query}%"
            db_query = db_query.filter(
                or_(
                    User.name.ilike(search_pattern),
                    User.skills.ilike(search_pattern),
                )
            )

        if skills:
            for skill in skills:
                db_query = db_query.filter(User.skills.ilike(f"%{skill}%"))

        if location:
            db_query = db_query.filter(User.desired_location.ilike(f"%{location}%"))

        if experience_years:
            db_query = db_query.filter(User.experience_years == experience_years)

        if employment_type:
            db_query = db_query.filter(User.desired_employment_type == employment_type)

        return db_query.count()
