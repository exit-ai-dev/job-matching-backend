# app/schemas/user.py
"""
ユーザー関連のスキーマ
"""
from pydantic import BaseModel, Field
from typing import Optional, Any


class PreferencesRequest(BaseModel):
    """希望条件保存リクエスト"""
    salary: Optional[int] = Field(None, description="希望年収（万円）")
    jobType: Optional[list[str]] = Field(None, description="希望職種（複数可）")
    answers: Optional[dict[str, Any]] = Field(None, description="動的な質問への回答")

    # その他の希望条件
    desiredLocation: Optional[str] = None
    desiredLocations: Optional[list[str]] = Field(None, description="希望勤務地（複数可）")
    desiredEmploymentType: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    """プロフィール更新リクエスト"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)

    # 求職者用フィールド
    skills: Optional[list[str]] = None
    experienceYears: Optional[str] = None
    desiredSalaryMin: Optional[str] = None
    desiredSalaryMax: Optional[str] = None
    desiredLocation: Optional[str] = None
    desiredEmploymentType: Optional[str] = None
    resumeUrl: Optional[str] = None
    portfolioUrl: Optional[str] = None

    # 企業用フィールド
    companyName: Optional[str] = None
    industry: Optional[str] = None
    companySize: Optional[str] = None
    companyDescription: Optional[str] = None
    companyWebsite: Optional[str] = None
    companyLocation: Optional[str] = None
    companyLogoUrl: Optional[str] = None
