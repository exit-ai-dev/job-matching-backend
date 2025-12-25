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
# 環境変数から CORS オリジンを取得し、空白を除去
cors_origins_list = [origin.strip() for origin in settings.cors_origins.split(",")]

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
