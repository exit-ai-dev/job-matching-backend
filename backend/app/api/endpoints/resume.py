# app/api/endpoints/resume.py
"""
履歴書API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.schemas.resume import ResumeRequest, ResumeResponse
from app.models.resume import Resume
from app.core.dependencies import CurrentUser
from app.db.session import get_db

router = APIRouter()


@router.get("", response_model=ResumeResponse)
async def get_resume(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    現在のユーザーの履歴書を取得

    Args:
        current_user: 現在のユーザー
        db: データベースセッション

    Returns:
        履歴書データ
    """
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="履歴書が見つかりません"
        )

    return ResumeResponse(
        id=resume.id,
        userId=resume.user_id,
        lastName=resume.last_name,
        firstName=resume.first_name,
        lastNameKana=resume.last_name_kana,
        firstNameKana=resume.first_name_kana,
        birthDate=resume.birth_date,
        gender=resume.gender,
        phone=resume.phone,
        email=resume.email,
        address=resume.address,
        education=resume.education,
        experience=resume.experience,
        experienceRoles=resume.experience_roles,
        currentSalary=resume.current_salary,
        skills=resume.skills,
        qualifications=resume.qualifications,
        nativeLanguage=resume.native_language,
        spokenLanguages=resume.spoken_languages,
        languageSkills=resume.language_skills,
        summary=resume.summary,
        careerChangeReason=resume.career_change_reason,
        futureVision=resume.future_vision,
        createdAt=resume.created_at,
        updatedAt=resume.updated_at,
    )


@router.put("", response_model=ResumeResponse)
async def save_resume(
    request: ResumeRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    履歴書を保存（作成または更新）

    Args:
        request: 履歴書リクエスト
        current_user: 現在のユーザー
        db: データベースセッション

    Returns:
        保存された履歴書データ
    """
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()

    if not resume:
        # 新規作成
        resume = Resume(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
        )
        db.add(resume)

    # フィールドを更新
    resume.last_name = request.lastName
    resume.first_name = request.firstName
    resume.last_name_kana = request.lastNameKana
    resume.first_name_kana = request.firstNameKana
    resume.birth_date = request.birthDate
    resume.gender = request.gender
    resume.phone = request.phone
    resume.email = request.email
    resume.address = request.address
    resume.education = request.education
    resume.experience = request.experience
    resume.experience_roles = request.experienceRoles
    resume.current_salary = request.currentSalary
    resume.skills = request.skills
    resume.qualifications = request.qualifications
    resume.native_language = request.nativeLanguage
    resume.spoken_languages = request.spokenLanguages
    resume.language_skills = request.languageSkills
    resume.summary = request.summary
    resume.career_change_reason = request.careerChangeReason
    resume.future_vision = request.futureVision

    db.commit()
    db.refresh(resume)

    # プロフィール完成度を100%に更新
    current_user.profile_completion = "100"
    db.commit()

    return ResumeResponse(
        id=resume.id,
        userId=resume.user_id,
        lastName=resume.last_name,
        firstName=resume.first_name,
        lastNameKana=resume.last_name_kana,
        firstNameKana=resume.first_name_kana,
        birthDate=resume.birth_date,
        gender=resume.gender,
        phone=resume.phone,
        email=resume.email,
        address=resume.address,
        education=resume.education,
        experience=resume.experience,
        experienceRoles=resume.experience_roles,
        currentSalary=resume.current_salary,
        skills=resume.skills,
        qualifications=resume.qualifications,
        nativeLanguage=resume.native_language,
        spokenLanguages=resume.spoken_languages,
        languageSkills=resume.language_skills,
        summary=resume.summary,
        careerChangeReason=resume.career_change_reason,
        futureVision=resume.future_vision,
        createdAt=resume.created_at,
        updatedAt=resume.updated_at,
    )
