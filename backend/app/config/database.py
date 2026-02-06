"""
データベース接続設定（psycopg2ベース）
Iizumiロジック移植用
"""

import os
from typing import Generator, Optional
from urllib.parse import urlparse
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """データベース設定クラス"""

    def __init__(self):
        # DATABASE_URLから接続情報を抽出
        database_url = os.getenv("DATABASE_URL", "")

        if database_url:
            parsed = urlparse(database_url)
            self.host = parsed.hostname or "localhost"
            self.port = parsed.port or 5432
            self.dbname = parsed.path.lstrip("/") if parsed.path else "etdev"
            self.user = parsed.username or "etdev"
            self.password = parsed.password or ""
            # sslmodeをクエリパラメータから取得
            self.sslmode = "require"
            if parsed.query:
                params = dict(p.split("=") for p in parsed.query.split("&") if "=" in p)
                self.sslmode = params.get("sslmode", "require")
        else:
            # フォールバック: 個別の環境変数
            self.host = os.getenv("DB_HOST", "localhost")
            self.port = int(os.getenv("DB_PORT", "5432"))
            self.dbname = os.getenv("DB_NAME", "etdev")
            self.user = os.getenv("DB_USER", "etdev")
            self.password = os.getenv("DB_PASSWORD", "")
            self.sslmode = os.getenv("DB_SSLMODE", "require")

    def get_connection_params(self) -> dict:
        """接続パラメータを辞書で返す"""
        return {
            "host": self.host,
            "port": self.port,
            "dbname": self.dbname,
            "user": self.user,
            "password": self.password,
            "sslmode": self.sslmode
        }


db_config = DatabaseConfig()


def get_db_conn():
    """
    データベース接続を取得

    Returns:
        psycopg2.connection: データベース接続オブジェクト
    """
    try:
        conn = psycopg2.connect(**db_config.get_connection_params())
        return conn
    except Exception as e:
        logger.error(f"データベース接続エラー: {e}")
        raise


def get_db_cursor(conn, use_dict_cursor: bool = False):
    """
    データベースカーソルを取得

    Args:
        conn: データベース接続オブジェクト
        use_dict_cursor: True の場合、RealDictCursor を使用

    Returns:
        カーソルオブジェクト
    """
    if use_dict_cursor:
        return conn.cursor(cursor_factory=RealDictCursor)
    return conn.cursor()


def get_db() -> Generator:
    """
    FastAPI依存性注入用のデータベース接続

    Yields:
        データベース接続
    """
    conn = get_db_conn()
    try:
        yield conn
    finally:
        conn.close()


def test_connection() -> bool:
    """データベース接続をテスト"""
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        cur.close()
        conn.close()
        logger.info(f"データベース接続成功: PostgreSQL {version[0]}")
        return True
    except Exception as e:
        logger.error(f"データベース接続失敗: {e}")
        return False
