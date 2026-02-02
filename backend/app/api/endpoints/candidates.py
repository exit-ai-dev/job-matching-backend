# app/api/endpoints/candidates.py
"""
候補者API（企業向け）
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.schemas.candidate import (
    CandidateItem,
    CandidateDetail,
    CandidateListResponse,
    CandidateSearchRequest,
)
from app.services.candidate_service import CandidateService
from app.core.dependencies import CurrentUser
from app.db.session import get_db

router = APIRouter()


def get_candidate_service(db: Session = Depends(get_db)) -> CandidateService:
    """候補者サービスを取得"""
    return CandidateService(db)


@router.get("/", response_model=CandidateListResponse)
async def get_candidates(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = None,
    service: CandidateService = Depends(get_candidate_service),
):
    """
    候補者一覧を取得（企業向け）

    Args:
        page: ページ番号
        per_page: 1ページあたりの件数
        current_user: 現在のユーザー（企業のみ）
        service: 候補者サービス

    Returns:
        候補者一覧
    """
    # 企業ユーザーのみアクセス可能
    if current_user.role.value != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="企業ユーザーのみアクセス可能です"
        )

    result = service.get_candidates(page=page, per_page=per_page)

    return CandidateListResponse(
        candidates=[CandidateItem(**c) for c in result["candidates"]],
        total=result["total"],
        page=result["page"],
        perPage=result["per_page"],
    )


@router.get("/{candidate_id}", response_model=CandidateDetail)
async def get_candidate(
    candidate_id: str,
    current_user: CurrentUser = None,
    service: CandidateService = Depends(get_candidate_service),
):
    """
    候補者詳細を取得（企業向け）

    Args:
        candidate_id: 候補者ID
        current_user: 現在のユーザー（企業のみ）
        service: 候補者サービス

    Returns:
        候補者詳細
    """
    # 企業ユーザーのみアクセス可能
    if current_user.role.value != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="企業ユーザーのみアクセス可能です"
        )

    result = service.get_candidate_detail(candidate_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="候補者が見つかりません"
        )

    return CandidateDetail(**result)


@router.post("/search", response_model=CandidateListResponse)
async def search_candidates(
    request: CandidateSearchRequest,
    current_user: CurrentUser = None,
    service: CandidateService = Depends(get_candidate_service),
):
    """
    候補者を検索（企業向け）

    Args:
        request: 検索リクエスト
        current_user: 現在のユーザー（企業のみ）
        service: 候補者サービス

    Returns:
        検索結果
    """
    # 企業ユーザーのみアクセス可能
    if current_user.role.value != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="企業ユーザーのみアクセス可能です"
        )

    result = service.search_candidates(
        query=request.query,
        skills=request.skills,
        location=request.location,
        experience_years=request.experienceYears,
        employment_type=request.employmentType,
        salary_min=request.salaryMin,
        salary_max=request.salaryMax,
        page=request.page,
        per_page=request.perPage,
    )

    return CandidateListResponse(
        candidates=[CandidateItem(**c) for c in result["candidates"]],
        total=result["total"],
        page=result["page"],
        perPage=result["per_page"],
    )
