#!/usr/bin/env python3
"""
Insert dummy data into the unified_job_matching PostgreSQL schema.

Usage:
  python insert_dummy_data.py
  python insert_dummy_data.py --reset   # truncates all tables first (CASCADE)

Connection is read from env vars (matches backend/.env defaults):
  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
"""

import os
import json
import uuid
import random
import argparse
from datetime import datetime, date, timedelta

import psycopg2
from psycopg2.extras import execute_values


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


def connect():
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
    # Truncate in a dependency-safe way.
    tables = [
        "job_attributes",
        "job_additional_answers",
        "user_interactions",
        "missing_job_info_log",
        "company_enrichment_requests",
        "scout_messages",
        "user_question_responses",
        "company_profile",
        "company_date",
        "user_profile",
        "user_preferences_profile",
        "user_personality_analysis",
        "user_sessions",
        "conversation_logs",
        "conversation_sessions",
        "conversation_turns",
        "user_insights",
        "score_history",
        "chat_history",
        "search_history",
        "global_preference_trends",
        "trend_thresholds",
        "current_weekly_trends",
        "baseline_job_fields",
        "dynamic_questions",
        "chat_sessions",
        "personal_date",
    ]
    for t in tables:
        cur.execute(f'TRUNCATE TABLE "{t}" RESTART IDENTITY CASCADE;')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true", help="truncate all tables before inserting")
    ap.add_argument("--users", type=int, default=10)
    ap.add_argument("--companies", type=int, default=5)
    ap.add_argument("--jobs", type=int, default=12)
    args = ap.parse_args()

    random.seed(42)

    conn = connect()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            if args.reset:
                reset_db(cur)

            # ---------------------------------
            # 1) Users (personal_date)
            # ---------------------------------
            users = []
            for i in range(args.users):
                users.append((
                    f"User {i+1}",
                    random_email("user"),
                    "dummy_password_hash",
                    random.randint(18, 55),
                    random.choice(["male", "female", "other"]),
                    f"090-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                ))

            execute_values(
                cur,
                """
                INSERT INTO personal_date (name, email, password, age, gender, phone)
                VALUES %s
                RETURNING user_id
                """,
                users
            )
            user_ids = [r[0] for r in cur.fetchall()]

            # ---------------------------------
            # 2) Companies (company_date)
            # ---------------------------------
            companies = []
            for i in range(args.companies):
                companies.append((
                    f"Company {i+1}",
                    random_email("company"),
                    "dummy_password_hash",
                    random.choice(["IT", "HR", "Finance", "Retail", "Healthcare"]),
                    random.choice(["10-50", "51-200", "201-1000"]),
                    random.randint(1995, 2022),
                    "https://example.com",
                    "Dummy company description.",
                ))

            execute_values(
                cur,
                """
                INSERT INTO company_date
                  (company_name, email, password, industry, company_size, founded_year, website_url, description)
                VALUES %s
                RETURNING company_id
                """,
                companies
            )
            company_ids = [r[0] for r in cur.fetchall()]

            # ---------------------------------
            # 3) Jobs (company_profile)
            # ---------------------------------
            job_rows = []
            for i in range(args.jobs):
                cid = random.choice(company_ids)
                job_rows.append((
                    cid,
                    random.choice(["Backend Engineer", "Frontend Engineer", "Data Analyst", "Sales", "PM"]),
                    "This is a dummy job description.",
                    random.choice(["Tokyo", "Saitama", "Kanagawa", "Chiba"]),
                    random.choice(["Shibuya", "Shinjuku", "Omiya", "Yokohama"]),
                    random.randint(300, 600) * 10000,
                    random.randint(600, 1200) * 10000,
                    random.choice(["正社員", "契約社員", "アルバイト"]),
                    random.choice(["remote", "hybrid", "onsite"]),
                    random.choice([True, False]),
                    random.choice([None, "09:00", "10:00", "11:00"]),
                    random.choice([True, False]),
                    random.choice(["3-5", "6-10", "11-30"]),
                    random.choice(["Scrum", "Kanban", "Waterfall"]),
                    json.dumps({"languages": ["Python", "TypeScript"], "frameworks": ["FastAPI", "React"]}),
                    ["Python", "SQL"],
                    ["Docker", "AWS"],
                    ["Health insurance", "Remote stipend"],
                    "Work style details (dummy).",
                    "Team culture details (dummy).",
                    "Growth opportunities (dummy).",
                    "Benefits details (dummy).",
                    "Office environment (dummy).",
                    "Project details (dummy).",
                    "Company appeal text (dummy).",
                    json.dumps({"extracted": True, "keywords": ["dummy"]}),
                    json.dumps([{"q": "dummy question", "type": "text"}]),
                    None,  # embedding (vector) left NULL
                    "active",
                    random.randint(0, 100),
                    random.randint(0, 100),
                    random.randint(0, 50),
                    random.randint(0, 20),
                ))

            execute_values(
                cur,
                """
                INSERT INTO company_profile
                  (company_id, job_title, job_description, location_prefecture, location_city,
                   salary_min, salary_max, employment_type, remote_option,
                   flex_time, latest_start_time, side_job_allowed, team_size, development_method,
                   tech_stack, required_skills, preferred_skills, benefits,
                   work_style_details, team_culture_details, growth_opportunities_details,
                   benefits_details, office_environment_details, project_details,
                   company_appeal_text, ai_extracted_features, additional_questions, embedding,
                   status, view_count, click_count, favorite_count, apply_count)
                VALUES %s
                RETURNING id
                """,
                job_rows
            )
            job_ids = [r[0] for r in cur.fetchall()]

            # ---------------------------------
            # 4) Per-user profile tables (1:1-ish)
            # ---------------------------------
            profile_rows = []
            pref_rows = []
            personality_rows = []
            for uid in user_ids:
                profile_rows.append((
                    uid,
                    random.choice(["Engineer", "Designer", "Analyst", "Sales"]),
                    random.randint(0, 15),
                    ["Python", "SQL", "Communication"],
                    random.choice(["HighSchool", "Bachelor", "Master"]),
                    random.choice(["Tokyo", "Saitama", "Kanagawa", "Chiba"]),
                    random.choice(["Shibuya", "Shinjuku", "Omiya", "Yokohama"]),
                    random.randint(300, 600) * 10000,
                    random.randint(600, 1200) * 10000,
                    random.choice(["remote", "hybrid", "onsite"]),
                ))
                pref_rows.append((
                    uid,
                    random.choice(["Backend Engineer", "Data Analyst", "PM"]),
                    random.choice(["Tokyo", "Saitama", "Kanagawa", "Chiba"]),
                    random.choice(["Shibuya", "Shinjuku", "Omiya", "Yokohama"]),
                    random.randint(300, 600) * 10000,
                    random.randint(600, 1200) * 10000,
                    random.choice(["remote", "hybrid", "onsite"]),
                    random.choice(["正社員", "契約社員", "アルバイト"]),
                    ["IT", "Finance"],
                    random.choice(["8h/day", "flex"]),
                    random.choice(["10-50", "51-200", "201-1000"]),
                ))
                personality_rows.append((
                    uid,
                    json.dumps({"traits": ["curious", "teamwork"]}),
                    json.dumps({"values": ["growth", "impact"]}),
                    random.choice(["direct", "friendly", "analytical"]),
                    json.dumps({"notes": "dummy"}),
                ))

            execute_values(
                cur,
                """
                INSERT INTO user_profile
                  (user_id, job_title, years_of_experience, skills, education_level,
                   location_prefecture, location_city, salary_min, salary_max, work_style_preference)
                VALUES %s
                ON CONFLICT (user_id) DO NOTHING
                """,
                profile_rows
            )

            execute_values(
                cur,
                """
                INSERT INTO user_preferences_profile
                  (user_id, job_title, location_prefecture, location_city, salary_min, salary_max,
                   remote_work_preference, employment_type, industry_preferences, work_hours_preference, company_size_preference)
                VALUES %s
                ON CONFLICT (user_id) DO NOTHING
                """,
                pref_rows
            )

            execute_values(
                cur,
                """
                INSERT INTO user_personality_analysis
                  (user_id, personality_traits, work_values, communication_style, analysis_details)
                VALUES %s
                """,
                personality_rows
            )

            # ---------------------------------
            # 5) Dynamic questions + responses
            # ---------------------------------
            questions = [
                ("リモート希望ですか？", "choice", "work_style", json.dumps({"options": ["remote", "hybrid", "onsite"]}), "onboarding"),
                ("得意スキルは？", "text", "skills", json.dumps({"hint": "Python, SQL など"}), "onboarding"),
                ("年収希望は？", "number", "salary", json.dumps({"unit": "JPY"}), "onboarding"),
            ]
            execute_values(
                cur,
                """
                INSERT INTO dynamic_questions (question_text, question_type, target_context, options, usage_context)
                VALUES %s
                RETURNING id
                """,
                questions
            )
            question_ids = [r[0] for r in cur.fetchall()]

            resp_rows = []
            for uid in user_ids:
                for qid in question_ids:
                    resp_rows.append((
                        uid,
                        qid,
                        random.choice(["remote", "hybrid", "Python", "SQL", "6000000"]),
                        json.dumps({"dummy": True}),
                    ))
            execute_values(
                cur,
                """
                INSERT INTO user_question_responses (user_id, question_id, response_text, response_data)
                VALUES %s
                """,
                resp_rows
            )

            # ---------------------------------
            # 6) Sessions & chat logs
            # ---------------------------------
            session_ids = []
            us_rows = []
            for uid in user_ids:
                sid = str(uuid.uuid4())
                session_ids.append(sid)
                us_rows.append((sid, uid, json.dumps({"turn_count": 0, "current_score": 0.0})))
            execute_values(
                cur,
                """
                INSERT INTO user_sessions (session_id, user_id, session_data)
                VALUES %s
                """,
                us_rows
            )

            # chat_sessions (separate table used by backend/utils/session_manager.py; user_id stored as string)
            cs_rows = []
            for sid, uid in zip(session_ids, user_ids):
                cs_rows.append((sid, str(uid), json.dumps({"session_id": sid, "user_id": uid, "note": "dummy"})))
            execute_values(
                cur,
                """
                INSERT INTO chat_sessions (session_id, user_id, session_data)
                VALUES %s
                """,
                cs_rows
            )

            # conversation_sessions
            conv_s_rows = []
            for sid, uid in zip(session_ids, user_ids):
                conv_s_rows.append((uid, sid, random.randint(1, 8), random.choice(["score_reached", "max_turns", "user_request"])))
            execute_values(
                cur,
                """
                INSERT INTO conversation_sessions (user_id, session_id, total_turns, end_reason)
                VALUES %s
                ON CONFLICT (session_id) DO NOTHING
                """,
                conv_s_rows
            )

            # conversation_logs / chat_history / conversation_turns / score_history / user_insights / search_history
            log_rows = []
            chat_hist_rows = []
            turns_rows = []
            score_rows = []
            insights_rows = []
            search_rows = []
            for sid, uid in zip(session_ids, user_ids):
                for turn in range(1, 4):
                    user_msg = f"Dummy user message {turn}"
                    ai_msg = f"Dummy AI response {turn}"
                    log_rows.append((sid, uid, turn, user_msg, ai_msg, json.dumps({"match_score": random.random()})))
                    chat_hist_rows.append((uid, sid, "user", user_msg))
                    chat_hist_rows.append((uid, sid, "ai", ai_msg))
                    turns_rows.append((
                        uid, sid, turn, user_msg, ai_msg,
                        json.dumps({"score": random.randint(0, 100)}),
                        float(random.randint(50, 95)),
                        float(random.randint(50, 95)),
                        random.randint(1, 20)
                    ))
                    score_rows.append((
                        uid, sid, turn, str(random.choice(job_ids)),
                        float(random.randint(50, 95)),
                        float(random.randint(50, 95)),
                        json.dumps({"reason": "dummy"})
                    ))
                insights_rows.append((uid, sid, json.dumps({"summary": "dummy insights"})))
                search_rows.append((uid, "dummy search", json.dumps({"remote": True}), random.randint(0, 20)))

            execute_values(
                cur,
                """
                INSERT INTO conversation_logs
                  (session_id, user_id, turn_number, user_message, ai_response, extracted_intent)
                VALUES %s
                """,
                log_rows
            )
            execute_values(
                cur,
                """
                INSERT INTO chat_history (user_id, session_id, sender, message)
                VALUES %s
                """,
                chat_hist_rows
            )
            execute_values(
                cur,
                """
                INSERT INTO conversation_turns
                  (user_id, session_id, turn_number, user_message, bot_message, extracted_info,
                   top_score, top_match_percentage, candidate_count)
                VALUES %s
                """,
                turns_rows
            )
            execute_values(
                cur,
                """
                INSERT INTO score_history
                  (user_id, session_id, turn_number, job_id, score, match_percentage, score_details)
                VALUES %s
                """,
                score_rows
            )
            execute_values(
                cur,
                """
                INSERT INTO user_insights (user_id, session_id, insights)
                VALUES %s
                """,
                insights_rows
            )
            execute_values(
                cur,
                """
                INSERT INTO search_history (user_id, search_query, filters, results_count)
                VALUES %s
                """,
                search_rows
            )

            # ---------------------------------
            # 7) Job attribute / extra question tables
            # ---------------------------------
            attr_rows = []
            add_ans_rows = []
            for jid in job_ids:
                for k in ["must_have_skills", "culture", "process"]:
                    attr_rows.append((jid, k, "dummy", "text"))
                add_ans_rows.append((jid, "追加質問: 勤務開始可能時期は？", "すぐに可能", 1))

            execute_values(
                cur,
                """
                INSERT INTO job_attributes
                  (job_id, attribute_name, attribute_value, attribute_type)
                VALUES %s
                """,
                attr_rows
            )
            execute_values(
                cur,
                """
                INSERT INTO job_additional_answers
                  (job_id, question_text, answer_text, question_order)
                VALUES %s
                """,
                add_ans_rows
            )

            # ---------------------------------
            # 8) Interaction / enrichment / scout message tables
            # ---------------------------------
            interaction_rows = []
            missing_rows = []
            enrich_rows = []
            scout_rows = []

            for uid in user_ids:
                jid = random.choice(job_ids)
                interaction_rows.append((uid, jid, random.choice(["view", "favorite", "apply"]), random.choice(session_ids), json.dumps({"dummy": True})))
                missing_rows.append((jid, uid, random.choice(["salary_max", "remote_option", "benefits"]), "chat"))

            for jid in job_ids[: min(6, len(job_ids))]:
                cid = random.choice(company_ids)
                enrich_rows.append((jid, cid, random.choice(["benefits", "process"]), "質問: 福利厚生は？", "text", random.randint(1, 10), random.randint(1, 5), "pending"))

            for _ in range(min(10, len(user_ids) * 2)):
                cid = random.choice(company_ids)
                jid = random.choice(job_ids)
                uid = random.choice(user_ids)
                scout_rows.append((
                    cid, jid, uid,
                    "スカウトのご案内",
                    "あなたにマッチしそうな求人があります。",
                    random.random(),
                    json.dumps({"reason": "dummy"}),
                    "sent",
                ))

            execute_values(
                cur,
                """
                INSERT INTO user_interactions (user_id, job_id, interaction_type, session_id, interaction_data)
                VALUES %s
                """,
                interaction_rows
            )
            execute_values(
                cur,
                """
                INSERT INTO missing_job_info_log (job_id, user_id, missing_field, detected_from)
                VALUES %s
                """,
                missing_rows
            )
            execute_values(
                cur,
                """
                INSERT INTO company_enrichment_requests
                  (job_id, company_id, missing_field, question_text, question_type, priority_score, detection_count, status)
                VALUES %s
                """,
                enrich_rows
            )
            execute_values(
                cur,
                """
                INSERT INTO scout_messages
                  (company_id, job_id, user_id, message_title, message_body, match_score, match_reasons, status)
                VALUES %s
                """,
                scout_rows
            )

            # ---------------------------------
            # 9) Trend-related tables (standalone)
            # ---------------------------------
            cur.execute(
                """
                INSERT INTO trend_thresholds (threshold_name, threshold_value, description)
                VALUES ('weekly_trigger', 10, 'dummy threshold')
                ON CONFLICT (threshold_name) DO UPDATE SET threshold_value = EXCLUDED.threshold_value
                """
            )
            cur.execute(
                """
                INSERT INTO global_preference_trends
                  (preference_key, preference_value, occurrence_count, unique_users, last_detected, trend_score, category)
                VALUES
                  ('remote_option', 'remote', 12, 7, NOW(), 0.75, 'work_style')
                """
            )
            cur.execute(
                """
                INSERT INTO current_weekly_trends (week_start, trend_data)
                VALUES (%s, %s)
                """,
                (date.today() - timedelta(days=date.today().weekday()), json.dumps({"top": ["remote", "Tokyo"]}))
            )
            cur.execute(
                """
                INSERT INTO baseline_job_fields
                  (field_name, field_type, label, question_template, options, placeholder, required, priority, category)
                VALUES
                  ('salary_min', 'int', '最低年収', '最低年収は？', NULL, '例: 400万円', true, 10, 'salary'),
                  ('salary_max', 'int', '最高年収', '最高年収は？', NULL, '例: 800万円', false, 5, 'salary')
                ON CONFLICT (field_name) DO NOTHING
                """
            )

        conn.commit()
        print("✅ Dummy data inserted successfully.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
