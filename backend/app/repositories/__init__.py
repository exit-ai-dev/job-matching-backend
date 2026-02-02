# app/repositories/__init__.py
"""
Repository層 - データアクセスの抽象化
"""
from app.repositories.base import BaseRepository
from app.repositories.user_repository import UserRepository
from app.repositories.job_repository import JobRepository
from app.repositories.application_repository import ApplicationRepository
from app.repositories.scout_repository import ScoutRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.candidate_repository import CandidateRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "JobRepository",
    "ApplicationRepository",
    "ScoutRepository",
    "ResumeRepository",
    "CandidateRepository",
]
