-- ============================================================
-- データベーススキーマ定義（完全版）
-- プロジェクト: 求人マッチングプラットフォーム
-- データベース名: jobmatch
-- DBMS: PostgreSQL 14+
-- 作成日: 2024-12-24
-- ============================================================

-- ============================================================
-- 1. 拡張機能のインストール
-- ============================================================

-- UUID生成関数
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- pgvector（ベクトル類似度検索）
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- 2. テーブル作成
-- ============================================================

-- ------------------------------------------------------------
-- 2.1 personal_date（個人情報テーブル）
-- ------------------------------------------------------------
DROP TABLE IF EXISTS personal_date CASCADE;

CREATE TABLE personal_date (
    user_id INTEGER PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    user_name VARCHAR(100) NOT NULL,
    birth_day DATE,
    phone_number VARCHAR(20),
    address VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE personal_date IS 'ユーザーの基本情報テーブル';
COMMENT ON COLUMN personal_date.user_id IS 'ユーザー一意識別ID（自動採番）';
COMMENT ON COLUMN personal_date.email IS 'メールアドレス（ログイン用）';
COMMENT ON COLUMN personal_date.password_hash IS 'ハッシュ化されたパスワード';
COMMENT ON COLUMN personal_date.user_name IS 'ユーザー名';

-- ------------------------------------------------------------
-- 2.2 user_profile（ユーザープロファイルテーブル）
-- ------------------------------------------------------------
DROP TABLE IF EXISTS user_profile CASCADE;

CREATE TABLE user_profile (
    user_id INTEGER PRIMARY KEY REFERENCES personal_date(user_id) ON DELETE CASCADE,
    job_title VARCHAR(100) DEFAULT '',
    location_prefecture VARCHAR(50) DEFAULT '',
    salary_min INTEGER DEFAULT 0,
    intent_label TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE user_profile IS 'ユーザーの希望条件プロファイル';
COMMENT ON COLUMN user_profile.job_title IS '希望職種';
COMMENT ON COLUMN user_profile.location_prefecture IS '希望勤務地（都道府県）';
COMMENT ON COLUMN user_profile.salary_min IS '希望最低年収（万円）';
COMMENT ON COLUMN user_profile.intent_label IS 'ユーザー意図ラベル（カンマ区切り）';

-- ------------------------------------------------------------
-- 2.3 company_date（企業マスタテーブル）
-- ------------------------------------------------------------
DROP TABLE IF EXISTS company_date CASCADE;

CREATE TABLE company_date (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    address VARCHAR(255),
    phone_number VARCHAR(20),
    website_url VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE company_date IS '企業の基本情報マスターテーブル';
COMMENT ON COLUMN company_date.id IS 'レコード一意ID';
COMMENT ON COLUMN company_date.company_id IS '企業識別子（複数拠点でも同一企業として管理）';
COMMENT ON COLUMN company_date.email IS '企業担当者メールアドレス（ログイン用）';

-- ------------------------------------------------------------
-- 2.4 company_profile（求人情報テーブル）
-- ------------------------------------------------------------
DROP TABLE IF EXISTS company_profile CASCADE;

CREATE TABLE company_profile (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL,
    job_title VARCHAR(200) NOT NULL,
    job_summary TEXT,
    salary_min INTEGER NOT NULL,
    salary_max INTEGER NOT NULL,
    location_prefecture VARCHAR(50),
    employment_type VARCHAR(50),
    required_skills TEXT,
    preferred_skills TEXT,
    benefits TEXT,
    work_hours VARCHAR(100),
    holidays VARCHAR(100),
    application_deadline DATE,
    intent_labels TEXT,
    embedding VECTOR(1536),
    click_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    apply_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company_date(company_id) ON DELETE CASCADE
);

COMMENT ON TABLE company_profile IS '求人情報とエンベディングを管理';
COMMENT ON COLUMN company_profile.id IS '求人一意ID';
COMMENT ON COLUMN company_profile.company_id IS '企業ID（外部キー）';
COMMENT ON COLUMN company_profile.job_title IS '職種名';
COMMENT ON COLUMN company_profile.job_summary IS '求人概要';
COMMENT ON COLUMN company_profile.salary_min IS '最低年収（万円）';
COMMENT ON COLUMN company_profile.salary_max IS '最高年収（万円）';
COMMENT ON COLUMN company_profile.embedding IS 'OpenAI Embeddingベクトル（1536次元）';
COMMENT ON COLUMN company_profile.intent_labels IS '求人特徴ラベル（カンマ区切り）';

-- ------------------------------------------------------------
-- 2.5 user_interactions（ユーザー行動記録テーブル）
-- ------------------------------------------------------------
DROP TABLE IF EXISTS user_interactions CASCADE;

CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES personal_date(user_id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES company_profile(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL CHECK (
        interaction_type IN ('apply', 'favorite', 'click', 'view', 'chat_mention')
    ),
    interaction_value FLOAT DEFAULT 0.0,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE user_interactions IS 'ユーザーの求人に対する行動履歴';
COMMENT ON COLUMN user_interactions.interaction_type IS '行動タイプ（apply/favorite/click/view/chat_mention）';
COMMENT ON COLUMN user_interactions.interaction_value IS '行動値（閲覧時間など）';
COMMENT ON COLUMN user_interactions.metadata IS '追加情報（JSON形式）';

-- ------------------------------------------------------------
-- 2.6 chat_history（チャット履歴テーブル）
-- ------------------------------------------------------------
DROP TABLE IF EXISTS chat_history CASCADE;

CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES personal_date(user_id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('user', 'bot')),
    message_text TEXT NOT NULL,
    extracted_intent JSONB,
    session_id VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE chat_history IS 'ユーザーとAIの会話履歴';
COMMENT ON COLUMN chat_history.message_type IS 'メッセージ送信者（user/bot）';
COMMENT ON COLUMN chat_history.extracted_intent IS 'AIが抽出した意図（JSON形式）';
COMMENT ON COLUMN chat_history.session_id IS 'チャットセッション識別子';

-- ------------------------------------------------------------
-- 2.7 dynamic_questions（動的質問マスタテーブル）
-- ------------------------------------------------------------
DROP TABLE IF EXISTS dynamic_questions CASCADE;

CREATE TABLE dynamic_questions (
    id SERIAL PRIMARY KEY,
    question_key VARCHAR(100) NOT NULL UNIQUE,
    question_text TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    question_type VARCHAR(50),
    usage_count INTEGER DEFAULT 0,
    positive_response_count INTEGER DEFAULT 0,
    effectiveness_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dynamic_questions IS '動的質問マスターテーブル';
COMMENT ON COLUMN dynamic_questions.question_key IS '質問一意識別キー（remote, flex_time等）';
COMMENT ON COLUMN dynamic_questions.category IS '質問カテゴリ（働き方の柔軟性、企業文化等）';
COMMENT ON COLUMN dynamic_questions.effectiveness_score IS '質問の有効性スコア（0.0-1.0）';

-- ------------------------------------------------------------
-- 2.8 user_question_responses（動的質問への回答テーブル）
-- ------------------------------------------------------------
DROP TABLE IF EXISTS user_question_responses CASCADE;

CREATE TABLE user_question_responses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES personal_date(user_id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES dynamic_questions(id) ON DELETE CASCADE,
    question_key VARCHAR(100),
    response_text TEXT NOT NULL,
    normalized_response TEXT,
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, question_id)
);

COMMENT ON TABLE user_question_responses IS '動的質問に対するユーザー回答';
COMMENT ON COLUMN user_question_responses.question_id IS '質問ID（外部キー）';
COMMENT ON COLUMN user_question_responses.question_key IS '質問識別キー';
COMMENT ON COLUMN user_question_responses.normalized_response IS 'AIで正規化された回答';
COMMENT ON COLUMN user_question_responses.confidence_score IS 'AIの確信度（0.0-1.0）';

-- ------------------------------------------------------------
-- 2.9 job_attributes（求人属性テーブル）
-- ------------------------------------------------------------
DROP TABLE IF EXISTS job_attributes CASCADE;

CREATE TABLE job_attributes (
    id SERIAL PRIMARY KEY,
    job_id UUID NOT NULL UNIQUE REFERENCES company_profile(id) ON DELETE CASCADE,
    company_culture JSONB,
    work_flexibility JSONB,
    career_path JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE job_attributes IS '求人の多軸属性（AIで抽出）';
COMMENT ON COLUMN job_attributes.company_culture IS '企業文化・雰囲気（JSON形式）';
COMMENT ON COLUMN job_attributes.work_flexibility IS '働き方の柔軟性（JSON形式）';
COMMENT ON COLUMN job_attributes.career_path IS 'キャリアパス情報（JSON形式）';

-- ------------------------------------------------------------
-- 2.10 user_preferences（ユーザープロファイルテーブル）
-- ------------------------------------------------------------
DROP TABLE IF EXISTS user_preferences CASCADE;

CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES personal_date(user_id) ON DELETE CASCADE,
    preference_vector TEXT,
    preference_text TEXT,
    company_culture_pref JSONB,
    work_flexibility_pref JSONB,
    career_path_pref JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE user_preferences IS 'ユーザーの多軸評価プロファイル';
COMMENT ON COLUMN user_preferences.preference_vector IS 'エンベディングベクトル（文字列化）';
COMMENT ON COLUMN user_preferences.preference_text IS 'プロファイルのテキスト表現';

-- ============================================================
-- 3. インデックス作成
-- ============================================================

-- personal_date
CREATE INDEX idx_personal_date_email ON personal_date(email);

-- user_profile
CREATE INDEX idx_user_profile_job_title ON user_profile(job_title);
CREATE INDEX idx_user_profile_location ON user_profile(location_prefecture);
CREATE INDEX idx_user_profile_salary ON user_profile(salary_min);

-- company_date
CREATE INDEX idx_company_date_company_id ON company_date(company_id);

-- company_profile
CREATE INDEX idx_company_profile_company_id ON company_profile(company_id);
CREATE INDEX idx_company_profile_job_title ON company_profile(job_title);
CREATE INDEX idx_company_profile_location ON company_profile(location_prefecture);
CREATE INDEX idx_company_profile_salary_range ON company_profile(salary_min, salary_max);
CREATE INDEX idx_company_profile_created_at ON company_profile(created_at DESC);

-- pgvectorのインデックス（コサイン類似度検索）
CREATE INDEX idx_company_profile_embedding ON company_profile 
    USING ivfflat (embedding vector_cosine_ops) 
    WITH (lists = 100);

-- user_interactions
CREATE INDEX idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX idx_user_interactions_job_id ON user_interactions(job_id);
CREATE INDEX idx_user_interactions_type ON user_interactions(interaction_type);
CREATE INDEX idx_user_interactions_created_at ON user_interactions(created_at DESC);
CREATE INDEX idx_user_interactions_user_job ON user_interactions(user_id, job_id);

-- chat_history
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_session_id ON chat_history(session_id);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at DESC);

-- user_question_responses
CREATE INDEX idx_uqr_user_id ON user_question_responses(user_id);
CREATE INDEX idx_uqr_question_id ON user_question_responses(question_id);
CREATE INDEX idx_uqr_question_key ON user_question_responses(question_key);

-- dynamic_questions
CREATE INDEX idx_dynamic_questions_key ON dynamic_questions(question_key);
CREATE INDEX idx_dynamic_questions_category ON dynamic_questions(category);
CREATE INDEX idx_dynamic_questions_effectiveness ON dynamic_questions(effectiveness_score DESC);

-- job_attributes
CREATE INDEX idx_job_attributes_job_id ON job_attributes(job_id);

-- user_preferences
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);

-- user_personality_analysis
CREATE INDEX idx_user_personality_analysis_user_id ON user_personality_analysis(user_id);
CREATE INDEX idx_user_personality_analysis_updated_at ON user_personality_analysis(updated_at DESC);

-- scout_messages
CREATE INDEX idx_scout_messages_company_id ON scout_messages(company_id);
CREATE INDEX idx_scout_messages_job_id ON scout_messages(job_id);
CREATE INDEX idx_scout_messages_user_id ON scout_messages(user_id);
CREATE INDEX idx_scout_messages_status ON scout_messages(status);
CREATE INDEX idx_scout_messages_created_at ON scout_messages(created_at DESC);
CREATE INDEX idx_scout_messages_company_status ON scout_messages(company_id, status);
CREATE INDEX idx_scout_messages_user_status ON scout_messages(user_id, status);

-- user_profile embedding index (if embedding column exists)
CREATE INDEX IF NOT EXISTS idx_user_profile_embedding ON user_profile 
    USING ivfflat (embedding vector_cosine_ops) 
    WITH (lists = 100);

-- ============================================================
-- 4. ビュー作成
-- ============================================================

-- ------------------------------------------------------------
-- 4.1 user_interaction_summary（ユーザー行動サマリービュー）
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW user_interaction_summary AS
SELECT 
    user_id,
    COUNT(*) FILTER (WHERE interaction_type = 'click') AS total_clicks,
    COUNT(*) FILTER (WHERE interaction_type = 'favorite') AS total_favorites,
    COUNT(*) FILTER (WHERE interaction_type = 'apply') AS total_applies,
    COUNT(*) FILTER (WHERE interaction_type = 'view') AS total_views,
    COUNT(*) FILTER (WHERE interaction_type = 'chat_mention') AS total_chat_mentions,
    MAX(created_at) AS last_interaction
FROM user_interactions
GROUP BY user_id;

COMMENT ON VIEW user_interaction_summary IS 'ユーザーの行動サマリー集計ビュー';

-- ------------------------------------------------------------
-- 4.2 job_stats（求人統計ビュー）
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW job_stats AS
SELECT 
    cp.id AS job_id,
    cp.job_title,
    cp.company_id,
    cd.company_name,
    cp.location_prefecture,
    cp.salary_min,
    cp.salary_max,
    cp.click_count,
    cp.favorite_count,
    cp.apply_count,
    cp.view_count,
    cp.created_at,
    cp.updated_at,
    COALESCE(ja.company_culture, '{}'::jsonb) AS company_culture,
    COALESCE(ja.work_flexibility, '{}'::jsonb) AS work_flexibility,
    COALESCE(ja.career_path, '{}'::jsonb) AS career_path
FROM company_profile cp
LEFT JOIN company_date cd ON cp.company_id = cd.company_id
LEFT JOIN job_attributes ja ON cp.id = ja.job_id;

COMMENT ON VIEW job_stats IS '求人情報と統計の統合ビュー';

-- ------------------------------------------------------------
-- 4.3 popular_jobs（人気求人ビュー）
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW popular_jobs AS
SELECT 
    cp.id,
    cp.job_title,
    cd.company_name,
    cp.location_prefecture,
    cp.salary_min,
    cp.salary_max,
    cp.click_count,
    cp.favorite_count,
    cp.apply_count,
    cp.view_count,
    (cp.apply_count * 5.0 + cp.favorite_count * 3.0 + cp.click_count * 1.0 + cp.view_count * 0.5) AS popularity_score
FROM company_profile cp
LEFT JOIN company_date cd ON cp.company_id = cd.company_id
ORDER BY popularity_score DESC;

COMMENT ON VIEW popular_jobs IS '人気求人ランキングビュー';

-- ============================================================
-- 5. トリガー作成
-- ============================================================

-- ------------------------------------------------------------
-- 5.1 updated_at自動更新トリガー関数
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- personal_date
CREATE TRIGGER update_personal_date_updated_at
    BEFORE UPDATE ON personal_date
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- user_profile
CREATE TRIGGER update_user_profile_updated_at
    BEFORE UPDATE ON user_profile
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- company_date
CREATE TRIGGER update_company_date_updated_at
    BEFORE UPDATE ON company_date
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- company_profile
CREATE TRIGGER update_company_profile_updated_at
    BEFORE UPDATE ON company_profile
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- dynamic_questions
CREATE TRIGGER update_dynamic_questions_updated_at
    BEFORE UPDATE ON dynamic_questions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- job_attributes
CREATE TRIGGER update_job_attributes_updated_at
    BEFORE UPDATE ON job_attributes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- user_preferences
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ------------------------------------------------------------
-- 2.11 user_personality_analysis（ユーザー性格分析テーブル）
-- ------------------------------------------------------------
DROP TABLE IF EXISTS user_personality_analysis CASCADE;

CREATE TABLE user_personality_analysis (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES personal_date(user_id) ON DELETE CASCADE,
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE user_personality_analysis IS 'AIによるユーザー性格分析結果';
COMMENT ON COLUMN user_personality_analysis.analysis_data IS '性格特性、価値観、キャリア志向などのJSON';

-- ------------------------------------------------------------
-- 2.12 scout_messages（スカウトメッセージテーブル）
-- ------------------------------------------------------------
DROP TABLE IF EXISTS scout_messages CASCADE;

CREATE TABLE scout_messages (
    id SERIAL PRIMARY KEY,
    company_id UUID NOT NULL,
    job_id UUID NOT NULL,
    user_id INTEGER NOT NULL REFERENCES personal_date(user_id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    auto_generated BOOLEAN NOT NULL DEFAULT false,
    status VARCHAR(20) NOT NULL DEFAULT 'sent' CHECK (
        status IN ('sent', 'read', 'replied', 'declined')
    ),
    read_at TIMESTAMP,
    replied_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company_date(company_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES company_profile(id) ON DELETE CASCADE
);

COMMENT ON TABLE scout_messages IS '企業からユーザーへのスカウトメッセージ';
COMMENT ON COLUMN scout_messages.auto_generated IS 'AI自動生成フラグ';
COMMENT ON COLUMN scout_messages.status IS 'sent/read/replied/declined';

-- ============================================================
-- 2.13 既存テーブルへのカラム追加
-- ============================================================

-- user_profile にエンベディング追加
ALTER TABLE user_profile ADD COLUMN IF NOT EXISTS embedding VECTOR(1536);

-- job_attributes に追加カラム
ALTER TABLE job_attributes 
ADD COLUMN IF NOT EXISTS remote_work BOOLEAN,
ADD COLUMN IF NOT EXISTS flex_time BOOLEAN,
ADD COLUMN IF NOT EXISTS overtime_avg VARCHAR(20);

COMMENT ON COLUMN job_attributes.remote_work IS 'リモートワーク可否';
COMMENT ON COLUMN job_attributes.flex_time IS 'フレックスタイム制度';
COMMENT ON COLUMN job_attributes.overtime_avg IS '平均残業時間（少/中/多）';

-- company_date に追加カラム
ALTER TABLE company_date 
ADD COLUMN IF NOT EXISTS industry VARCHAR(100),
ADD COLUMN IF NOT EXISTS company_size VARCHAR(50);

COMMENT ON COLUMN company_date.industry IS '業界';
COMMENT ON COLUMN company_date.company_size IS '企業規模（小/中/大）';

-- ============================================================
-- 6. 初期データ挿入（基本的な質問）
-- ============================================================

INSERT INTO dynamic_questions (question_key, question_text, category, question_type) VALUES
    ('remote', 'リモートワークを希望しますか？', '働き方の柔軟性', 'boolean'),
    ('flex_time', 'フレックスタイム制度を希望しますか？', '働き方の柔軟性', 'boolean'),
    ('overtime', '残業についてどのようにお考えですか？', '働き方の柔軟性', 'choice'),
    ('side_job', '副業を希望しますか？', '働き方の柔軟性', 'boolean'),
    ('company_culture', 'どのような企業文化を希望しますか？', '企業文化・雰囲気', 'choice'),
    ('company_size', '希望する企業規模はありますか？', '企業文化・雰囲気', 'choice'),
    ('growth_opportunity', '成長機会を重視しますか？', 'キャリアパス', 'boolean'),
    ('training', '研修制度を重視しますか？', 'キャリアパス', 'boolean'),
    ('promotion_speed', 'キャリアアップのスピードをどの程度重視しますか？', 'キャリアパス', 'choice'),
    ('bonus', 'ボーナスの有無を重視しますか？', '給与・福利厚生', 'boolean'),
    ('benefits', '福利厚生を重視しますか？', '給与・福利厚生', 'boolean'),
    ('commute_time', '通勤時間をどの程度重視しますか？', 'ワークライフバランス', 'choice')
ON CONFLICT (question_key) DO NOTHING;

-- ============================================================
-- 完了メッセージ
-- ============================================================

DO $$
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'データベーススキーマの作成が完了しました！';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'テーブル数: 12 (スカウト機能2テーブル追加)';
    RAISE NOTICE 'ビュー数: 3';
    RAISE NOTICE 'インデックス数: 35+';
    RAISE NOTICE 'トリガー数: 8';
    RAISE NOTICE '';
    RAISE NOTICE '新規追加機能:';
    RAISE NOTICE '  - user_personality_analysis (ユーザー性格分析)';
    RAISE NOTICE '  - scout_messages (スカウトメッセージ管理)';
    RAISE NOTICE '';
    RAISE NOTICE '次のステップ:';
    RAISE NOTICE '  1. ダミーデータ生成: python generate_dummy_data_10k.py';
    RAISE NOTICE '  2. データ確認: SELECT COUNT(*) FROM personal_date;';
    RAISE NOTICE '  3. スカウト機能確認: SELECT COUNT(*) FROM scout_messages;';
    RAISE NOTICE '============================================================';
END $$;