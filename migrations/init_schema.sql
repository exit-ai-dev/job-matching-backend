-- ==============================================
-- Job Matching Platform - Complete Database Schema
-- ==============================================
-- This file contains the complete database schema for the job matching platform
-- Date: 2026-01-19

-- ==============================================
-- 1. Users Table (求職者・企業ユーザー)
-- ==============================================
CREATE TABLE IF NOT EXISTS users (
    -- Primary Key
    id VARCHAR(36) PRIMARY KEY,

    -- Authentication
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(10) NOT NULL CHECK (role IN ('seeker', 'employer')),

    -- LINE Integration
    line_user_id VARCHAR(100) UNIQUE,
    line_display_name VARCHAR(100),
    line_picture_url VARCHAR(500),
    line_email VARCHAR(255),
    line_linked_at TIMESTAMP WITH TIME ZONE,

    -- Job Seeker Specific Fields
    skills TEXT,  -- JSON string array
    experience_years VARCHAR(20),
    desired_salary_min VARCHAR(50),
    desired_salary_max VARCHAR(50),
    desired_location VARCHAR(100),
    desired_employment_type VARCHAR(50),
    resume_url VARCHAR(500),
    portfolio_url VARCHAR(500),

    -- Employer Specific Fields
    company_name VARCHAR(200),
    industry VARCHAR(100),
    company_size VARCHAR(50),
    company_description TEXT,
    company_website VARCHAR(500),
    company_location VARCHAR(200),
    company_logo_url VARCHAR(500),

    -- Profile Completion
    profile_completion VARCHAR(10) DEFAULT '0',

    -- Common Fields
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_line_user_id ON users(line_user_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ==============================================
-- 2. Jobs Table (求人情報)
-- ==============================================
CREATE TABLE IF NOT EXISTS jobs (
    -- Primary Key
    id VARCHAR(36) PRIMARY KEY,
    employer_id VARCHAR(36) NOT NULL,

    -- Basic Information
    title VARCHAR(200) NOT NULL,
    company VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(200) NOT NULL,
    employment_type VARCHAR(20) NOT NULL CHECK (employment_type IN ('full-time', 'part-time', 'contract', 'internship')),

    -- Salary Information
    salary_min INTEGER,
    salary_max INTEGER,
    salary_text VARCHAR(200),

    -- Skills
    required_skills TEXT,  -- JSON string array
    preferred_skills TEXT,  -- JSON string array

    -- Details
    requirements TEXT,
    benefits TEXT,
    tags TEXT,  -- JSON string array

    -- Remote Work
    remote BOOLEAN DEFAULT FALSE NOT NULL,

    -- Status
    status VARCHAR(20) DEFAULT 'draft' NOT NULL CHECK (status IN ('draft', 'published', 'closed')),
    featured BOOLEAN DEFAULT FALSE NOT NULL,

    -- AI Matching
    embedding TEXT,  -- JSON string (vector)

    -- Metadata
    meta_data TEXT,  -- JSON string

    -- Timestamps
    posted_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Foreign Keys
    FOREIGN KEY (employer_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for jobs table
CREATE INDEX IF NOT EXISTS idx_jobs_employer_id ON jobs(employer_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_employment_type ON jobs(employment_type);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);

-- ==============================================
-- 3. Applications Table (応募情報)
-- ==============================================
CREATE TABLE IF NOT EXISTS applications (
    -- Primary Key
    id VARCHAR(36) PRIMARY KEY,
    seeker_id VARCHAR(36) NOT NULL,
    job_id VARCHAR(36) NOT NULL,

    -- Status
    status VARCHAR(20) DEFAULT 'screening' NOT NULL CHECK (status IN ('screening', 'interview', 'offered', 'rejected', 'withdrawn')),
    status_detail VARCHAR(100),  -- e.g., "一次面接待ち"
    status_color VARCHAR(20) DEFAULT 'yellow',  -- UI display color

    -- Match Score
    match_score INTEGER,

    -- Next Steps
    next_step VARCHAR(100),
    interview_date TIMESTAMP WITH TIME ZONE,

    -- Submitted Documents
    resume_submitted VARCHAR(10) DEFAULT 'false',
    portfolio_submitted VARCHAR(10) DEFAULT 'false',
    cover_letter TEXT,

    -- Messages and Notes
    message TEXT,
    notes TEXT,

    -- Timestamps
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Foreign Keys
    FOREIGN KEY (seeker_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,

    -- Unique constraint: one application per user per job
    UNIQUE(seeker_id, job_id)
);

-- Indexes for applications table
CREATE INDEX IF NOT EXISTS idx_applications_seeker_id ON applications(seeker_id);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_applied_at ON applications(applied_at DESC);

-- ==============================================
-- 4. Scouts Table (スカウト情報)
-- ==============================================
CREATE TABLE IF NOT EXISTS scouts (
    -- Primary Key
    id VARCHAR(36) PRIMARY KEY,
    employer_id VARCHAR(36) NOT NULL,
    seeker_id VARCHAR(36) NOT NULL,
    job_id VARCHAR(36),  -- Optional: can be a general scout without specific job

    -- Scout Content
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,

    -- Match Score
    match_score INTEGER,

    -- Status
    status VARCHAR(20) DEFAULT 'new' NOT NULL CHECK (status IN ('new', 'read', 'replied', 'declined')),

    -- Tags
    tags TEXT,  -- JSON string array

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    read_at TIMESTAMP WITH TIME ZONE,
    replied_at TIMESTAMP WITH TIME ZONE,

    -- Foreign Keys
    FOREIGN KEY (employer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (seeker_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE SET NULL
);

-- Indexes for scouts table
CREATE INDEX IF NOT EXISTS idx_scouts_employer_id ON scouts(employer_id);
CREATE INDEX IF NOT EXISTS idx_scouts_seeker_id ON scouts(seeker_id);
CREATE INDEX IF NOT EXISTS idx_scouts_job_id ON scouts(job_id);
CREATE INDEX IF NOT EXISTS idx_scouts_status ON scouts(status);
CREATE INDEX IF NOT EXISTS idx_scouts_created_at ON scouts(created_at DESC);

-- ==============================================
-- Comments for Documentation
-- ==============================================

-- Users table
COMMENT ON TABLE users IS 'ユーザーテーブル（求職者・企業）';
COMMENT ON COLUMN users.id IS 'ユーザーID（UUID）';
COMMENT ON COLUMN users.email IS 'メールアドレス（ログイン用）';
COMMENT ON COLUMN users.password_hash IS 'パスワードハッシュ';
COMMENT ON COLUMN users.name IS 'ユーザー名';
COMMENT ON COLUMN users.role IS 'ロール: seeker（求職者）/ employer（企業）';
COMMENT ON COLUMN users.line_user_id IS 'LINE ユーザーID';
COMMENT ON COLUMN users.line_display_name IS 'LINE 表示名';
COMMENT ON COLUMN users.line_picture_url IS 'LINE プロフィール画像URL';
COMMENT ON COLUMN users.line_email IS 'LINE メールアドレス';
COMMENT ON COLUMN users.skills IS 'スキル（JSON配列）';
COMMENT ON COLUMN users.profile_completion IS 'プロフィール完成度（%）';

-- Jobs table
COMMENT ON TABLE jobs IS '求人テーブル';
COMMENT ON COLUMN jobs.id IS '求人ID（UUID）';
COMMENT ON COLUMN jobs.employer_id IS '企業ユーザーID';
COMMENT ON COLUMN jobs.title IS '求人タイトル';
COMMENT ON COLUMN jobs.employment_type IS '雇用形態: full-time / part-time / contract / internship';
COMMENT ON COLUMN jobs.status IS 'ステータス: draft / published / closed';
COMMENT ON COLUMN jobs.embedding IS 'AIマッチング用ベクトル（JSON）';

-- Applications table
COMMENT ON TABLE applications IS '応募テーブル';
COMMENT ON COLUMN applications.id IS '応募ID（UUID）';
COMMENT ON COLUMN applications.seeker_id IS '求職者ユーザーID';
COMMENT ON COLUMN applications.job_id IS '求人ID';
COMMENT ON COLUMN applications.status IS 'ステータス: screening / interview / offered / rejected / withdrawn';
COMMENT ON COLUMN applications.match_score IS 'マッチスコア（0-100）';

-- Scouts table
COMMENT ON TABLE scouts IS 'スカウトテーブル';
COMMENT ON COLUMN scouts.id IS 'スカウトID（UUID）';
COMMENT ON COLUMN scouts.employer_id IS '企業ユーザーID';
COMMENT ON COLUMN scouts.seeker_id IS '求職者ユーザーID';
COMMENT ON COLUMN scouts.job_id IS '求人ID（オプション）';
COMMENT ON COLUMN scouts.status IS 'ステータス: new / read / replied / declined';
