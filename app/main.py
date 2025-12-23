# app/main.py
"""
Job Matching Backend API
すべてのAPIエンドポイントを統合したメインアプリケーション
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.endpoints import auth, jobs, matching, applications, scouts, conversation, users, employer

settings = get_settings()

# FastAPIアプリケーション初期化
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
)

# CORSミドルウェアを追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
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
