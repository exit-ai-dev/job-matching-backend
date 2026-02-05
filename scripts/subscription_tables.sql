-- =============================================================================
-- サブスクリプション関連テーブル作成SQL
-- Azure Database for PostgreSQL 用
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. subscription_plans テーブル（プラン定義）
-- -----------------------------------------------------------------------------
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

COMMENT ON TABLE subscription_plans IS 'サブスクリプションプラン定義';
COMMENT ON COLUMN subscription_plans.name IS '内部名（seeker_free, employer_business等）';
COMMENT ON COLUMN subscription_plans.tier IS 'プラン階層（seeker_free, seeker_standard, seeker_premium, employer_free, employer_starter, employer_business）';
COMMENT ON COLUMN subscription_plans.features IS '機能制限JSON（{"ai_chat_limit": 3, "application_limit": 5}等）';

-- -----------------------------------------------------------------------------
-- 2. subscriptions テーブル（ユーザーのサブスクリプション）
-- -----------------------------------------------------------------------------
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

COMMENT ON TABLE subscriptions IS 'ユーザーサブスクリプション';
COMMENT ON COLUMN subscriptions.status IS 'ステータス（active, canceled, past_due, paused, trialing）';
COMMENT ON COLUMN subscriptions.gmo_subscription_id IS 'GMOペイメント継続課金ID';

-- -----------------------------------------------------------------------------
-- 3. usage_tracking テーブル（使用量追跡）
-- -----------------------------------------------------------------------------
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

COMMENT ON TABLE usage_tracking IS '月間使用量追跡';

-- -----------------------------------------------------------------------------
-- 4. payment_history テーブル（決済履歴）
-- -----------------------------------------------------------------------------
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

COMMENT ON TABLE payment_history IS '決済履歴';
COMMENT ON COLUMN payment_history.status IS 'ステータス（pending, success, failed, refunded）';

-- -----------------------------------------------------------------------------
-- 5. users テーブルへのカラム追加
-- -----------------------------------------------------------------------------
DO $$
BEGIN
    -- gmo_member_id カラムを追加
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'gmo_member_id') THEN
        ALTER TABLE users ADD COLUMN gmo_member_id VARCHAR(100) UNIQUE;
        CREATE INDEX idx_users_gmo_member_id ON users(gmo_member_id);
        RAISE NOTICE 'Added gmo_member_id column to users table';
    END IF;

    -- subscription_tier カラムを追加
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'subscription_tier') THEN
        ALTER TABLE users ADD COLUMN subscription_tier VARCHAR(50) NOT NULL DEFAULT 'free';
        RAISE NOTICE 'Added subscription_tier column to users table';
    END IF;
END $$;

-- =============================================================================
-- シードデータ投入
-- =============================================================================

-- 既存データがない場合のみ投入
INSERT INTO subscription_plans (id, name, display_name, user_role, tier, price_jpy, features, description, display_order, is_active)
SELECT * FROM (VALUES
    -- 求職者向けプラン
    (gen_random_uuid()::text, 'seeker_free', 'フリープラン', 'seeker', 'seeker_free', 0,
     '{"ai_chat_limit": 0, "application_limit": 5}',
     '基本的な求人閲覧と月5件までの応募が可能', 1, true),

    (gen_random_uuid()::text, 'seeker_standard', 'スタンダードプラン', 'seeker', 'seeker_standard', 980,
     '{"ai_chat_limit": 20, "application_limit": 30}',
     'AIチャット20回/月、応募30件/月まで利用可能', 2, true),

    (gen_random_uuid()::text, 'seeker_premium', 'プレミアムプラン', 'seeker', 'seeker_premium', 2980,
     '{"ai_chat_limit": -1, "application_limit": -1}',
     'AIチャット・応募ともに無制限', 3, true),

    -- 企業向けプラン
    (gen_random_uuid()::text, 'employer_free', 'フリープラン', 'employer', 'employer_free', 0,
     '{"scout_limit": 3, "job_posting_limit": 1, "candidate_view_limit": 5}',
     '求人1件、スカウト3件/月まで利用可能', 1, true),

    (gen_random_uuid()::text, 'employer_starter', 'スタータープラン', 'employer', 'employer_starter', 9800,
     '{"scout_limit": 15, "job_posting_limit": 3, "candidate_view_limit": 30}',
     '求人3件、スカウト15件/月、候補者閲覧30件/月', 2, true),

    (gen_random_uuid()::text, 'employer_business', 'ビジネスプラン', 'employer', 'employer_business', 29800,
     '{"scout_limit": 50, "job_posting_limit": 10, "candidate_view_limit": 100}',
     '求人10件、スカウト50件/月、候補者閲覧100件/月', 3, true)

) AS v(id, name, display_name, user_role, tier, price_jpy, features, description, display_order, is_active)
WHERE NOT EXISTS (SELECT 1 FROM subscription_plans LIMIT 1);

-- 投入結果確認
SELECT name, display_name, user_role, price_jpy, features
FROM subscription_plans
ORDER BY user_role, display_order;
