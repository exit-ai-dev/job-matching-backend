# app/models/__init__.py
"""
データベースモデル
"""
from app.models.user import User, UserRole
from app.models.job import Job, JobStatus, EmploymentType
from app.models.application import Application, ApplicationStatus
from app.models.scout import Scout, ScoutStatus
from app.models.resume import Resume
from app.models.company import Company
from app.models.company_profile import CompanyProfile
from app.models.user_preferences import UserPreferencesProfile
from app.models.conversation import ConversationSession, ConversationLog, ChatSession

__all__ = [
    # ユーザー関連
    "User",
    "UserRole",
    # 求人関連
    "Job",
    "JobStatus",
    "EmploymentType",
    # 応募関連
    "Application",
    "ApplicationStatus",
    # スカウト関連
    "Scout",
    "ScoutStatus",
    # 履歴書
    "Resume",
    # 企業関連（マッチング用）
    "Company",
    "CompanyProfile",
    # ユーザー希望条件
    "UserPreferencesProfile",
    # 会話関連
    "ConversationSession",
    "ConversationLog",
    "ChatSession",
]
