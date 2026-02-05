# app/api/endpoints/scouts.py
"""
スカウトAPI
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid
import json

from app.schemas.scout import (
    ScoutCreate,
    ScoutUpdate,
    ScoutItem,
    ScoutDetail,
    ScoutListResponse,
)
from app.models.scout import Scout, ScoutStatus
from app.models.user import User, UserRole
from app.db.session import get_db
from app.core.dependencies import CurrentUser
from app.core.subscription import verify_subscription_limit

router = APIRouter()


def scout_to_item(scout: Scout, user_role: str, employer: User = None, seeker: User = None) -> ScoutItem:
    """ScoutモデルをScoutItemに変換"""
    # タグをJSON解析
    tags = []
    if scout.tags:
        try:
            tags = json.loads(scout.tags)
        except:
            pass

    return ScoutItem(
        id=scout.id,
        title=scout.title,
        company=employer.company_name if employer and user_role == "seeker" else None,
        candidateName=seeker.name if seeker and user_role == "employer" else None,
        message=scout.message,
        matchScore=scout.match_score,
        status=scout.status.value,
        createdAt=scout.created_at.strftime("%Y-%m-%d") if scout.created_at else "",
        tags=tags,
    )


def scout_to_detail(scout: Scout, user_role: str, employer: User = None, seeker: User = None) -> ScoutDetail:
    """ScoutモデルをScoutDetailに変換"""
    # タグをJSON解析
    tags = []
    if scout.tags:
        try:
            tags = json.loads(scout.tags)
        except:
            pass

    return ScoutDetail(
        id=scout.id,
        title=scout.title,
        company=employer.company_name if employer and user_role == "seeker" else None,
        candidateName=seeker.name if seeker and user_role == "employer" else None,
        message=scout.message,
        matchScore=scout.match_score,
        status=scout.status.value,
        createdAt=scout.created_at.strftime("%Y-%m-%d") if scout.created_at else "",
        readAt=scout.read_at.isoformat() if scout.read_at else None,
        repliedAt=scout.replied_at.isoformat() if scout.replied_at else None,
        tags=tags,
        jobId=scout.job_id,
    )


@router.get("/", response_model=ScoutListResponse)
async def get_scouts(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """
    スカウト一覧を取得（求職者：受信、企業：送信）

    Args:
        current_user: 認証済みユーザー
        status_filter: ステータスフィルター
        db: データベースセッション

    Returns:
        スカウト一覧
    """
    user_role = current_user.role.value

    # ユーザーロールに応じてクエリを変更
    if current_user.role == UserRole.SEEKER:
        # 求職者：受信したスカウト
        query = db.query(Scout).filter(Scout.seeker_id == current_user.id)
    else:
        # 企業：送信したスカウト
        query = db.query(Scout).filter(Scout.employer_id == current_user.id)

    # ステータスフィルター
    if status_filter and status_filter != "all":
        try:
            query = query.filter(Scout.status == ScoutStatus(status_filter))
        except ValueError:
            pass

    # スカウトを取得
    scouts = query.order_by(Scout.created_at.desc()).all()

    # ユーザー情報を結合
    items = []
    for scout in scouts:
        employer = db.query(User).filter(User.id == scout.employer_id).first()
        seeker = db.query(User).filter(User.id == scout.seeker_id).first()
        items.append(scout_to_item(scout, user_role, employer, seeker))

    return ScoutListResponse(
        scouts=items,
        total=len(items),
    )


@router.post("/", response_model=ScoutDetail, status_code=status.HTTP_201_CREATED)
async def create_scout(
    request: ScoutCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    スカウトを送信（企業のみ）

    Args:
        request: スカウト作成リクエスト
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        作成したスカウト
    """
    # 企業のみがスカウトを送信可能
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="企業アカウントのみがスカウトを送信できます"
        )

    # サブスクリプション制限チェック
    await verify_subscription_limit("scout_limit", db, current_user, increment=True)

    # 求職者が存在するか確認
    seeker = db.query(User).filter(
        User.id == request.seekerId,
        User.role == UserRole.SEEKER
    ).first()

    if not seeker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="求職者が見つかりません"
        )

    # スカウトを作成
    scout = Scout(
        id=str(uuid.uuid4()),
        employer_id=current_user.id,
        seeker_id=request.seekerId,
        job_id=request.jobId,
        title=request.title,
        message=request.message,
        tags=json.dumps(request.tags) if request.tags else None,
        status=ScoutStatus.NEW,
    )

    db.add(scout)
    db.commit()
    db.refresh(scout)

    return scout_to_detail(scout, current_user.role.value, current_user, seeker)


@router.get("/{scout_id}", response_model=ScoutDetail)
async def get_scout(
    scout_id: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    スカウト詳細を取得

    Args:
        scout_id: スカウトID
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        スカウト詳細
    """
    scout = db.query(Scout).filter(Scout.id == scout_id).first()

    if not scout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="スカウトが見つかりません"
        )

    # アクセス権限チェック
    if current_user.role == UserRole.SEEKER and scout.seeker_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このスカウトにアクセスする権限がありません"
        )
    elif current_user.role == UserRole.EMPLOYER and scout.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このスカウトにアクセスする権限がありません"
        )

    # 求職者が閲覧した場合、既読にする
    if current_user.role == UserRole.SEEKER and scout.status == ScoutStatus.NEW:
        scout.status = ScoutStatus.READ
        scout.read_at = datetime.utcnow()
        db.commit()
        db.refresh(scout)

    employer = db.query(User).filter(User.id == scout.employer_id).first()
    seeker = db.query(User).filter(User.id == scout.seeker_id).first()

    return scout_to_detail(scout, current_user.role.value, employer, seeker)


@router.put("/{scout_id}", response_model=ScoutDetail)
async def update_scout(
    scout_id: str,
    request: ScoutUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    スカウトステータスを更新

    Args:
        scout_id: スカウトID
        request: 更新内容
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        更新後のスカウト
    """
    scout = db.query(Scout).filter(Scout.id == scout_id).first()

    if not scout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="スカウトが見つかりません"
        )

    # アクセス権限チェック（求職者のみが更新可能）
    if current_user.role != UserRole.SEEKER or scout.seeker_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このスカウトを更新する権限がありません"
        )

    # ステータスを更新
    try:
        old_status = scout.status
        scout.status = ScoutStatus(request.status)

        # 返信した場合は返信日時を記録
        if old_status != ScoutStatus.REPLIED and scout.status == ScoutStatus.REPLIED:
            scout.replied_at = datetime.utcnow()

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効なステータスです"
        )

    db.commit()
    db.refresh(scout)

    employer = db.query(User).filter(User.id == scout.employer_id).first()
    seeker = db.query(User).filter(User.id == scout.seeker_id).first()

    return scout_to_detail(scout, current_user.role.value, employer, seeker)
