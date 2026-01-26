"""
データベース接続設定
完全なDBスキーマ(db_schema_complete.sql)に対応

Azure Database for PostgreSQL 対応:
- DATABASE_URL または DB_* 環境変数で接続
- DB_SSLMODE (例: require) をサポート

使い方（推奨）:
  DATABASE_URL="postgresql://<user>:<pass>@<host>:5432/<db>?sslmode=require"

または従来どおり:
  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_SSLMODE
"""

import os
from typing import Generator, Optional, Dict, Any

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    """データベース設定クラス"""

    def __init__(self):
        # 推奨: Azure では DATABASE_URL（接続文字列）を使う
        self.database_url = os.getenv("DATABASE_URL")

        # 従来方式（分割環境変数）
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.dbname = os.getenv("DB_NAME", "jobmatch")
        self.user = os.getenv("DB_USER", "devuser")
        self.password = os.getenv("DB_PASSWORD", "devpass")

        # Azure PostgreSQL は SSL 必須が一般的なので、既定を require に寄せる
        # ローカルが困る場合は DB_SSLMODE=prefer を設定
        self.sslmode = os.getenv("DB_SSLMODE", "prefer")

        # 任意: 接続タイムアウト
        self.connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))

    def get_connection(self):
        """psycopg2 接続を返す"""
        # 1) DATABASE_URL があれば最優先
        if self.database_url:
            # DATABASE_URL の中に sslmode が無い場合だけ付与（重複指定回避）
            url = self.database_url
            if "sslmode=" not in url and self.sslmode:
                sep = "&" if "?" in url else "?"
                url = f"{url}{sep}sslmode={self.sslmode}"
            return psycopg2.connect(url, connect_timeout=self.connect_timeout)

        # 2) 分割環境変数方式
        params: Dict[str, Any] = {
            "host": self.host,
            "port": self.port,
            "dbname": self.dbname,
            "user": self.user,
            "password": self.password,
            "connect_timeout": self.connect_timeout,
        }
        if self.sslmode:
            params["sslmode"] = self.sslmode  # prefer / require / verify-full など

        return psycopg2.connect(**params)


db_config = DatabaseConfig()


def get_db_conn():
    """データベース接続を取得"""
    try:
        return db_config.get_connection()
    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")
        raise


def get_db_cursor(conn, use_dict_cursor: bool = False):
    """データベースカーソルを取得"""
    if use_dict_cursor:
        return conn.cursor(cursor_factory=RealDictCursor)
    return conn.cursor()


def get_db() -> Generator:
    """FastAPI依存性注入用のデータベース接続"""
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
        print(f"✅ データベース接続成功: PostgreSQL {version[0]}")
        return True
    except Exception as e:
        print(f"❌ データベース接続失敗: {e}")
        return False


if __name__ == "__main__":
    test_connection()
