# app/services/user_service.py
"""
ユーザーサービス
"""
from typing import Optional, List
import json
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    """ユーザーサービス"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_by_id(self, user_id: str) -> Optional[User]:
        """ユーザーを取得"""
        return self.user_repo.get_by_id(user_id)

    def update_preferences(
        self,
        user: User,
        salary: Optional[int] = None,
        job_type: Optional[str] = None,
        desired_location: Optional[str] = None,
        desired_employment_type: Optional[str] = None,
    ) -> User:
        """希望条件を更新"""
        if salary is not None:
            user.desired_salary_min = str(salary)
            user.desired_salary_max = str(salary)

        if job_type:
            user.skills = json.dumps([job_type])

        if desired_location:
            user.desired_location = desired_location

        if desired_employment_type:
            user.desired_employment_type = desired_employment_type

        # プロフィール完成度を更新
        user.profile_completion = str(self._calculate_profile_completion(user))

        return self.user_repo.update(user)

    def update_profile(
        self,
        user: User,
        name: Optional[str] = None,
        skills: Optional[List[str]] = None,
        experience_years: Optional[str] = None,
        desired_salary_min: Optional[str] = None,
        desired_salary_max: Optional[str] = None,
        desired_location: Optional[str] = None,
        desired_employment_type: Optional[str] = None,
        resume_url: Optional[str] = None,
        portfolio_url: Optional[str] = None,
        company_name: Optional[str] = None,
        industry: Optional[str] = None,
        company_size: Optional[str] = None,
        company_description: Optional[str] = None,
        company_website: Optional[str] = None,
        company_location: Optional[str] = None,
        company_logo_url: Optional[str] = None,
    ) -> User:
        """プロフィールを更新"""
        if name is not None:
            user.name = name

        # 求職者用フィールド
        if user.role.value == "seeker":
            if skills is not None:
                user.skills = json.dumps(skills)
            if experience_years is not None:
                user.experience_years = experience_years
            if desired_salary_min is not None:
                user.desired_salary_min = desired_salary_min
            if desired_salary_max is not None:
                user.desired_salary_max = desired_salary_max
            if desired_location is not None:
                user.desired_location = desired_location
            if desired_employment_type is not None:
                user.desired_employment_type = desired_employment_type
            if resume_url is not None:
                user.resume_url = resume_url
            if portfolio_url is not None:
                user.portfolio_url = portfolio_url

        # 企業用フィールド
        if user.role.value == "employer":
            if company_name is not None:
                user.company_name = company_name
            if industry is not None:
                user.industry = industry
            if company_size is not None:
                user.company_size = company_size
            if company_description is not None:
                user.company_description = company_description
            if company_website is not None:
                user.company_website = company_website
            if company_location is not None:
                user.company_location = company_location
            if company_logo_url is not None:
                user.company_logo_url = company_logo_url

        # プロフィール完成度を計算
        user.profile_completion = str(self._calculate_profile_completion(user))

        return self.user_repo.update(user)

    def _calculate_profile_completion(self, user: User) -> int:
        """プロフィール完成度を計算"""
        completion = 0

        if user.name:
            completion += 20

        if user.role.value == "seeker":
            if user.skills:
                completion += 20
            if user.experience_years:
                completion += 20
            if user.desired_salary_min:
                completion += 20
            if user.desired_location:
                completion += 20
        else:  # employer
            if user.company_name:
                completion += 20
            if user.industry:
                completion += 20
            if user.company_size:
                completion += 20
            if user.company_description:
                completion += 20

        return min(completion, 100)

    def parse_skills(self, user: User) -> Optional[List[str]]:
        """スキルをJSON解析"""
        if not user.skills:
            return None
        try:
            return json.loads(user.skills)
        except:
            return None
