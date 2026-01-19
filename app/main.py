# app/main.py
"""
Job Matching Backend API
すべてのAPIエンドポイントを統合したメインアプリケーション
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.endpoints import auth, jobs, matching, applications, scouts, conversation, users, employer

logger = logging.getLogger(__name__)

settings = get_settings()

# FastAPIアプリケーション初期化
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
)

# CORSミドルウェアを追加
# Azure環境変数のバグ対応: ハードコーディングで設定
cors_origins_list = [
    "https://gray-sky-0b7ccbf00.6.azurestaticapps.net",  # Azure Static Web Apps (本番)
    "http://localhost:5173",  # ローカル開発
    "http://localhost:5174",  # ローカル開発（代替ポート）
    "http://localhost:5175",  # ローカル開発（代替ポート）
]

# 環境変数からも読み込む（バックアップ）
try:
    env_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    cors_origins_list.extend(env_origins)
    # 重複を削除
    cors_origins_list = list(set(cors_origins_list))
except Exception as e:
    logger.warning(f"Failed to load CORS origins from environment: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# APIルーターを登録
app.include_router(auth.router, prefix="/api/auth", tags=["認証"])
app.include_router(users.router, prefix="/api/users", tags=["ユーザー"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["求人"])
app.include_router(matching.router, prefix="/api/matching", tags=["マッチング"])
app.include_router(applications.router, prefix="/api/applications", tags=["応募"])
app.include_router(scouts.router, prefix="/api/scouts", tags=["スカウト"])
app.include_router(conversation.router, prefix="/api/conversation", tags=["会話"])
app.include_router(employer.router, prefix="/api/employer", tags=["企業"])


@app.on_event("startup")
async def startup_event():
    """起動時の処理"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.env}")
    logger.info(f"CORS Origins: {cors_origins_list}")
    logger.info(f"Debug mode: {settings.debug}")

    # Run database migrations
    try:
        logger.info("Running database migrations...")
        from app.db.session import SessionLocal
        from sqlalchemy import text

        db = SessionLocal()
        try:
            # Check and add LINE fields if they don't exist
            check_sql = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'users'
                AND column_name IN ('line_display_name', 'line_picture_url', 'line_email')
            """)

            existing_columns = db.execute(check_sql).fetchall()
            existing_column_names = [row[0] for row in existing_columns]

            if 'line_display_name' not in existing_column_names:
                logger.info("Adding line_display_name column...")
                db.execute(text("ALTER TABLE users ADD COLUMN line_display_name VARCHAR(100) NULL"))

            if 'line_picture_url' not in existing_column_names:
                logger.info("Adding line_picture_url column...")
                db.execute(text("ALTER TABLE users ADD COLUMN line_picture_url VARCHAR(500) NULL"))

            if 'line_email' not in existing_column_names:
                logger.info("Adding line_email column...")
                db.execute(text("ALTER TABLE users ADD COLUMN line_email VARCHAR(255) NULL"))

            db.commit()
            logger.info("Database migrations completed successfully")
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            db.rollback()
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Job Matching API",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}


@app.get("/debug/config")
async def debug_config():
    """デバッグ用: 現在の設定を確認"""
    return {
        "cors_origins": settings.cors_origins,
        "cors_origins_list": settings.cors_origins.split(","),
        "cors_credentials": settings.cors_credentials,
        "cors_methods": settings.cors_methods,
        "cors_headers": settings.cors_headers,
        "env": settings.env,
    }
