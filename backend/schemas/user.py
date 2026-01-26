"""
ユーザー関連のPydanticスキーマ
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime


class UserRegister(BaseModel):
    """ユーザー登録リクエスト"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    age: Optional[int] = Field(None, ge=18, le=100)
    gender: Optional[str] = None
    location: Optional[str] = None


class UserLogin(BaseModel):
    """ログインリクエスト"""
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """ユーザープロフィール"""
    user_id: str
    name: str
    email: str
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class UserProfileUpdate(BaseModel):
    """プロフィール更新リクエスト"""
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=100)
    gender: Optional[str] = None
    location: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserPreferencesUpdate(BaseModel):
    """ユーザー希望条件（Step2）更新リクエスト（DBスキーマ準拠）"""
    job_title: Optional[str] = None
    location_prefecture: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    remote_work_preference: Optional[str] = None

    # 追加情報は jsonb にまとめて保存する（DBに confirmed_preferences があるため）
    confirmed_preferences: Optional[Dict[str, Any]] = None


class Token(BaseModel):
    """認証トークン"""
    access_token: str
    token_type: str = "bearer"
    user_id: str


class TokenData(BaseModel):
    """トークンデータ"""
    user_id: Optional[str] = None
