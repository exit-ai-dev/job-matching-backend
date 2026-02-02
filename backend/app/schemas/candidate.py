# app/schemas/candidate.py
"""
候補者スキーマ
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CandidateItem(BaseModel):
    """候補者リストアイテム"""
    id: str
    name: str
    skills: List[str] = []
    experienceYears: Optional[str] = None
    desiredLocation: Optional[str] = None
    desiredSalary: Optional[str] = None
    desiredEmploymentType: Optional[str] = None
    profileCompletion: Optional[str] = None
    createdAt: Optional[str] = None
    hasResume: bool = False


class ResumeDetail(BaseModel):
    """履歴書詳細"""
    lastName: Optional[str] = None
    firstName: Optional[str] = None
    lastNameKana: Optional[str] = None
    firstNameKana: Optional[str] = None
    birthDate: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None
    experienceRoles: Optional[str] = None
    currentSalary: Optional[str] = None
    skills: Optional[str] = None
    qualifications: Optional[str] = None
    nativeLanguage: Optional[str] = None
    spokenLanguages: Optional[str] = None
    languageSkills: Optional[str] = None
    summary: Optional[str] = None
    careerChangeReason: Optional[str] = None
    futureVision: Optional[str] = None


class CandidateDetail(CandidateItem):
    """候補者詳細"""
    resume: Optional[ResumeDetail] = None


class CandidateListResponse(BaseModel):
    """候補者一覧レスポンス"""
    candidates: List[CandidateItem]
    total: int
    page: int = 1
    perPage: int = 20


class CandidateSearchRequest(BaseModel):
    """候補者検索リクエスト"""
    query: Optional[str] = None
    skills: Optional[List[str]] = None
    location: Optional[str] = None
    experienceYears: Optional[str] = None
    employmentType: Optional[str] = None
    salaryMin: Optional[int] = None
    salaryMax: Optional[int] = None
    page: int = 1
    perPage: int = 20
