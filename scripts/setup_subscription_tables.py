#!/usr/bin/env python3
"""
サブスクリプション関連テーブルの作成とシードデータ投入スクリプト

Azure Database for PostgreSQL への接続に対応

使用方法:
    # 環境変数を設定してから実行
    export DATABASE_URL="postgresql://user:password@host:5432/dbname?sslmode=require"
    python scripts/setup_subscription_tables.py

    # または、接続情報を直接指定
    python scripts/setup_subscription_tables.py --host your-server.postgres.database.azure.com \
        --database job_matching --user admin@your-server --password yourpassword
"""

import argparse
import os
import uuid
import json
from datetime import datetime

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("psycopg2がインストールされていません。以下のコマンドでインストールしてください:")
    print("  pip install psycopg2-binary")
    exit(1)


# =============================================================================
# テーブル作成SQL
# =============================================================================

CREATE_SUBSCRIPTION_PLANS_TABLE = """
CREATE TABLE IF NOT EXISTS subscription_plans (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    user_role VARCHAR(20) NOT NULL,
    tier VARCHAR(30) NOT NULL,
    price_jpy INTEGER NOT NULL DEFAULT 0,
    features TEXT,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
"""

CREATE_SUBSCRIPTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS subscriptions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id VARCHAR(36) NOT NULL REFERENCES subscription_plans(id),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    gmo_member_id VARCHAR(100),
    gmo_subscription_id VARCHAR(100) UNIQUE,
    current_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
"""

CREATE_USAGE_TRACKING_TABLE = """
CREATE TABLE IF NOT EXISTS usage_tracking (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    ai_chat_count INTEGER NOT NULL DEFAULT 0,
    application_count INTEGER NOT NULL DEFAULT 0,
    scout_count INTEGER NOT NULL DEFAULT 0,
    job_posting_count INTEGER NOT NULL DEFAULT 0,
    candidate_view_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id);
"""

CREATE_PAYMENT_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS payment_history (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id VARCHAR(36) REFERENCES subscriptions(id),
    gmo_order_id VARCHAR(100) UNIQUE,
    gmo_tran_id VARCHAR(100),
    amount_jpy INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'JPY',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_method VARCHAR(50),
    description VARCHAR(500),
    error_message TEXT,
    receipt_url VARCHAR(500),
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_payment_history_user_id ON payment_history(user_id);
"""

# usersテーブルへのカラム追加
ALTER_USERS_TABLE = """
DO $$
BEGIN
    -- gmo_member_id カラムを追加
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'gmo_member_id') THEN
        ALTER TABLE users ADD COLUMN gmo_member_id VARCHAR(100) UNIQUE;
        CREATE INDEX idx_users_gmo_member_id ON users(gmo_member_id);
    END IF;

    -- subscription_tier カラムを追加
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'subscription_tier') THEN
        ALTER TABLE users ADD COLUMN subscription_tier VARCHAR(50) NOT NULL DEFAULT 'free';
    END IF;
END $$;
"""


# =============================================================================
# シードデータ
# =============================================================================

SUBSCRIPTION_PLANS_SEED = [
    # 求職者向けプラン
    {
        "id": str(uuid.uuid4()),
        "name": "seeker_free",
        "display_name": "フリープラン",
        "user_role": "seeker",
        "tier": "seeker_free",
        "price_jpy": 0,
        "features": json.dumps({
            "ai_chat_limit": 0,
            "application_limit": 5
        }),
        "description": "基本的な求人閲覧と月5件までの応募が可能",
        "display_order": 1,
        "is_active": True
    },
    {
        "id": str(uuid.uuid4()),
        "name": "seeker_standard",
        "display_name": "スタンダードプラン",
        "user_role": "seeker",
        "tier": "seeker_standard",
        "price_jpy": 980,
        "features": json.dumps({
            "ai_chat_limit": 20,
            "application_limit": 30
        }),
        "description": "AIチャット20回/月、応募30件/月まで利用可能",
        "display_order": 2,
        "is_active": True
    },
    {
        "id": str(uuid.uuid4()),
        "name": "seeker_premium",
        "display_name": "プレミアムプラン",
        "user_role": "seeker",
        "tier": "seeker_premium",
        "price_jpy": 2980,
        "features": json.dumps({
            "ai_chat_limit": -1,  # -1 = 無制限
            "application_limit": -1
        }),
        "description": "AIチャット・応募ともに無制限",
        "display_order": 3,
        "is_active": True
    },
    # 企業向けプラン
    {
        "id": str(uuid.uuid4()),
        "name": "employer_free",
        "display_name": "フリープラン",
        "user_role": "employer",
        "tier": "employer_free",
        "price_jpy": 0,
        "features": json.dumps({
            "scout_limit": 3,
            "job_posting_limit": 1,
            "candidate_view_limit": 5
        }),
        "description": "求人1件、スカウト3件/月まで利用可能",
        "display_order": 1,
        "is_active": True
    },
    {
        "id": str(uuid.uuid4()),
        "name": "employer_starter",
        "display_name": "スタータープラン",
        "user_role": "employer",
        "tier": "employer_starter",
        "price_jpy": 9800,
        "features": json.dumps({
            "scout_limit": 15,
            "job_posting_limit": 3,
            "candidate_view_limit": 30
        }),
        "description": "求人3件、スカウト15件/月、候補者閲覧30件/月",
        "display_order": 2,
        "is_active": True
    },
    {
        "id": str(uuid.uuid4()),
        "name": "employer_business",
        "display_name": "ビジネスプラン",
        "user_role": "employer",
        "tier": "employer_business",
        "price_jpy": 29800,
        "features": json.dumps({
            "scout_limit": 50,
            "job_posting_limit": 10,
            "candidate_view_limit": 100
        }),
        "description": "求人10件、スカウト50件/月、候補者閲覧100件/月",
        "display_order": 3,
        "is_active": True
    },
]


# =============================================================================
# メイン処理
# =============================================================================

def get_connection(args):
    """データベース接続を取得"""
    # 環境変数からDATABASE_URLを取得
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        print(f"環境変数 DATABASE_URL を使用して接続します")
        return psycopg2.connect(database_url)

    # コマンドライン引数から接続
    if args.host and args.database and args.user and args.password:
        print(f"接続先: {args.host}/{args.database}")
        return psycopg2.connect(
            host=args.host,
            port=args.port,
            database=args.database,
            user=args.user,
            password=args.password,
            sslmode="require"  # Azure PostgreSQLはSSL必須
        )

    raise ValueError(
        "データベース接続情報が必要です。\n"
        "環境変数 DATABASE_URL を設定するか、--host, --database, --user, --password を指定してください。"
    )


def create_tables(cursor):
    """テーブルを作成"""
    print("\n=== テーブル作成 ===")

    tables = [
        ("subscription_plans", CREATE_SUBSCRIPTION_PLANS_TABLE),
        ("subscriptions", CREATE_SUBSCRIPTIONS_TABLE),
        ("usage_tracking", CREATE_USAGE_TRACKING_TABLE),
        ("payment_history", CREATE_PAYMENT_HISTORY_TABLE),
    ]

    for table_name, create_sql in tables:
        print(f"  Creating table: {table_name}...", end=" ")
        cursor.execute(create_sql)
        print("OK")

    # usersテーブルにカラム追加
    print(f"  Altering table: users...", end=" ")
    cursor.execute(ALTER_USERS_TABLE)
    print("OK")


def insert_seed_data(cursor):
    """シードデータを投入"""
    print("\n=== シードデータ投入 ===")

    # 既存データチェック
    cursor.execute("SELECT COUNT(*) FROM subscription_plans")
    count = cursor.fetchone()[0]

    if count > 0:
        print(f"  subscription_plans にはすでに {count} 件のデータがあります。")
        response = input("  上書きしますか？ (y/N): ").strip().lower()
        if response != 'y':
            print("  スキップしました。")
            return

        # 既存データを削除
        print("  既存データを削除中...", end=" ")
        cursor.execute("DELETE FROM payment_history")
        cursor.execute("DELETE FROM usage_tracking")
        cursor.execute("DELETE FROM subscriptions")
        cursor.execute("DELETE FROM subscription_plans")
        print("OK")

    # シードデータ投入
    insert_sql = """
        INSERT INTO subscription_plans
        (id, name, display_name, user_role, tier, price_jpy, features, description, display_order, is_active)
        VALUES (%(id)s, %(name)s, %(display_name)s, %(user_role)s, %(tier)s, %(price_jpy)s,
                %(features)s, %(description)s, %(display_order)s, %(is_active)s)
    """

    for plan in SUBSCRIPTION_PLANS_SEED:
        print(f"  Inserting: {plan['name']} ({plan['display_name']})...", end=" ")
        cursor.execute(insert_sql, plan)
        print("OK")

    print(f"\n  合計 {len(SUBSCRIPTION_PLANS_SEED)} 件のプランを投入しました。")


def verify_data(cursor):
    """データを検証"""
    print("\n=== データ検証 ===")

    cursor.execute("""
        SELECT name, display_name, user_role, price_jpy, features
        FROM subscription_plans
        ORDER BY user_role, display_order
    """)

    print("\n  登録されているプラン:")
    print("  " + "-" * 80)
    print(f"  {'プラン名':<20} {'表示名':<20} {'対象':<10} {'月額':<10} {'機能制限'}")
    print("  " + "-" * 80)

    for row in cursor.fetchall():
        name, display_name, user_role, price_jpy, features = row
        price_str = f"¥{price_jpy:,}" if price_jpy > 0 else "無料"
        print(f"  {name:<20} {display_name:<20} {user_role:<10} {price_str:<10} {features[:40]}...")

    print("  " + "-" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="サブスクリプション関連テーブルの作成とシードデータ投入"
    )
    parser.add_argument("--host", help="PostgreSQLホスト (例: your-server.postgres.database.azure.com)")
    parser.add_argument("--port", type=int, default=5432, help="ポート番号 (デフォルト: 5432)")
    parser.add_argument("--database", help="データベース名")
    parser.add_argument("--user", help="ユーザー名")
    parser.add_argument("--password", help="パスワード")
    parser.add_argument("--skip-seed", action="store_true", help="シードデータ投入をスキップ")
    parser.add_argument("--dry-run", action="store_true", help="実行せずにSQLを表示のみ")

    args = parser.parse_args()

    if args.dry_run:
        print("=== DRY RUN: 実行されるSQL ===\n")
        print("-- テーブル作成")
        print(CREATE_SUBSCRIPTION_PLANS_TABLE)
        print(CREATE_SUBSCRIPTIONS_TABLE)
        print(CREATE_USAGE_TRACKING_TABLE)
        print(CREATE_PAYMENT_HISTORY_TABLE)
        print("\n-- usersテーブル変更")
        print(ALTER_USERS_TABLE)
        print("\n-- シードデータ")
        for plan in SUBSCRIPTION_PLANS_SEED:
            print(f"-- {plan['name']}: {plan['display_name']} (¥{plan['price_jpy']})")
        return

    try:
        conn = get_connection(args)
        cursor = conn.cursor()

        print("データベースに接続しました。")

        # テーブル作成
        create_tables(cursor)

        # シードデータ投入
        if not args.skip_seed:
            insert_seed_data(cursor)

        # データ検証
        verify_data(cursor)

        # コミット
        conn.commit()
        print("\n✓ すべての変更をコミットしました。")

    except psycopg2.Error as e:
        print(f"\n✗ データベースエラー: {e}")
        if conn:
            conn.rollback()
        exit(1)
    except Exception as e:
        print(f"\n✗ エラー: {e}")
        exit(1)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("\nデータベース接続を閉じました。")


if __name__ == "__main__":
    main()
