# app/services/auth_service.py
"""
認証サービス
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.core.config import get_settings

# 設定から取得
settings = get_settings()
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# パスワードハッシュ設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """認証サービス"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """パスワードを検証"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """パスワードをハッシュ化"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(user_id: str) -> Tuple[str, int]:
        """アクセストークンを作成"""
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta
        to_encode = {"sub": user_id, "exp": expire}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt, ACCESS_TOKEN_EXPIRE_MINUTES * 60

    def register(
        self,
        email: str,
        password: str,
        name: str,
        role: str,
        company_name: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> User:
        """ユーザー登録"""
        # メールアドレスの重複チェック
        if self.user_repo.email_exists(email):
            raise ValueError("このメールアドレスは既に登録されています")

        # 企業の場合、会社名は必須
        if role == "employer" and not company_name:
            raise ValueError("企業の場合、会社名は必須です")

        # ユーザー作成
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=self.get_password_hash(password),
            name=name,
            role=UserRole.EMPLOYER if role == "employer" else UserRole.SEEKER,
            company_name=company_name,
            industry=industry,
            profile_completion="20",
        )

        return self.user_repo.create(user)

    def login(self, email: str, password: str) -> Optional[User]:
        """ログイン"""
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None

        # 最終ログイン日時を更新
        user.last_login_at = datetime.utcnow()
        self.db.commit()

        return user

    def register_with_line(
        self,
        line_user_id: str,
        line_display_name: str,
        name: str,
        role: str,
        line_picture_url: Optional[str] = None,
        line_email: Optional[str] = None,
        company_name: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> User:
        """LINE連携で新規登録"""
        # LINE IDの重複チェック
        existing = self.user_repo.get_by_line_user_id(line_user_id)
        if existing:
            raise ValueError("このLINEアカウントは既に登録されています")

        # 企業の場合、会社名は必須
        if role == "employer" and not company_name:
            raise ValueError("企業の場合、会社名は必須です")

        # ダミーパスワードを生成（LINE認証なのでパスワード不要だが、DBにはハッシュが必要）
        dummy_password = str(uuid.uuid4())

        user = User(
            id=str(uuid.uuid4()),
            email=line_email or f"{line_user_id}@line.placeholder",
            password_hash=self.get_password_hash(dummy_password),
            name=name,
            role=UserRole.EMPLOYER if role == "employer" else UserRole.SEEKER,
            line_user_id=line_user_id,
            line_display_name=line_display_name,
            line_picture_url=line_picture_url,
            line_email=line_email,
            line_linked_at=datetime.utcnow(),
            company_name=company_name,
            industry=industry,
            profile_completion="20",
        )

        return self.user_repo.create(user)

    def login_with_line(self, line_user_id: str) -> Optional[User]:
        """LINEでログイン"""
        user = self.user_repo.get_by_line_user_id(line_user_id)
        if not user or not user.is_active:
            return None

        # 最終ログイン日時を更新
        user.last_login_at = datetime.utcnow()
        self.db.commit()

        return user

    def link_line(
        self,
        user: User,
        line_user_id: str,
        line_display_name: str,
        line_picture_url: Optional[str] = None,
        line_email: Optional[str] = None,
    ) -> User:
        """既存アカウントにLINEを連携"""
        # 既に連携済みか確認
        if user.line_user_id:
            raise ValueError("既にLINEアカウントが連携されています")

        # 他のユーザーが使用していないか確認
        existing = self.user_repo.get_by_line_user_id(line_user_id)
        if existing:
            raise ValueError("このLINEアカウントは既に他のユーザーに連携されています")

        user.line_user_id = line_user_id
        user.line_display_name = line_display_name
        user.line_picture_url = line_picture_url
        user.line_email = line_email
        user.line_linked_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(user)

        return user
