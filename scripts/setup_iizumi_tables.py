#!/usr/bin/env python3
"""
Iizumiロジック移植用テーブルセットアップスクリプト

使用方法:
    python scripts/setup_iizumi_tables.py

環境変数:
    DATABASE_URL: PostgreSQL接続文字列
"""

import os
import sys
from urllib.parse import urlparse

# backendディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("Error: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)


def get_connection():
    """データベース接続を取得"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)

    parsed = urlparse(database_url)

    conn_params = {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "dbname": parsed.path.lstrip("/"),
        "user": parsed.username,
        "password": parsed.password,
        "sslmode": "require"
    }

    return psycopg2.connect(**conn_params)


def run_migration():
    """マイグレーションを実行"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        print("\n=== Iizumi Migration Start ===\n")

        # 1. chat_sessions テーブル作成
        print("1. Creating chat_sessions table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                session_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id
            ON chat_sessions(user_id)
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at
            ON chat_sessions(updated_at)
        """)
        print("   chat_sessions: OK")

        # 2. user_preferences_profile テーブル作成
        print("2. Creating user_preferences_profile table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences_profile (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(36) UNIQUE NOT NULL,
                job_title VARCHAR(200),
                location_prefecture VARCHAR(50),
                location_city VARCHAR(100),
                salary_min INTEGER,
                salary_max INTEGER,
                remote_work_preference VARCHAR(50),
                employment_type VARCHAR(50),
                industry_preferences JSONB,
                work_hours_preference VARCHAR(100),
                company_size_preference VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_preferences_profile_user_id
            ON user_preferences_profile(user_id)
        """)
        print("   user_preferences_profile: OK")

        # 3. jobs テーブル確認
        print("3. Checking jobs table...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM pg_tables WHERE tablename = 'jobs'
            )
        """)
        if cur.fetchone()[0]:
            print("   jobs table: EXISTS")
        else:
            print("   WARNING: jobs table does not exist!")

        # 4. テーブル状況確認
        print("\n4. Table statistics:")

        cur.execute("SELECT COUNT(*) FROM chat_sessions")
        chat_count = cur.fetchone()[0]
        print(f"   chat_sessions: {chat_count} rows")

        cur.execute("SELECT COUNT(*) FROM user_preferences_profile")
        pref_count = cur.fetchone()[0]
        print(f"   user_preferences_profile: {pref_count} rows")

        cur.execute("SELECT COUNT(*) FROM jobs WHERE UPPER(status::text) = 'PUBLISHED'")
        jobs_count = cur.fetchone()[0]
        print(f"   jobs (published): {jobs_count} rows")

        conn.commit()
        print("\n=== Migration Complete ===\n")

    except Exception as e:
        conn.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def cleanup_tables():
    """テーブル削除（ロールバック用）"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        print("\n=== Cleanup Start ===\n")

        cur.execute("DROP TABLE IF EXISTS chat_sessions CASCADE")
        print("Dropped: chat_sessions")

        # user_preferences_profile は他の機能でも使うため削除しない
        # cur.execute("DROP TABLE IF EXISTS user_preferences_profile CASCADE")

        conn.commit()
        print("\n=== Cleanup Complete ===\n")

    except Exception as e:
        conn.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Iizumi Migration Script")
    parser.add_argument("--cleanup", action="store_true", help="Drop tables (rollback)")
    args = parser.parse_args()

    if args.cleanup:
        cleanup_tables()
    else:
        run_migration()
