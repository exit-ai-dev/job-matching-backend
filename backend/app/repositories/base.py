# app/repositories/base.py
"""
ベースリポジトリクラス
"""
from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.orm import Session
from app.db.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """汎用リポジトリ基底クラス"""

    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: str) -> Optional[T]:
        """IDで取得"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """全件取得（ページネーション付き）"""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, entity: T) -> T:
        """作成"""
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: T) -> T:
        """更新"""
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: T) -> bool:
        """削除"""
        self.db.delete(entity)
        self.db.commit()
        return True

    def count(self) -> int:
        """件数取得"""
        return self.db.query(self.model).count()
