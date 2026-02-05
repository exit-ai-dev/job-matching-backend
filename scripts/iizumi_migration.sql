-- =============================================================================
-- iizumi_migration.sql
-- Iizumiロジック移植用のデータベースマイグレーションスクリプト
--
-- 実行方法:
--   psql -h <host> -U <user> -d <database> -f iizumi_migration.sql
-- または Azure Data Studio / pgAdmin で実行
-- =============================================================================

BEGIN;

-- =============================================================================
-- 1. chat_sessions テーブル（新規作成）
-- =============================================================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'chat_sessions') THEN
        CREATE TABLE chat_sessions (
            session_id VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            session_data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
        CREATE INDEX idx_chat_sessions_updated_at ON chat_sessions(updated_at);

        RAISE NOTICE 'chat_sessions テーブルを作成しました';
    ELSE
        RAISE NOTICE 'chat_sessions テーブルは既に存在します';
    END IF;
END $$;

-- =============================================================================
-- 2. user_preferences_profile テーブル（新規作成 or 確認）
-- =============================================================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'user_preferences_profile') THEN
        CREATE TABLE user_preferences_profile (
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
        );

        CREATE INDEX idx_user_preferences_profile_user_id ON user_preferences_profile(user_id);

        RAISE NOTICE 'user_preferences_profile テーブルを作成しました';
    ELSE
        RAISE NOTICE 'user_preferences_profile テーブルは既に存在します';
    END IF;
END $$;

-- =============================================================================
-- 3. jobs テーブルの確認（Iizumiロジックで使用）
-- =============================================================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'jobs') THEN
        RAISE EXCEPTION 'jobs テーブルが存在しません。先にメインのマイグレーションを実行してください。';
    ELSE
        RAISE NOTICE 'jobs テーブルが存在することを確認しました';
    END IF;
END $$;

-- =============================================================================
-- 4. jobs テーブルに必要なカラムがあるか確認
-- =============================================================================
DO $$
BEGIN
    -- title カラム確認
    IF NOT EXISTS (
        SELECT FROM information_schema.columns
        WHERE table_name = 'jobs' AND column_name = 'title'
    ) THEN
        RAISE EXCEPTION 'jobs.title カラムが存在しません';
    END IF;

    -- location カラム確認
    IF NOT EXISTS (
        SELECT FROM information_schema.columns
        WHERE table_name = 'jobs' AND column_name = 'location'
    ) THEN
        RAISE EXCEPTION 'jobs.location カラムが存在しません';
    END IF;

    -- status カラム確認
    IF NOT EXISTS (
        SELECT FROM information_schema.columns
        WHERE table_name = 'jobs' AND column_name = 'status'
    ) THEN
        RAISE EXCEPTION 'jobs.status カラムが存在しません';
    END IF;

    RAISE NOTICE 'jobs テーブルの必須カラムを確認しました';
END $$;

-- =============================================================================
-- 5. テスト用データの挿入（オプション）
-- =============================================================================
-- 開発環境でテスト用ユーザーの希望条件を追加する場合はコメントを外してください
/*
INSERT INTO user_preferences_profile (user_id, job_title, location_prefecture, salary_min)
VALUES
    ('test-user-001', 'デザイナー', '東京都', 400),
    ('test-user-002', 'エンジニア', '大阪府', 500)
ON CONFLICT (user_id) DO UPDATE SET
    job_title = EXCLUDED.job_title,
    location_prefecture = EXCLUDED.location_prefecture,
    salary_min = EXCLUDED.salary_min;
*/

-- =============================================================================
-- 6. マイグレーション完了確認
-- =============================================================================
DO $$
DECLARE
    chat_count INTEGER;
    pref_count INTEGER;
    jobs_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO chat_count FROM chat_sessions;
    SELECT COUNT(*) INTO pref_count FROM user_preferences_profile;
    SELECT COUNT(*) INTO jobs_count FROM jobs WHERE status::text = 'published';

    RAISE NOTICE '';
    RAISE NOTICE '=== マイグレーション完了 ===';
    RAISE NOTICE 'chat_sessions: % 件', chat_count;
    RAISE NOTICE 'user_preferences_profile: % 件', pref_count;
    RAISE NOTICE 'jobs (published): % 件', jobs_count;
    RAISE NOTICE '=============================';
END $$;

COMMIT;

-- =============================================================================
-- ロールバック用（必要な場合のみ実行）
-- =============================================================================
/*
BEGIN;
DROP TABLE IF EXISTS chat_sessions CASCADE;
-- user_preferences_profile は他の機能でも使うため削除しない
COMMIT;
*/
