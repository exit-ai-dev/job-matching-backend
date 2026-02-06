#!/usr/bin/env python3
"""
Insert dummy data into the job-matching PostgreSQL database.

Usage:
  python insert_dummy_data.py
  python insert_dummy_data.py --reset   # truncates tables first (CASCADE)

Connection:
  Uses DATABASE_URL env var, or falls back to individual env vars:
  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
"""

import os
import json
import uuid
import random
import argparse
from datetime import datetime
from urllib.parse import urlparse

import psycopg2
from psycopg2.extras import execute_values


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


def connect():
    """Connect to database using DATABASE_URL or individual env vars."""
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        parsed = urlparse(database_url)
        return psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            dbname=parsed.path.lstrip("/"),
            user=parsed.username,
            password=parsed.password,
            sslmode="require"
        )
    else:
        return psycopg2.connect(
            host=env("DB_HOST", "localhost"),
            port=int(env("DB_PORT", "5432")),
            dbname=env("DB_NAME", "jobmatch"),
            user=env("DB_USER", "devuser"),
            password=env("DB_PASSWORD", "devpass"),
        )


def now_utc():
    return datetime.utcnow()


def random_email(prefix: str) -> str:
    return f"{prefix}.{uuid.uuid4().hex[:10]}@example.com"


def reset_db(cur):
    """Truncate tables in dependency-safe order."""
    tables = [
        "applications",
        "scouts",
        "resumes",
        "chat_sessions",
        "conversation_logs",
        "conversation_sessions",
        "user_preferences_profile",
        "usage_tracking",
        "payment_history",
        "subscriptions",
        "jobs",
        "users",
    ]
    for t in tables:
        try:
            cur.execute(f'TRUNCATE TABLE "{t}" RESTART IDENTITY CASCADE;')
            print(f"  Truncated: {t}")
        except Exception as e:
            print(f"  Skip {t}: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true", help="truncate tables before inserting")
    ap.add_argument("--seekers", type=int, default=10, help="number of seeker users")
    ap.add_argument("--employers", type=int, default=5, help="number of employer users")
    ap.add_argument("--jobs", type=int, default=20, help="number of job postings")
    args = ap.parse_args()

    random.seed(42)

    conn = connect()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            if args.reset:
                print("Resetting database...")
                reset_db(cur)
                print()

            # ---------------------------------
            # 1) Seeker Users
            # ---------------------------------
            print(f"Creating {args.seekers} seeker users...")
            seeker_ids = []

            skills_pool = ["Python", "JavaScript", "TypeScript", "React", "Vue.js", "Node.js",
                          "Java", "Go", "Ruby", "PHP", "AWS", "GCP", "Docker", "Kubernetes",
                          "SQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch"]
            locations = ["東京都", "神奈川県", "大阪府", "愛知県", "福岡県", "北海道", "京都府", "兵庫県"]

            for i in range(args.seekers):
                uid = str(uuid.uuid4())
                seeker_ids.append(uid)

                user_skills = ", ".join(random.sample(skills_pool, random.randint(3, 6)))
                exp_years = str(random.randint(1, 15))
                salary_min = str(random.randint(400, 800))
                salary_max = str(random.randint(800, 1500))

                cur.execute("""
                    INSERT INTO users (
                        id, email, password_hash, name, role,
                        skills, experience_years, desired_salary_min, desired_salary_max,
                        desired_location, desired_employment_type,
                        is_active, is_verified, subscription_tier
                    ) VALUES (%s, %s, %s, %s, 'SEEKER',
                        %s, %s, %s, %s, %s, %s,
                        true, true, 'free')
                """, (
                    uid,
                    random_email("seeker"),
                    "dummy_password_hash",
                    f"求職者 {i+1}",
                    user_skills,
                    exp_years,
                    salary_min,
                    salary_max,
                    random.choice(locations),
                    random.choice(["FULL_TIME", "CONTRACT"])
                ))

            print(f"  Created {len(seeker_ids)} seekers")

            # ---------------------------------
            # 2) Employer Users
            # ---------------------------------
            print(f"Creating {args.employers} employer users...")
            employer_ids = []

            industries = ["IT・通信", "金融", "製造", "小売", "医療・福祉", "教育", "コンサルティング"]
            company_sizes = ["1-10", "11-50", "51-200", "201-500", "501-1000", "1000+"]

            for i in range(args.employers):
                uid = str(uuid.uuid4())
                employer_ids.append(uid)

                company_name = f"株式会社テスト企業{i+1}"

                cur.execute("""
                    INSERT INTO users (
                        id, email, password_hash, name, role,
                        company_name, industry, company_size, company_description,
                        company_location,
                        is_active, is_verified, subscription_tier
                    ) VALUES (%s, %s, %s, %s, 'EMPLOYER',
                        %s, %s, %s, %s, %s,
                        true, true, 'free')
                """, (
                    uid,
                    random_email("employer"),
                    "dummy_password_hash",
                    f"採用担当 {i+1}",
                    company_name,
                    random.choice(industries),
                    random.choice(company_sizes),
                    f"{company_name}は革新的な企業です。一緒に成長しませんか？",
                    random.choice(locations)
                ))

            print(f"  Created {len(employer_ids)} employers")

            # ---------------------------------
            # 3) Jobs
            # ---------------------------------
            print(f"Creating {args.jobs} job postings...")
            job_ids = []

            job_titles = [
                "バックエンドエンジニア", "フロントエンドエンジニア", "フルスタックエンジニア",
                "データサイエンティスト", "機械学習エンジニア", "インフラエンジニア",
                "SREエンジニア", "QAエンジニア", "プロダクトマネージャー",
                "UIデザイナー", "UXデザイナー", "プロジェクトマネージャー"
            ]

            employment_types = ["FULL_TIME", "PART_TIME", "CONTRACT", "INTERNSHIP"]

            for i in range(args.jobs):
                jid = str(uuid.uuid4())
                job_ids.append(jid)

                employer_id = random.choice(employer_ids)
                title = random.choice(job_titles)
                salary_min = random.randint(4000000, 8000000)
                salary_max = salary_min + random.randint(1000000, 4000000)

                required = ", ".join(random.sample(skills_pool, random.randint(2, 4)))
                preferred = ", ".join(random.sample(skills_pool, random.randint(1, 3)))

                cur.execute("""
                    INSERT INTO jobs (
                        id, employer_id, title, company, description, location,
                        employment_type, salary_min, salary_max, salary_text,
                        required_skills, preferred_skills, requirements, benefits,
                        remote, status, featured
                    ) VALUES (%s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, 'PUBLISHED', %s)
                """, (
                    jid,
                    employer_id,
                    title,
                    f"株式会社テスト企業{random.randint(1, args.employers)}",
                    f"""【{title}】を募集しています。

■ 仕事内容
・新規サービスの開発・運用
・既存システムの改善・機能追加
・技術選定・アーキテクチャ設計

■ 求める人物像
・チームで協力して働ける方
・新しい技術に興味がある方
・ユーザー目線でプロダクトを考えられる方""",
                    random.choice(locations),
                    random.choice(employment_types),
                    salary_min,
                    salary_max,
                    f"年収 {salary_min//10000}万円 〜 {salary_max//10000}万円",
                    required,
                    preferred,
                    f"・{title}としての実務経験2年以上\n・{required.split(',')[0].strip()}の経験",
                    "・フレックスタイム制\n・リモートワーク可\n・各種社会保険完備\n・書籍購入補助",
                    random.choice([True, False]),
                    random.choice([True, False])
                ))

            print(f"  Created {len(job_ids)} jobs")

            # ---------------------------------
            # 4) User Preferences Profile
            # ---------------------------------
            print("Creating user preference profiles...")

            for uid in seeker_ids:
                cur.execute("""
                    INSERT INTO user_preferences_profile (
                        user_id, job_title, location_prefecture,
                        salary_min, salary_max, remote_work_preference,
                        employment_type
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO NOTHING
                """, (
                    uid,
                    random.choice(job_titles),
                    random.choice(locations),
                    random.randint(400, 800) * 10000,
                    random.randint(800, 1500) * 10000,
                    random.choice(["remote", "hybrid", "onsite"]),
                    random.choice(["正社員", "契約社員", "業務委託"])
                ))

            print(f"  Created {len(seeker_ids)} preference profiles")

            # ---------------------------------
            # 5) Chat Sessions (for Iizumi logic)
            # ---------------------------------
            print("Creating chat sessions...")

            session_count = 0
            for uid in seeker_ids[:5]:  # First 5 seekers get chat sessions
                sid = str(uuid.uuid4())
                session_data = {
                    "session_id": sid,
                    "user_id": uid,
                    "turn_count": random.randint(1, 8),
                    "current_score": random.uniform(30, 85),
                    "preferences": {
                        "job_title": random.choice(job_titles),
                        "location": random.choice(locations)
                    }
                }

                cur.execute("""
                    INSERT INTO chat_sessions (session_id, user_id, session_data)
                    VALUES (%s, %s, %s)
                """, (sid, uid, json.dumps(session_data)))
                session_count += 1

            print(f"  Created {session_count} chat sessions")

            # ---------------------------------
            # 6) Applications
            # ---------------------------------
            print("Creating job applications...")

            app_count = 0
            for uid in seeker_ids:
                # Each seeker applies to 1-3 jobs
                applied_jobs = random.sample(job_ids, min(random.randint(1, 3), len(job_ids)))
                for jid in applied_jobs:
                    cur.execute("""
                        INSERT INTO applications (
                            id, seeker_id, job_id, status, cover_letter
                        ) VALUES (%s, %s, %s, %s, %s)
                    """, (
                        str(uuid.uuid4()),
                        uid,
                        jid,
                        random.choice(["SCREENING", "INTERVIEW", "OFFERED", "REJECTED"]),
                        "志望動機：貴社のビジョンに共感し、ぜひ一緒に働きたいと考えております。"
                    ))
                    app_count += 1

            print(f"  Created {app_count} applications")

            # ---------------------------------
            # 7) Scouts
            # ---------------------------------
            print("Creating scout messages...")

            scout_count = 0
            for eid in employer_ids:
                # Each employer scouts 2-4 seekers
                scouted = random.sample(seeker_ids, min(random.randint(2, 4), len(seeker_ids)))
                for uid in scouted:
                    jid = random.choice(job_ids)
                    cur.execute("""
                        INSERT INTO scouts (
                            id, employer_id, seeker_id, job_id,
                            title, message, match_score, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        str(uuid.uuid4()),
                        eid,
                        uid,
                        jid,
                        "スカウトのご案内",
                        "あなたのスキルに魅力を感じ、ぜひお話させていただきたいと思いご連絡しました。",
                        random.randint(70, 95),
                        random.choice(["NEW", "READ", "REPLIED"])
                    ))
                    scout_count += 1

            print(f"  Created {scout_count} scouts")

        conn.commit()
        print()
        print("Dummy data inserted successfully!")
        print(f"   Seekers: {len(seeker_ids)}")
        print(f"   Employers: {len(employer_ids)}")
        print(f"   Jobs: {len(job_ids)}")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
