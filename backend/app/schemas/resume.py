# app/schemas/resume.py
"""
履歴書スキーマ
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ResumeBase(BaseModel):
    """履歴書の基本スキーマ"""
    lastName: Optional[str] = Field(None, max_length=50)
    firstName: Optional[str] = Field(None, max_length=50)
    lastNameKana: Optional[str] = Field(None, max_length=50)
    firstNameKana: Optional[str] = Field(None, max_length=50)
    birthDate: Optional[str] = Field(None, max_length=20)
    gender: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    education: Optional[str] = None
    experience: Optional[str] = None
    experienceRoles: Optional[str] = Field(None, max_length=500)
    currentSalary: Optional[str] = Field(None, max_length=50)
    skills: Optional[str] = None
    qualifications: Optional[str] = None
    nativeLanguage: Optional[str] = Field(None, max_length=50)
    spokenLanguages: Optional[str] = Field(None, max_length=200)
    languageSkills: Optional[str] = None
    summary: Optional[str] = None
    careerChangeReason: Optional[str] = None
    futureVision: Optional[str] = None


class ResumeRequest(ResumeBase):
    """履歴書作成・更新リクエスト"""
    pass


class ResumeResponse(ResumeBase):
    """履歴書レスポンス"""
    id: str
    userId: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
