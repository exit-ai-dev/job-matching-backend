-- ============================================
-- JobMatch AI システム - 完全データベーススキーマ
-- 全テーブル・カラム定義（統合版）
-- ============================================
-- 
-- 【概要】
-- このSQLファイルは、JobMatch AIシステムの全データベース構造を
-- 1つのファイルで定義しています。このファイルを実行するだけで、
-- 必要な全てのテーブル、インデックス、ビューが作成されます。
--
-- 【実行方法】
-- psql -h localhost -U postgres -d jobmatch -f complete_database_schema.sql
--
-- 【PostgreSQLバージョン】
-- PostgreSQL 12以降を推奨
-- 
-- 【必要な拡張機能】
-- - pgvector (ベクトル検索用)
--
-- 【作成されるオブジェクト】
-- - テーブル: 30個
-- - ビュー: 1個
-- - インデックス: 15個以上
-- 
-- ============================================

-- ============================================
-- 前提条件: 拡張機能のインストール
-- ============================================

-- pgvector拡張機能の有効化（ベクトル検索用）
-- 事前に以下のコマンドでインストールが必要:
-- sudo apt install postgresql-<version>-pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- UUID生成用（PostgreSQL 13以降では標準で利用可能）
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- データベース作成（必要に応じてコメント解除）
-- ============================================

-- CREATE DATABASE jobmatch
--     WITH 
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'ja_JP.UTF-8'
--     LC_CTYPE = 'ja_JP.UTF-8'
--     TEMPLATE = template0;

-- \c jobmatch

-- ============================================
-- 1. ユーザー関連テーブル (5テーブル)
-- ============================================

-- 1.1 個人基本情報
CREATE TABLE IF NOT EXISTS personal_date (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    age INTEGER,
    gender VARCHAR(20),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE personal_date IS 'ユーザー基本情報テーブル';
COMMENT ON COLUMN personal_date.user_id IS 'ユーザーID（主キー、自動採番）';
COMMENT ON COLUMN personal_date.email IS 'メールアドレス（ログインID、ユニーク制約）';
COMMENT ON COLUMN personal_date.password IS 'パスワード（ハッシュ化して保存）';

-- 1.2 ユーザープロフィール（職歴・スキル）
CREATE TABLE IF NOT EXISTS user_profile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE,
    job_title VARCHAR(200),
    years_of_experience INTEGER,
    skills TEXT[],
    education_level VARCHAR(50),
    location_prefecture VARCHAR(50),
    location_city VARCHAR(100),
    salary_min INTEGER,
    salary_max INTEGER,
    work_style_preference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

COMMENT ON TABLE user_profile IS 'ユーザープロフィール（職歴・スキル情報）';
COMMENT ON COLUMN user_profile.skills IS 'スキル配列（例: {Python, JavaScript, SQL}）';
COMMENT ON COLUMN user_profile.salary_min IS '希望最低年収（円）';
COMMENT ON COLUMN user_profile.salary_max IS '希望最高年収（円）';

-- 1.3 ユーザー希望条件プロフィール
CREATE TABLE IF NOT EXISTS user_preferences_profile (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE,
    job_title VARCHAR(200),
    location_prefecture VARCHAR(50),
    location_city VARCHAR(100),
    salary_min INTEGER,
    salary_max INTEGER,
    remote_work_preference VARCHAR(50),
    employment_type VARCHAR(50),
    industry_preferences TEXT[],
    work_hours_preference VARCHAR(100),
    company_size_preference VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

COMMENT ON TABLE user_preferences_profile IS 'ユーザー希望条件プロフィール';
COMMENT ON COLUMN user_preferences_profile.remote_work_preference IS 'リモートワーク希望（例: 完全リモート、週2-3日出社）';
COMMENT ON COLUMN user_preferences_profile.industry_preferences IS '希望業界配列';

-- 1.4 ユーザー性格分析
CREATE TABLE IF NOT EXISTS user_personality_analysis (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE,
    personality_traits JSONB,
    work_values JSONB,
    communication_style VARCHAR(50),
    decision_making_style VARCHAR(50),
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

COMMENT ON TABLE user_personality_analysis IS 'ユーザー性格分析（AIによる分析結果）';
COMMENT ON COLUMN user_personality_analysis.personality_traits IS '性格特性（JSONB形式）';
COMMENT ON COLUMN user_personality_analysis.work_values IS '仕事の価値観（JSONB形式）';

-- 1.5 ユーザーセッション
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE,
    session_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

COMMENT ON TABLE user_sessions IS 'ユーザーセッション管理';
COMMENT ON COLUMN user_sessions.session_data IS 'セッションデータ（JSONB形式）';
COMMENT ON COLUMN user_sessions.expires_at IS 'セッション有効期限';

-- ============================================
-- 2. 企業・求人関連テーブル (4テーブル)
-- ============================================

-- 2.1 企業基本情報
CREATE TABLE IF NOT EXISTS company_date (
    company_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    company_size VARCHAR(50),
    founded_year INTEGER,
    website_url VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE company_date IS '企業基本情報テーブル';
COMMENT ON COLUMN company_date.company_id IS '企業ID（UUID、主キー）';
COMMENT ON COLUMN company_date.company_size IS '企業規模（例: 1-10名、11-50名、51-200名）';

-- 2.2 求人情報（メインテーブル - 3層構造）
CREATE TABLE IF NOT EXISTS company_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES company_date(company_id) ON DELETE CASCADE,
    
    -- Layer 1: 基本情報（必須）
    job_title VARCHAR(200) NOT NULL,
    job_description TEXT NOT NULL,
    location_prefecture VARCHAR(50) NOT NULL,
    location_city VARCHAR(100),
    salary_min INTEGER NOT NULL,
    salary_max INTEGER NOT NULL,
    employment_type VARCHAR(50) DEFAULT '正社員',
    
    -- Layer 2: 構造化データ（オプション）
    remote_option VARCHAR(50),
    flex_time BOOLEAN DEFAULT FALSE,
    latest_start_time TIME,
    side_job_allowed BOOLEAN DEFAULT FALSE,
    team_size VARCHAR(50),
    development_method VARCHAR(100),
    tech_stack JSONB,
    required_skills TEXT[],
    preferred_skills TEXT[],
    benefits TEXT[],
    
    -- Layer 3: 自由記述（AI抽出対象）
    work_style_details TEXT,
    team_culture_details TEXT,
    growth_opportunities_details TEXT,
    benefits_details TEXT,
    office_environment_details TEXT,
    project_details TEXT,
    company_appeal_text TEXT,
    
    -- AI処理済みデータ
    ai_extracted_features JSONB,
    additional_questions JSONB,
    embedding VECTOR(1536),
    
    -- メタデータ
    status VARCHAR(20) DEFAULT 'active',
    view_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    apply_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE company_profile IS '求人情報テーブル（3層構造: 基本情報/構造化データ/自由記述）';
COMMENT ON COLUMN company_profile.tech_stack IS '技術スタック（JSONB形式、例: {"backend": ["Python", "Django"], "frontend": ["React"]}）';
COMMENT ON COLUMN company_profile.embedding IS 'ベクトル埋め込み（1536次元、OpenAI text-embedding-ada-002形式）';
COMMENT ON COLUMN company_profile.status IS 'ステータス（active, inactive, closed）';

-- 2.3 求人属性（追加の構造化データ）
CREATE TABLE IF NOT EXISTS job_attributes (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES company_profile(id) ON DELETE CASCADE,
    attribute_name VARCHAR(100) NOT NULL,
    attribute_value TEXT,
    attribute_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE job_attributes IS '求人の追加属性（動的な属性管理）';

-- 2.4 動的質問の回答（別テーブル方式）
CREATE TABLE IF NOT EXISTS job_additional_answers (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES company_profile(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    answer_text TEXT,
    question_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE job_additional_answers IS '動的質問への回答（トレンドに基づく追加質問）';

-- ============================================
-- 3. 会話・マッチング関連テーブル (7テーブル)
-- ============================================

-- 3.1 会話ログ（メインログ）
CREATE TABLE IF NOT EXISTS conversation_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE,
    turn_number INTEGER NOT NULL,
    user_message TEXT,
    ai_response TEXT,
    extracted_intent JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE conversation_logs IS '会話ログ（メインログ）';
COMMENT ON COLUMN conversation_logs.extracted_intent IS '抽出された意図（JSONB形式）';

-- 3.2 会話セッション
CREATE TABLE IF NOT EXISTS conversation_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE,
    session_id VARCHAR(100) NOT NULL UNIQUE,
    total_turns INTEGER,
    end_reason VARCHAR(50),
    final_match_percentage FLOAT,
    presented_jobs JSONB,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE conversation_sessions IS '会話セッション管理';
COMMENT ON COLUMN conversation_sessions.end_reason IS '終了理由（completed, abandoned, timeout等）';
COMMENT ON COLUMN conversation_sessions.presented_jobs IS '提示した求人のリスト（JSONB配列）';

-- 3.3 会話ターン詳細
CREATE TABLE IF NOT EXISTS conversation_turns (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    turn_number INTEGER NOT NULL,
    user_message TEXT,
    bot_message TEXT,
    extracted_info JSONB,
    top_score FLOAT,
    top_match_percentage FLOAT,
    candidate_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE conversation_turns IS '会話ターン詳細（各ターンの情報）';
COMMENT ON COLUMN conversation_turns.top_score IS '最高スコア（そのターンでの最高マッチングスコア）';
COMMENT ON COLUMN conversation_turns.candidate_count IS '候補求人数（そのターンでマッチした求人数）';

-- 3.4 ユーザー洞察蓄積
CREATE TABLE IF NOT EXISTS user_insights (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    insights JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, session_id)
);

COMMENT ON TABLE user_insights IS 'ユーザー洞察蓄積（会話から得られた洞察）';

-- 3.5 スコア履歴
CREATE TABLE IF NOT EXISTS score_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    turn_number INTEGER NOT NULL,
    job_id VARCHAR(100) NOT NULL,
    score FLOAT,
    match_percentage FLOAT,
    score_details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE score_history IS 'マッチングスコア履歴';
COMMENT ON COLUMN score_history.score_details IS 'スコア詳細（各要素のスコア、JSONB形式）';

-- 3.6 チャット履歴
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    sender VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE chat_history IS 'チャット履歴（シンプルな会話履歴）';
COMMENT ON COLUMN chat_history.sender IS '送信者（user または bot）';

-- 3.7 チャットセッション管理
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE chat_sessions IS 'チャットセッション管理（セッション単位の管理）';

-- ============================================
-- 4. ユーザー行動追跡テーブル (3テーブル)
-- ============================================

-- 4.1 ユーザーインタラクション
CREATE TABLE IF NOT EXISTS user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE,
    job_id UUID REFERENCES company_profile(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL,
    session_id VARCHAR(100),
    interaction_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE user_interactions IS 'ユーザー行動追跡（view, click, favorite, apply等）';
COMMENT ON COLUMN user_interactions.interaction_type IS 'インタラクションタイプ（view, click, favorite, apply）';

-- 4.2 ユーザーインタラクションサマリー（ビュー）
CREATE OR REPLACE VIEW user_interaction_summary AS
SELECT 
    user_id,
    job_id,
    COUNT(*) FILTER (WHERE interaction_type = 'view') as view_count,
    COUNT(*) FILTER (WHERE interaction_type = 'click') as click_count,
    COUNT(*) FILTER (WHERE interaction_type = 'favorite') as favorite_count,
    COUNT(*) FILTER (WHERE interaction_type = 'apply') as apply_count,
    MAX(created_at) as last_interaction
FROM user_interactions
GROUP BY user_id, job_id;

COMMENT ON VIEW user_interaction_summary IS 'ユーザーインタラクションサマリー（集計ビュー）';

-- 4.3 検索履歴
CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE,
    search_query TEXT,
    filters JSONB,
    results_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE search_history IS '検索履歴（検索クエリとフィルター条件）';

-- ============================================
-- 5. エンリッチメント・トレンド関連テーブル (5テーブル)
-- ============================================

-- 5.1 不足情報ログ
CREATE TABLE IF NOT EXISTS missing_job_info_log (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES company_profile(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES personal_date(user_id) ON DELETE SET NULL,
    missing_field VARCHAR(100) NOT NULL,
    detected_from VARCHAR(50),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE missing_job_info_log IS '不足情報検知ログ（どのフィールドが不足しているか）';
COMMENT ON COLUMN missing_job_info_log.detected_from IS '検知元（conversation, search等）';

-- 5.2 企業への追加質問リクエスト
CREATE TABLE IF NOT EXISTS company_enrichment_requests (
    id SERIAL PRIMARY KEY,
    job_id UUID REFERENCES company_profile(id) ON DELETE CASCADE,
    company_id UUID REFERENCES company_date(company_id) ON DELETE CASCADE,
    missing_field VARCHAR(100) NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50),
    priority_score INTEGER,
    detection_count INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'pending',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    response_text TEXT
);

COMMENT ON TABLE company_enrichment_requests IS '企業への追加質問リクエスト（不足情報の補完）';
COMMENT ON COLUMN company_enrichment_requests.detection_count IS '検知回数（同じ質問が複数回検知された回数）';

-- 5.3 グローバル嗜好トレンド
CREATE TABLE IF NOT EXISTS global_preference_trends (
    id SERIAL PRIMARY KEY,
    preference_key VARCHAR(100) NOT NULL,
    preference_value TEXT,
    occurrence_count INTEGER DEFAULT 1,
    unique_users INTEGER DEFAULT 1,
    last_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trend_score FLOAT,
    category VARCHAR(50),
    UNIQUE(preference_key, preference_value)
);

COMMENT ON TABLE global_preference_trends IS 'グローバル嗜好トレンド分析（全ユーザーの嗜好傾向）';
COMMENT ON COLUMN global_preference_trends.trend_score IS 'トレンドスコア（重要度を数値化）';

-- 5.4 トレンド閾値（動的質問生成用）
CREATE TABLE IF NOT EXISTS trend_thresholds (
    id SERIAL PRIMARY KEY,
    threshold_name VARCHAR(100) UNIQUE NOT NULL,
    threshold_value INTEGER NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE trend_thresholds IS 'トレンド閾値（動的質問生成の閾値管理）';

-- 5.5 週次トレンド（キャッシュ）
CREATE TABLE IF NOT EXISTS current_weekly_trends (
    id SERIAL PRIMARY KEY,
    week_start DATE NOT NULL,
    trend_data JSONB NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(week_start)
);

COMMENT ON TABLE current_weekly_trends IS '週次トレンドキャッシュ（パフォーマンス向上用）';

-- ============================================
-- 6. 基本項目管理テーブル (1テーブル)
-- ============================================

-- 6.1 基本項目定義
CREATE TABLE IF NOT EXISTS baseline_job_fields (
    field_id SERIAL PRIMARY KEY,
    field_name VARCHAR(100) UNIQUE NOT NULL,
    field_type VARCHAR(50) NOT NULL,
    label VARCHAR(200) NOT NULL,
    question_template TEXT,
    options JSONB,
    placeholder TEXT,
    required BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 0,
    category VARCHAR(50),
    promoted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE baseline_job_fields IS '基本項目定義（求人情報の基本フィールド管理）';
COMMENT ON COLUMN baseline_job_fields.promoted_at IS '必須項目に昇格した日時';

-- ============================================
-- 7. スカウト関連テーブル (1テーブル)
-- ============================================

-- 7.1 スカウトメッセージ
CREATE TABLE IF NOT EXISTS scout_messages (
    id SERIAL PRIMARY KEY,
    company_id UUID REFERENCES company_date(company_id) ON DELETE CASCADE,
    job_id UUID REFERENCES company_profile(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE,
    message_title VARCHAR(255) NOT NULL,
    message_body TEXT NOT NULL,
    match_score FLOAT,
    match_reasons JSONB,
    status VARCHAR(50) DEFAULT 'sent',
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    replied_at TIMESTAMP
);

COMMENT ON TABLE scout_messages IS 'スカウトメッセージ（企業からユーザーへのスカウト）';
COMMENT ON COLUMN scout_messages.match_reasons IS 'マッチ理由（JSONB形式、詳細なマッチング理由）';
COMMENT ON COLUMN scout_messages.status IS 'ステータス（sent, read, replied）';

-- ============================================
-- 8. 動的質問関連テーブル (2テーブル)
-- ============================================

-- 8.1 動的質問定義
CREATE TABLE IF NOT EXISTS dynamic_questions (
    id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50),
    target_context VARCHAR(100),
    options JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dynamic_questions IS '動的質問定義（トレンドに基づいて生成される質問）';
COMMENT ON COLUMN dynamic_questions.target_context IS '対象コンテキスト（job_seeker, company等）';

-- 8.2 ユーザー回答
CREATE TABLE IF NOT EXISTS user_question_responses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES personal_date(user_id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES dynamic_questions(id) ON DELETE CASCADE,
    response_text TEXT,
    response_data JSONB,
    session_id VARCHAR(100),
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE user_question_responses IS 'ユーザー回答（動的質問への回答）';

-- ============================================
-- インデックス作成（パフォーマンス最適化）
-- ============================================

-- 求人検索用インデックス
CREATE INDEX IF NOT EXISTS idx_company_profile_job_title ON company_profile(job_title);
CREATE INDEX IF NOT EXISTS idx_company_profile_location ON company_profile(location_prefecture, location_city);
CREATE INDEX IF NOT EXISTS idx_company_profile_salary ON company_profile(salary_min, salary_max);
CREATE INDEX IF NOT EXISTS idx_company_profile_status ON company_profile(status);
CREATE INDEX IF NOT EXISTS idx_company_profile_company_id ON company_profile(company_id);
CREATE INDEX IF NOT EXISTS idx_company_profile_created_at ON company_profile(created_at DESC);

-- ユーザーインタラクション用インデックス
CREATE INDEX IF NOT EXISTS idx_user_interactions_user_job ON user_interactions(user_id, job_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_type ON user_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_user_interactions_created ON user_interactions(created_at DESC);

-- 会話ログ用インデックス
CREATE INDEX IF NOT EXISTS idx_conversation_logs_session ON conversation_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_logs_user ON conversation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_user ON conversation_sessions(user_id);

-- 会話ターン用インデックス
CREATE INDEX IF NOT EXISTS idx_conversation_turns_session ON conversation_turns(user_id, session_id);
CREATE INDEX IF NOT EXISTS idx_score_history_session ON score_history(user_id, session_id, turn_number);

-- エンリッチメント用インデックス
CREATE INDEX IF NOT EXISTS idx_missing_job_info_job ON missing_job_info_log(job_id);
CREATE INDEX IF NOT EXISTS idx_missing_job_info_field ON missing_job_info_log(missing_field);
CREATE INDEX IF NOT EXISTS idx_enrichment_requests_job ON company_enrichment_requests(job_id);
CREATE INDEX IF NOT EXISTS idx_enrichment_requests_status ON company_enrichment_requests(status);

-- トレンド用インデックス
CREATE INDEX IF NOT EXISTS idx_global_trends_key ON global_preference_trends(preference_key);
CREATE INDEX IF NOT EXISTS idx_global_trends_score ON global_preference_trends(trend_score DESC);

-- チャットセッション用インデックス
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at);

-- ============================================
-- 初期データ挿入（トレンド閾値）
-- ============================================

INSERT INTO trend_thresholds (threshold_name, threshold_value, description) 
VALUES 
    ('high_demand_threshold', 10, '高需要と判断する最小出現回数'),
    ('medium_demand_threshold', 5, '中需要と判断する最小出現回数'),
    ('question_generation_threshold', 3, '動的質問を生成する最小出現回数')
ON CONFLICT (threshold_name) DO NOTHING;

-- ============================================
-- 統計情報
-- ============================================

DO $$ 
DECLARE
    table_count INTEGER;
    index_count INTEGER;
BEGIN 
    -- テーブル数をカウント
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE';
    
    -- インデックス数をカウント
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes 
    WHERE schemaname = 'public';
    
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ JobMatch AI データベーススキーマ作成完了';
    RAISE NOTICE '========================================';
    RAISE NOTICE '📊 作成されたテーブル数: %', table_count;
    RAISE NOTICE '🔍 作成されたインデックス数: %', index_count;
    RAISE NOTICE '📁 ビュー数: 1 (user_interaction_summary)';
    RAISE NOTICE '⚙️  初期データ: trend_thresholds に3件挿入済み';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE '【テーブル一覧】';
    RAISE NOTICE '1. ユーザー関連: 5テーブル';
    RAISE NOTICE '   - personal_date, user_profile, user_preferences_profile,';
    RAISE NOTICE '     user_personality_analysis, user_sessions';
    RAISE NOTICE '';
    RAISE NOTICE '2. 企業・求人関連: 4テーブル';
    RAISE NOTICE '   - company_date, company_profile, job_attributes,';
    RAISE NOTICE '     job_additional_answers';
    RAISE NOTICE '';
    RAISE NOTICE '3. 会話・マッチング関連: 7テーブル';
    RAISE NOTICE '   - conversation_logs, conversation_sessions, conversation_turns,';
    RAISE NOTICE '     user_insights, score_history, chat_history, chat_sessions';
    RAISE NOTICE '';
    RAISE NOTICE '4. ユーザー行動追跡: 3テーブル';
    RAISE NOTICE '   - user_interactions, user_interaction_summary (VIEW),';
    RAISE NOTICE '     search_history';
    RAISE NOTICE '';
    RAISE NOTICE '5. エンリッチメント・トレンド: 5テーブル';
    RAISE NOTICE '   - missing_job_info_log, company_enrichment_requests,';
    RAISE NOTICE '     global_preference_trends, trend_thresholds,';
    RAISE NOTICE '     current_weekly_trends';
    RAISE NOTICE '';
    RAISE NOTICE '6. その他: 4テーブル';
    RAISE NOTICE '   - baseline_job_fields, scout_messages, dynamic_questions,';
    RAISE NOTICE '     user_question_responses';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE '【次のステップ】';
    RAISE NOTICE '1. ダミーデータの投入:';
    RAISE NOTICE '   python generate_dummy_data.py --password your_password';
    RAISE NOTICE '';
    RAISE NOTICE '2. データベース接続テスト:';
    RAISE NOTICE '   psql -h localhost -U postgres -d jobmatch -c "SELECT COUNT(*) FROM personal_date;"';
    RAISE NOTICE '';
    RAISE NOTICE '3. スキーマ確認:';
    RAISE NOTICE '   \dt  (テーブル一覧表示)';
    RAISE NOTICE '   \d+ table_name  (テーブル詳細表示)';
    RAISE NOTICE '========================================';
END $$;
