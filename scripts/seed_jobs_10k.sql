-- 10,000 dummy jobs for the `jobs` table (PostgreSQL)
-- Requires at least one employer user in `users`.

INSERT INTO jobs (
    id,
    employer_id,
    title,
    company,
    description,
    location,
    employment_type,
    salary_min,
    salary_max,
    salary_text,
    required_skills,
    preferred_skills,
    requirements,
    benefits,
    tags,
    remote,
    status,
    featured,
    embedding,
    meta_data,
    posted_date,
    created_at,
    updated_at
)
SELECT
    lower(format(
        '%s-%s-%s-%s-%s',
        substr(md5(random()::text), 1, 8),
        substr(md5(random()::text), 9, 4),
        substr(md5(random()::text), 13, 4),
        substr(md5(random()::text), 17, 4),
        substr(md5(random()::text), 21, 12)
    )) AS id,
    employer.employer_id AS employer_id,
    title_pool.title AS title,
    company_pool.company AS company,
    format(
        '%sの募集です。%sの経験を活かし、プロダクト開発に携わっていただきます。',
        title_pool.title,
        stack_pool.primary_skill
    ) AS description,
    location_pool.location AS location,
    employment_pool.employment_type::employmenttype AS employment_type,
    salary_pool.salary_min AS salary_min,
    salary_pool.salary_max AS salary_max,
    salary_pool.salary_text AS salary_text,
    required_pool.required_skills AS required_skills,
    preferred_pool.preferred_skills AS preferred_skills,
    '基本的な開発経験 / チーム開発経験' AS requirements,
    '社会保険完備 / 交通費支給 / 在宅手当' AS benefits,
    tags_pool.tags AS tags,
    remote_pool.remote AS remote,
    'PUBLISHED'::jobstatus AS status,
    (random() < 0.05) AS featured,
    NULL AS embedding,
    jsonb_build_object('source', 'dummy_seed', 'batch', 'seed_jobs_10k')::text AS meta_data,
    (now() - (random() * interval '90 days')) AS posted_date,
    now() AS created_at,
    now() AS updated_at
FROM generate_series(1, 10000) AS gs
CROSS JOIN LATERAL (
    SELECT id AS employer_id
    FROM users
    WHERE role::text = 'employer' OR role::text = 'EMPLOYER'
    ORDER BY random()
    LIMIT 1
) AS employer
CROSS JOIN LATERAL (
    SELECT unnest(ARRAY[
        'バックエンドエンジニア',
        'フロントエンドエンジニア',
        'フルスタックエンジニア',
        'データエンジニア',
        '機械学習エンジニア',
        'インフラエンジニア',
        'SRE',
        'モバイルエンジニア',
        'プロダクトマネージャー',
        'UI/UXデザイナー'
    ]) AS title
    ORDER BY random()
    LIMIT 1
) AS title_pool
CROSS JOIN LATERAL (
    SELECT unnest(ARRAY[
        '株式会社テックイノベーション',
        '株式会社デジタルクリエイト',
        '株式会社ネクストソリューション',
        '株式会社クラウドワークス',
        '株式会社システムリンク',
        '株式会社スマートビジョン'
    ]) AS company
    ORDER BY random()
    LIMIT 1
) AS company_pool
CROSS JOIN LATERAL (
    SELECT unnest(ARRAY[
        '東京都渋谷区',
        '東京都港区',
        '東京都新宿区',
        '大阪府大阪市',
        '愛知県名古屋市',
        '福岡県福岡市',
        'リモート'
    ]) AS location
    ORDER BY random()
    LIMIT 1
) AS location_pool
CROSS JOIN LATERAL (
    SELECT unnest(ARRAY[
        'full-time',
        'part-time',
        'contract',
        'internship'
    ]) AS employment_type
    ORDER BY random()
    LIMIT 1
) AS employment_pool
CROSS JOIN LATERAL (
    SELECT
        (400 + (random() * 600)::int) AS salary_min,
        (800 + (random() * 900)::int) AS salary_max,
        format('%s〜%s万円', (400 + (random() * 600)::int), (800 + (random() * 900)::int)) AS salary_text
) AS salary_pool
CROSS JOIN LATERAL (
    SELECT unnest(ARRAY[
        'Python',
        'JavaScript',
        'TypeScript',
        'Java',
        'Go',
        'AWS',
        'GCP',
        'React',
        'Docker',
        'PostgreSQL'
    ]) AS primary_skill
    ORDER BY random()
    LIMIT 1
) AS stack_pool
CROSS JOIN LATERAL (
    SELECT jsonb_build_array(
        stack_pool.primary_skill,
        'Git',
        'CI/CD'
    )::text AS required_skills
) AS required_pool
CROSS JOIN LATERAL (
    SELECT jsonb_build_array(
        'Kubernetes',
        'Terraform',
        'Redis'
    )::text AS preferred_skills
) AS preferred_pool
CROSS JOIN LATERAL (
    SELECT jsonb_build_array(
        '自社開発',
        'B2B',
        'クラウド',
        '成長中'
    )::text AS tags
) AS tags_pool
CROSS JOIN LATERAL (
    SELECT (random() < 0.6) AS remote
) AS remote_pool
WHERE EXISTS (SELECT 1 FROM users WHERE role::text = 'employer' OR role::text = 'EMPLOYER');
