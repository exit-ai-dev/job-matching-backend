# init_db.py
"""
データベース初期化スクリプト
"""
from app.db.base import Base
from app.db.session import get_engine
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.models.scout import Scout

def init_db():
    """
    データベーステーブルを作成
    """
    print("Creating database tables...")
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    print(f"\nCreated tables: {list(Base.metadata.tables.keys())}")


if __name__ == "__main__":
    init_db()
