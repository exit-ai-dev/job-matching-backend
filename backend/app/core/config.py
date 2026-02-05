# app/core/config.py
"""
アプリケーション設定管理
Pydantic Settingsを使用して環境変数から設定を読み込む
"""
from typing import List
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定"""

    # アプリケーション情報
    app_name: str = "Job Matching API"
    app_version: str = "1.0.0"
    app_description: str = "AI求人マッチングシステムのバックエンドAPI"
    debug: bool = False
    env: str = Field(default="local", description="Deployment environment name")

    # サーバー設定
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS設定
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:5174,http://localhost:5175",
        validation_alias=AliasChoices("ALLOWED_ORIGINS", "CORS_ORIGINS"),
        description="Comma separated allowed origins"
    )
    cors_credentials: bool = True
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    )
    cors_headers: List[str] = Field(
        default=[
            "Accept",
            "Accept-Language",
            "Content-Type",
            "Authorization",
            "Origin",
            "X-Requested-With",
        ]
    )

    # OpenAI API設定
    openai_api_key: str = Field(default="", description="OpenAI API Key (optional for local dev)")
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_dimension: int = 1536

    # データベース設定（将来の拡張用）
    database_url: str = Field(
        default="sqlite:///./job_matching.db",
        description="Database connection URL"
    )

    # ファイルストレージ設定
    data_directory: str = "./data"
    conversations_directory: str = "./data/conversations"
    embeddings_directory: str = "./data/embeddings"
    jobs_file: str = "./data/jobs.json"

    # ロギング設定
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # マッチング設定
    default_top_k: int = 10
    matching_threshold: float = 0.5

    # セキュリティ設定（将来の拡張用）
    secret_key: str = Field(
        default="your-secret-key-here",
        description="Secret key for JWT tokens"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # GMOペイメント設定
    gmo_site_id: str = Field(default="", description="GMO Site ID")
    gmo_site_pass: str = Field(default="", description="GMO Site Password")
    gmo_shop_id: str = Field(default="", description="GMO Shop ID")
    gmo_shop_pass: str = Field(default="", description="GMO Shop Password")
    gmo_api_url: str = Field(
        default="https://pt01.mul-pay.jp",
        description="GMO API URL (pt01 for test, p01 for production)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# シングルトンインスタンス
_settings: Settings | None = None


def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
