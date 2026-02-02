# app/api/endpoints/users.py
"""
ユーザー管理API
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
import json

from app.schemas.user import PreferencesRequest, ProfileUpdateRequest
from app.schemas.auth import UserResponse
from app.core.dependencies import CurrentUser
from app.db.session import get_db

router = APIRouter()


@router.post("/preferences")
async def save_preferences(
    request: PreferencesRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    希望条件を保存

    Args:
        request: 希望条件リクエスト
        current_user: 現在のユーザー
        db: データベースセッション

    Returns:
        更新されたユーザー情報
    """
    # 希望年収を設定
    if request.salary is not None:
        # salaryは単一の値だが、minとmaxに同じ値を設定
        current_user.desired_salary_min = str(request.salary)
        current_user.desired_salary_max = str(request.salary)

    # 希望職種をスキルとして保存（配列対応）
    if request.jobType:
        current_user.skills = json.dumps(request.jobType)

    # 希望勤務地・雇用形態
    if request.desiredLocation:
        current_user.desired_location = request.desiredLocation
    # desiredLocations（複数）が指定された場合は、カンマ区切りで保存
    if request.desiredLocations:
        current_user.desired_location = ", ".join(request.desiredLocations)
    if request.desiredEmploymentType:
        current_user.desired_employment_type = request.desiredEmploymentType

    # プロフィール完成度を更新（希望条件を設定したので80%に）
    current_user.profile_completion = "80"

    db.commit()
    db.refresh(current_user)

    # スキルをJSON解析
    skills = None
    if current_user.skills:
        try:
            skills = json.loads(current_user.skills)
        except:
            pass

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        lineLinked=current_user.line_user_id is not None,
        profileCompletion=current_user.profile_completion or "0",
        createdAt=current_user.created_at,
        skills=skills,
        experienceYears=current_user.experience_years,
        desiredSalaryMin=current_user.desired_salary_min,
        desiredSalaryMax=current_user.desired_salary_max,
        desiredLocation=current_user.desired_location,
        desiredEmploymentType=current_user.desired_employment_type,
        companyName=current_user.company_name,
        industry=current_user.industry,
        companySize=current_user.company_size,
        companyDescription=current_user.company_description,
    )


@router.put("/profile")
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    プロフィールを更新

    Args:
        request: プロフィール更新リクエスト
        current_user: 現在のユーザー
        db: データベースセッション

    Returns:
        更新されたユーザー情報
    """
    # 基本情報
    if request.name is not None:
        current_user.name = request.name

    # 求職者用フィールド
    if current_user.role.value == "seeker":
        if request.skills is not None:
            current_user.skills = json.dumps(request.skills)
        if request.experienceYears is not None:
            current_user.experience_years = request.experienceYears
        if request.desiredSalaryMin is not None:
            current_user.desired_salary_min = request.desiredSalaryMin
        if request.desiredSalaryMax is not None:
            current_user.desired_salary_max = request.desiredSalaryMax
        if request.desiredLocation is not None:
            current_user.desired_location = request.desiredLocation
        if request.desiredEmploymentType is not None:
            current_user.desired_employment_type = request.desiredEmploymentType
        if request.resumeUrl is not None:
            current_user.resume_url = request.resumeUrl
        if request.portfolioUrl is not None:
            current_user.portfolio_url = request.portfolioUrl

    # 企業用フィールド
    if current_user.role.value == "employer":
        if request.companyName is not None:
            current_user.company_name = request.companyName
        if request.industry is not None:
            current_user.industry = request.industry
        if request.companySize is not None:
            current_user.company_size = request.companySize
        if request.companyDescription is not None:
            current_user.company_description = request.companyDescription
        if request.companyWebsite is not None:
            current_user.company_website = request.companyWebsite
        if request.companyLocation is not None:
            current_user.company_location = request.companyLocation
        if request.companyLogoUrl is not None:
            current_user.company_logo_url = request.companyLogoUrl

    # プロフィール完成度を計算（簡易版）
    completion = 0
    if current_user.name:
        completion += 20
    if current_user.role.value == "seeker":
        if current_user.skills:
            completion += 20
        if current_user.experience_years:
            completion += 20
        if current_user.desired_salary_min:
            completion += 20
        if current_user.desired_location:
            completion += 20
    else:  # employer
        if current_user.company_name:
            completion += 20
        if current_user.industry:
            completion += 20
        if current_user.company_size:
            completion += 20
        if current_user.company_description:
            completion += 20

    current_user.profile_completion = str(min(completion, 100))

    db.commit()
    db.refresh(current_user)

    # スキルをJSON解析
    skills = None
    if current_user.skills:
        try:
            skills = json.loads(current_user.skills)
        except:
            pass

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        lineLinked=current_user.line_user_id is not None,
        profileCompletion=current_user.profile_completion or "0",
        createdAt=current_user.created_at,
        skills=skills,
        experienceYears=current_user.experience_years,
        desiredSalaryMin=current_user.desired_salary_min,
        desiredSalaryMax=current_user.desired_salary_max,
        desiredLocation=current_user.desired_location,
        desiredEmploymentType=current_user.desired_employment_type,
        companyName=current_user.company_name,
        industry=current_user.industry,
        companySize=current_user.company_size,
        companyDescription=current_user.company_description,
    )
