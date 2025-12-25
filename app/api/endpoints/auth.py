# app/api/endpoints/auth.py
"""
認証API
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
import uuid
import json
from datetime import datetime, timedelta
import bcrypt
from jose import jwt, JWTError

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    LineLinkRequest,
    AuthResponse,
    UserResponse,
    TokenResponse,
)
from app.models.user import User, UserRole
from app.db.session import get_db
from app.core.config import get_settings
from app.core.dependencies import CurrentUser

router = APIRouter()
settings = get_settings()


def create_access_token(user_id: str) -> tuple[str, int]:
    """
    アクセストークンを作成

    Args:
        user_id: ユーザーID

    Returns:
        トークンと有効期限（秒）
    """
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.utcnow() + expires_delta

    to_encode = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt, settings.access_token_expire_minutes * 60


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワード検証"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """パスワードをハッシュ化"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    ユーザー登録

    Args:
        request: 登録リクエスト
        db: データベースセッション

    Returns:
        認証レスポンス（ユーザー情報とトークン）
    """
    # メールアドレスの重複チェック
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このメールアドレスは既に登録されています"
        )

    # 企業登録の場合、companyNameが必須
    if request.role == "employer" and not request.companyName:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="企業名は必須です"
        )

    # ユーザーを作成
    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        password_hash=get_password_hash(request.password),
        name=request.name,
        role=UserRole(request.role),
        company_name=request.companyName if request.role == "employer" else None,
        industry=request.industry if request.role == "employer" else None,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # トークンを生成
    access_token, expires_in = create_access_token(user.id)

    # レスポンスを作成
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        lineLinked=user.line_user_id is not None,
        profileCompletion=user.profile_completion or "0",
        createdAt=user.created_at,
        companyName=user.company_name,
        industry=user.industry,
    )

    token_response = TokenResponse(
        accessToken=access_token,
        expiresIn=expires_in
    )

    return AuthResponse(user=user_response, token=token_response)


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    ログイン

    Args:
        request: ログインリクエスト
        db: データベースセッション

    Returns:
        認証レスポンス（ユーザー情報とトークン）
    """
    # ユーザーを検索
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このアカウントは無効化されています"
        )

    # 最終ログイン時刻を更新
    user.last_login_at = datetime.utcnow()
    db.commit()

    # トークンを生成
    access_token, expires_in = create_access_token(user.id)

    # スキルをJSON解析
    skills = None
    if user.skills:
        try:
            skills = json.loads(user.skills)
        except:
            pass

    # レスポンスを作成
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        lineLinked=user.line_user_id is not None,
        profileCompletion=user.profile_completion or "0",
        createdAt=user.created_at,
        skills=skills,
        experienceYears=user.experience_years,
        desiredSalaryMin=user.desired_salary_min,
        desiredSalaryMax=user.desired_salary_max,
        desiredLocation=user.desired_location,
        desiredEmploymentType=user.desired_employment_type,
        companyName=user.company_name,
        industry=user.industry,
        companySize=user.company_size,
        companyDescription=user.company_description,
    )

    token_response = TokenResponse(
        accessToken=access_token,
        expiresIn=expires_in
    )

    return AuthResponse(user=user_response, token=token_response)


@router.post("/line/link", response_model=AuthResponse)
async def link_line(
    request: LineLinkRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """
    LINE連携（既存アカウントとLINEアカウントを紐付け）

    Args:
        request: LINE連携リクエスト
        current_user: 認証済みユーザー
        db: データベースセッション

    Returns:
        更新されたユーザー情報
    """
    # LINE IDが既に他のアカウントで使用されていないか確認
    existing_line_user = db.query(User).filter(
        User.line_user_id == request.lineUserId,
        User.id != current_user.id
    ).first()

    if existing_line_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このLINEアカウントは既に他のアカウントと紐付けられています"
        )

    # LINE情報を更新
    current_user.line_user_id = request.lineUserId
    current_user.line_display_name = request.lineDisplayName
    current_user.line_picture_url = request.linePictureUrl
    current_user.line_email = request.lineEmail

    db.commit()
    db.refresh(current_user)

    # レスポンスを作成
    skills = None
    if current_user.skills:
        try:
            skills = json.loads(current_user.skills)
        except:
            pass

    user_response = UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        lineLinked=True,
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
        lineUserId=current_user.line_user_id,
        lineDisplayName=current_user.line_display_name,
        linePictureUrl=current_user.line_picture_url,
        lineEmail=current_user.line_email,
    )

    access_token, expires_in = create_access_token(current_user.id)

    token_response = TokenResponse(
        accessToken=access_token,
        expiresIn=expires_in
    )

    return AuthResponse(user=user_response, token=token_response)


@router.post("/line/login", response_model=AuthResponse)
async def login_with_line(
    request: LineLinkRequest,
    db: Session = Depends(get_db),
):
    """
    LINEログイン（LINEアカウントで既存アカウントにログイン）

    Args:
        request: LINE連携リクエスト
        db: データベースセッション

    Returns:
        認証レスポンス
    """
    # LINE IDでユーザーを検索
    user = db.query(User).filter(User.line_user_id == request.lineUserId).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="このLINEアカウントは登録されていません。先にアカウントを作成してください"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このアカウントは無効化されています"
        )

    # 最終ログイン時刻を更新
    user.last_login_at = datetime.utcnow()

    # LINE情報を更新（名前や画像が変更されている可能性があるため）
    user.line_display_name = request.lineDisplayName
    user.line_picture_url = request.linePictureUrl
    if request.lineEmail:
        user.line_email = request.lineEmail

    db.commit()
    db.refresh(user)

    # レスポンスを作成
    skills = None
    if user.skills:
        try:
            skills = json.loads(user.skills)
        except:
            pass

    user_response = UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        lineLinked=True,
        profileCompletion=user.profile_completion or "0",
        createdAt=user.created_at,
        skills=skills,
        experienceYears=user.experience_years,
        desiredSalaryMin=user.desired_salary_min,
        desiredSalaryMax=user.desired_salary_max,
        desiredLocation=user.desired_location,
        desiredEmploymentType=user.desired_employment_type,
        companyName=user.company_name,
        industry=user.industry,
        companySize=user.company_size,
        companyDescription=user.company_description,
        lineUserId=user.line_user_id,
        lineDisplayName=user.line_display_name,
        linePictureUrl=user.line_picture_url,
        lineEmail=user.line_email,
    )

    access_token, expires_in = create_access_token(user.id)

    token_response = TokenResponse(
        accessToken=access_token,
        expiresIn=expires_in
    )

    return AuthResponse(user=user_response, token=token_response)


@router.get("/me", response_model=AuthResponse)
async def get_current_user_info(current_user: CurrentUser):
    """
    現在のユーザー情報を取得

    Args:
        current_user: 認証済みユーザー

    Returns:
        ユーザー情報とトークン情報
    """
    # スキルをJSON解析
    skills = None
    if current_user.skills:
        try:
            skills = json.loads(current_user.skills)
        except:
            pass

    # レスポンスを作成
    user_response = UserResponse(
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
        lineUserId=current_user.line_user_id,
        lineDisplayName=current_user.line_display_name,
        linePictureUrl=current_user.line_picture_url,
        lineEmail=current_user.line_email,
    )

    # 新しいトークンを生成（有効期限を延長）
    access_token, expires_in = create_access_token(current_user.id)

    token_response = TokenResponse(
        accessToken=access_token,
        expiresIn=expires_in
    )

    return AuthResponse(user=user_response, token=token_response)


@router.post("/logout")
async def logout():
    """
    ログアウト

    Returns:
        成功メッセージ
    """
    # JWTトークンを使用しているため、クライアント側でトークンを削除するだけでOK
    return {"message": "ログアウトしました"}
