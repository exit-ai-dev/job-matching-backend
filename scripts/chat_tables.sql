-- chat_tables.sql
-- Iizumiロジック移植用のテーブル作成スクリプト

-- =============================================================================
-- chat_sessions テーブル（チャットセッション管理）
-- =============================================================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at);

-- コメント追加
COMMENT ON TABLE chat_sessions IS 'チャットセッション管理（Iizumiロジック用）';
COMMENT ON COLUMN chat_sessions.session_id IS 'セッションID（UUID）';
COMMENT ON COLUMN chat_sessions.user_id IS 'ユーザーID';
COMMENT ON COLUMN chat_sessions.session_data IS 'セッションデータ（JSONB形式）';

-- =============================================================================
-- user_preferences_profile テーブル（ユーザー希望条件）
-- 既に存在する場合はスキップ
-- =============================================================================
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
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_user_preferences_profile_user_id ON user_preferences_profile(user_id);

-- コメント追加
COMMENT ON TABLE user_preferences_profile IS 'ユーザー希望条件プロフィール（Step2情報）';
COMMENT ON COLUMN user_preferences_profile.job_title IS '希望職種';
COMMENT ON COLUMN user_preferences_profile.location_prefecture IS '希望勤務地（都道府県）';
COMMENT ON COLUMN user_preferences_profile.salary_min IS '希望最低年収（万円）';

-- =============================================================================
-- 動作確認
-- =============================================================================
-- SELECT COUNT(*) FROM chat_sessions;
-- SELECT COUNT(*) FROM user_preferences_profile;
