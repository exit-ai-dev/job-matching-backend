#!/usr/bin/env python
"""
データベース初期化スクリプト
Azure PostgreSQLまたはローカルSQLiteにテーブルを作成します

使用方法:
  python scripts/init_db.py

環境変数:
  DATABASE_URL: データベース接続URL (未設定の場合はSQLiteを使用)
"""
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import get_engine
from app.db.base import Base

# すべてのモデルをインポート（テーブル作成に必要）
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.models.scout import Scout
from app.models.resume import Resume
from app.models.company import Company
from app.models.company_profile import CompanyProfile
from app.models.user_preferences import UserPreferencesProfile
from app.models.conversation import ConversationSession, ConversationLog, ChatSession


def init_database():
    """データベースを初期化（テーブル作成）"""
    print("データベース初期化を開始します...")

    engine = get_engine()
    print(f"接続先: {engine.url}")

    # テーブルを作成
    print("テーブルを作成中...")
    Base.metadata.create_all(bind=engine)

    # 作成されたテーブルを確認
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"\n作成されたテーブル ({len(tables)}個):")
    for table in tables:
        columns = [col['name'] for col in inspector.get_columns(table)]
        print(f"  - {table}: {len(columns)} columns")

    print("\nデータベース初期化が完了しました！")


if __name__ == "__main__":
    init_database()
