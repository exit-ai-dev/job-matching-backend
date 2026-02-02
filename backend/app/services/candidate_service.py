# app/services/candidate_service.py
"""
候補者サービス（企業向け）
"""
from typing import Optional, List, Dict, Any
import json
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.resume import Resume
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.resume_repository import ResumeRepository


class CandidateService:
    """候補者サービス"""

    def __init__(self, db: Session):
        self.db = db
        self.candidate_repo = CandidateRepository(db)
        self.resume_repo = ResumeRepository(db)

    def get_candidates(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """候補者一覧を取得"""
        skip = (page - 1) * per_page
        candidates = self.candidate_repo.get_all(skip=skip, limit=per_page)
        total = self.candidate_repo.count()

        return {
            "candidates": [self.candidate_to_item(c) for c in candidates],
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    def get_candidate_detail(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """候補者詳細を取得"""
        result = self.candidate_repo.get_with_resume(candidate_id)
        if not result:
            return None

        user = result["user"]
        resume = result["resume"]

        return self.candidate_to_detail(user, resume)

    def search_candidates(
        self,
        query: Optional[str] = None,
        skills: Optional[List[str]] = None,
        location: Optional[str] = None,
        experience_years: Optional[str] = None,
        employment_type: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Dict[str, Any]:
        """候補者を検索"""
        skip = (page - 1) * per_page
        candidates = self.candidate_repo.search(
            query=query,
            skills=skills,
            location=location,
            experience_years=experience_years,
            employment_type=employment_type,
            salary_min=salary_min,
            salary_max=salary_max,
            skip=skip,
            limit=per_page,
        )

        total = self.candidate_repo.search_count(
            query=query,
            skills=skills,
            location=location,
            experience_years=experience_years,
            employment_type=employment_type,
        )

        return {
            "candidates": [self.candidate_to_item(c) for c in candidates],
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    def candidate_to_item(self, user: User) -> Dict[str, Any]:
        """候補者をリストアイテム形式に変換"""
        skills = []
        if user.skills:
            try:
                skills = json.loads(user.skills)
            except:
                skills = [user.skills]

        desired_salary = ""
        if user.desired_salary_min and user.desired_salary_max:
            desired_salary = f"{user.desired_salary_min}万円〜{user.desired_salary_max}万円"
        elif user.desired_salary_min:
            desired_salary = f"{user.desired_salary_min}万円〜"

        return {
            "id": user.id,
            "name": user.name,
            "skills": skills[:5] if isinstance(skills, list) else [],
            "experienceYears": user.experience_years,
            "desiredLocation": user.desired_location,
            "desiredSalary": desired_salary,
            "desiredEmploymentType": user.desired_employment_type,
            "profileCompletion": user.profile_completion,
            "createdAt": user.created_at.isoformat() if user.created_at else None,
            "hasResume": self.resume_repo.exists_for_user(user.id),
        }

    def candidate_to_detail(self, user: User, resume: Optional[Resume] = None) -> Dict[str, Any]:
        """候補者を詳細形式に変換"""
        item = self.candidate_to_item(user)

        # 履歴書情報を追加
        if resume:
            item.update({
                "resume": {
                    "lastName": resume.last_name,
                    "firstName": resume.first_name,
                    "lastNameKana": resume.last_name_kana,
                    "firstNameKana": resume.first_name_kana,
                    "birthDate": resume.birth_date,
                    "gender": resume.gender,
                    "phone": resume.phone,
                    "email": resume.email,
                    "address": resume.address,
                    "education": resume.education,
                    "experience": resume.experience,
                    "experienceRoles": resume.experience_roles,
                    "currentSalary": resume.current_salary,
                    "skills": resume.skills,
                    "qualifications": resume.qualifications,
                    "nativeLanguage": resume.native_language,
                    "spokenLanguages": resume.spoken_languages,
                    "languageSkills": resume.language_skills,
                    "summary": resume.summary,
                    "careerChangeReason": resume.career_change_reason,
                    "futureVision": resume.future_vision,
                },
            })
        else:
            item["resume"] = None

        return item
