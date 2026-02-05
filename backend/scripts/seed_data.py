#!/usr/bin/env python
"""
ダミーデータ投入スクリプト
テーブル作成後にサンプルデータを投入します

使用方法:
  python scripts/seed_data.py

環境変数:
  DATABASE_URL: データベース接続URL
"""
import sys
import os
import uuid
from datetime import datetime, timedelta
import json

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal, get_engine
from app.db.base import Base
from app.models.user import User, UserRole
from app.models.job import Job
from app.models.application import Application
from app.models.scout import Scout
from app.models.company import Company
from app.models.company_profile import CompanyProfile
from app.models.user_preferences import UserPreferencesProfile

import bcrypt


def get_password_hash(password: str) -> str:
    """パスワードをハッシュ化"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def seed_users(db):
    """ユーザーデータを投入"""
    print("ユーザーデータを投入中...")

    users = [
        # 求職者
        {
            "id": str(uuid.uuid4()),
            "email": "seeker1@example.com",
            "password_hash": get_password_hash("password123"),
            "name": "山田 太郎",
            "role": UserRole.SEEKER,
            "skills": json.dumps(["Python", "JavaScript", "React", "AWS"]),
            "experience_years": "5",
            "desired_salary_min": "600",
            "desired_salary_max": "800",
            "desired_location": "東京",
            "desired_employment_type": "正社員",
            "profile_completion": "80",
        },
        {
            "id": str(uuid.uuid4()),
            "email": "seeker2@example.com",
            "password_hash": get_password_hash("password123"),
            "name": "佐藤 花子",
            "role": UserRole.SEEKER,
            "skills": json.dumps(["UI/UX", "Figma", "Adobe XD", "HTML/CSS"]),
            "experience_years": "3",
            "desired_salary_min": "500",
            "desired_salary_max": "700",
            "desired_location": "東京, 大阪",
            "desired_employment_type": "正社員",
            "profile_completion": "70",
        },
        {
            "id": str(uuid.uuid4()),
            "email": "seeker3@example.com",
            "password_hash": get_password_hash("password123"),
            "name": "鈴木 一郎",
            "role": UserRole.SEEKER,
            "skills": json.dumps(["Java", "Spring Boot", "MySQL", "Docker"]),
            "experience_years": "7",
            "desired_salary_min": "700",
            "desired_salary_max": "1000",
            "desired_location": "リモート",
            "desired_employment_type": "正社員",
            "profile_completion": "90",
        },
        # 企業
        {
            "id": str(uuid.uuid4()),
            "email": "employer1@example.com",
            "password_hash": get_password_hash("password123"),
            "name": "採用担当 A",
            "role": UserRole.EMPLOYER,
            "company_name": "株式会社テックイノベーション",
            "industry": "IT・通信",
            "company_size": "100-500名",
            "company_description": "AIとクラウド技術を活用したソリューションを提供するIT企業です。",
            "profile_completion": "100",
        },
        {
            "id": str(uuid.uuid4()),
            "email": "employer2@example.com",
            "password_hash": get_password_hash("password123"),
            "name": "採用担当 B",
            "role": UserRole.EMPLOYER,
            "company_name": "株式会社デジタルクリエイト",
            "industry": "Web・アプリ開発",
            "company_size": "50-100名",
            "company_description": "スタートアップ向けのWebアプリケーション開発を行っています。",
            "profile_completion": "100",
        },
    ]

    for user_data in users:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(**user_data)
            db.add(user)
            print(f"  + {user_data['email']} ({user_data['role'].value})")
        else:
            print(f"  - {user_data['email']} (既存)")

    db.commit()
    return db.query(User).filter(User.role == UserRole.EMPLOYER).all()


def seed_jobs(db, employers):
    """求人データを投入"""
    print("\n求人データを投入中...")

    jobs_data = [
        {
            "title": "シニアフルスタックエンジニア",
            "description": "当社のプロダクト開発チームで、フロントエンドからバックエンドまで幅広く開発を担当していただきます。",
            "company": "株式会社テックイノベーション",
            "location": "東京都渋谷区",
            "salary_min": 700,
            "salary_max": 1000,
            "employment_type": "full-time",
            "required_skills": ["Python", "React", "AWS", "Docker"],
            "preferred_skills": ["Kubernetes", "GraphQL"],
            "remote": True,
            "status": "published",
        },
        {
            "title": "フロントエンドエンジニア（React）",
            "description": "ユーザー向けWebアプリケーションのフロントエンド開発を担当していただきます。モダンな開発環境で働けます。",
            "company": "株式会社テックイノベーション",
            "location": "東京都渋谷区",
            "salary_min": 500,
            "salary_max": 750,
            "employment_type": "full-time",
            "required_skills": ["React", "TypeScript", "HTML/CSS"],
            "preferred_skills": ["Next.js", "Tailwind CSS"],
            "remote": True,
            "status": "published",
        },
        {
            "title": "バックエンドエンジニア（Python）",
            "description": "AIプロダクトのバックエンドAPI開発を担当していただきます。大規模データ処理の経験がある方歓迎。",
            "company": "株式会社テックイノベーション",
            "location": "東京都渋谷区",
            "salary_min": 600,
            "salary_max": 900,
            "employment_type": "full-time",
            "required_skills": ["Python", "FastAPI", "PostgreSQL"],
            "preferred_skills": ["機械学習", "Redis"],
            "remote": True,
            "status": "published",
        },
        {
            "title": "UI/UXデザイナー",
            "description": "自社プロダクトのUI/UXデザインを担当していただきます。エンジニアと協力して、使いやすいプロダクトを作りましょう。",
            "company": "株式会社デジタルクリエイト",
            "location": "東京都港区",
            "salary_min": 450,
            "salary_max": 700,
            "employment_type": "full-time",
            "required_skills": ["Figma", "UI/UX", "Adobe XD"],
            "preferred_skills": ["フロントエンド開発", "プロトタイピング"],
            "remote": True,
            "status": "published",
        },
        {
            "title": "プロジェクトマネージャー",
            "description": "クライアントワークのプロジェクトマネジメントを担当していただきます。技術理解のある方を求めています。",
            "company": "株式会社デジタルクリエイト",
            "location": "東京都港区",
            "salary_min": 600,
            "salary_max": 850,
            "employment_type": "full-time",
            "required_skills": ["プロジェクト管理", "アジャイル", "コミュニケーション"],
            "preferred_skills": ["エンジニア経験", "PMP"],
            "remote": False,
            "status": "published",
        },
        {
            "title": "Javaエンジニア（業務システム）",
            "description": "大手企業向け業務システムの開発・保守を担当していただきます。安定した環境で働けます。",
            "company": "株式会社テックイノベーション",
            "location": "大阪府大阪市",
            "salary_min": 500,
            "salary_max": 800,
            "employment_type": "full-time",
            "required_skills": ["Java", "Spring Boot", "Oracle"],
            "preferred_skills": ["AWS", "CI/CD"],
            "remote": False,
            "status": "published",
        },
        {
            "title": "インフラエンジニア（AWS）",
            "description": "AWSを中心としたクラウドインフラの設計・構築・運用を担当していただきます。",
            "company": "株式会社テックイノベーション",
            "location": "東京都渋谷区",
            "salary_min": 600,
            "salary_max": 900,
            "employment_type": "full-time",
            "required_skills": ["AWS", "Terraform", "Linux"],
            "preferred_skills": ["Kubernetes", "監視ツール"],
            "remote": True,
            "status": "published",
        },
        {
            "title": "データエンジニア",
            "description": "データ基盤の設計・構築、データパイプラインの開発を担当していただきます。",
            "company": "株式会社デジタルクリエイト",
            "location": "東京都港区",
            "salary_min": 550,
            "salary_max": 850,
            "employment_type": "full-time",
            "required_skills": ["Python", "SQL", "Airflow"],
            "preferred_skills": ["Spark", "BigQuery"],
            "remote": True,
            "status": "published",
        },
    ]

    employer_map = {e.company_name: e for e in employers}

    for job_data in jobs_data:
        employer = employer_map.get(job_data["company"])
        if not employer:
            continue

        existing = db.query(Job).filter(
            Job.title == job_data["title"],
            Job.employer_id == employer.id
        ).first()

        if not existing:
            job = Job(
                id=str(uuid.uuid4()),
                employer_id=employer.id,
                title=job_data["title"],
                description=job_data["description"],
                company=job_data["company"],
                location=job_data["location"],
                salary_min=job_data["salary_min"],
                salary_max=job_data["salary_max"],
                employment_type=job_data["employment_type"],
                required_skills=json.dumps(job_data["required_skills"]),
                preferred_skills=json.dumps(job_data["preferred_skills"]),
                remote=job_data["remote"],
                status=job_data["status"],
            )
            db.add(job)
            print(f"  + {job_data['title']}")
        else:
            print(f"  - {job_data['title']} (既存)")

    db.commit()


def seed_companies(db):
    """企業データを投入（company_date テーブル）"""
    print("\n企業データ（company_date）を投入中...")

    companies = [
        {
            "company_id": str(uuid.uuid4()),
            "company_name": "株式会社テックイノベーション",
            "email": "contact@tech-innovation.co.jp",
            "password": get_password_hash("company123"),
            "industry": "IT・通信",
            "company_size": "100-500名",
            "founded_year": 2015,
            "website_url": "https://tech-innovation.co.jp",
            "description": "AIとクラウド技術を活用したソリューションを提供するIT企業です。",
        },
        {
            "company_id": str(uuid.uuid4()),
            "company_name": "株式会社デジタルクリエイト",
            "email": "contact@digital-create.co.jp",
            "password": get_password_hash("company123"),
            "industry": "Web・アプリ開発",
            "company_size": "50-100名",
            "founded_year": 2018,
            "website_url": "https://digital-create.co.jp",
            "description": "スタートアップ向けのWebアプリケーション開発を行っています。",
        },
    ]

    created_companies = []
    for company_data in companies:
        existing = db.query(Company).filter(Company.email == company_data["email"]).first()
        if not existing:
            company = Company(**company_data)
            db.add(company)
            created_companies.append(company)
            print(f"  + {company_data['company_name']}")
        else:
            created_companies.append(existing)
            print(f"  - {company_data['company_name']} (既存)")

    db.commit()
    return created_companies


def seed_company_profiles(db, companies):
    """求人データを投入（company_profile テーブル - マッチング用）"""
    print("\n求人データ（company_profile）を投入中...")

    company_map = {c.company_name: c for c in companies}

    profiles_data = [
        {
            "company_name": "株式会社テックイノベーション",
            "job_title": "シニアフルスタックエンジニア",
            "job_description": "当社のプロダクト開発チームで、フロントエンドからバックエンドまで幅広く開発を担当していただきます。",
            "location_prefecture": "東京都",
            "location_city": "渋谷区",
            "salary_min": 700,
            "salary_max": 1000,
            "employment_type": "正社員",
            "remote_option": "フルリモート可",
            "flex_time": True,
            "tech_stack": {"languages": ["Python", "TypeScript"], "frameworks": ["React", "FastAPI"]},
            "required_skills": ["Python", "React", "AWS", "Docker"],
            "preferred_skills": ["Kubernetes", "GraphQL"],
            "team_size": "5-10名",
            "work_style_details": "フルリモートで働けます。週1回のチームミーティングあり。",
            "status": "active",
        },
        {
            "company_name": "株式会社テックイノベーション",
            "job_title": "バックエンドエンジニア（Python）",
            "job_description": "AIプロダクトのバックエンドAPI開発を担当していただきます。",
            "location_prefecture": "東京都",
            "location_city": "渋谷区",
            "salary_min": 600,
            "salary_max": 900,
            "employment_type": "正社員",
            "remote_option": "フルリモート可",
            "flex_time": True,
            "tech_stack": {"languages": ["Python"], "frameworks": ["FastAPI", "Django"]},
            "required_skills": ["Python", "FastAPI", "PostgreSQL"],
            "preferred_skills": ["機械学習", "Redis"],
            "team_size": "5-10名",
            "status": "active",
        },
        {
            "company_name": "株式会社デジタルクリエイト",
            "job_title": "UI/UXデザイナー",
            "job_description": "自社プロダクトのUI/UXデザインを担当していただきます。",
            "location_prefecture": "東京都",
            "location_city": "港区",
            "salary_min": 450,
            "salary_max": 700,
            "employment_type": "正社員",
            "remote_option": "週2-3日リモート",
            "flex_time": True,
            "tech_stack": {"tools": ["Figma", "Adobe XD"]},
            "required_skills": ["Figma", "UI/UX", "Adobe XD"],
            "preferred_skills": ["フロントエンド開発", "プロトタイピング"],
            "team_size": "3-5名",
            "status": "active",
        },
    ]

    for profile_data in profiles_data:
        company = company_map.get(profile_data["company_name"])
        if not company:
            continue

        existing = db.query(CompanyProfile).filter(
            CompanyProfile.job_title == profile_data["job_title"],
            CompanyProfile.company_id == company.company_id
        ).first()

        if not existing:
            profile = CompanyProfile(
                id=str(uuid.uuid4()),
                company_id=company.company_id,
                job_title=profile_data["job_title"],
                job_description=profile_data["job_description"],
                location_prefecture=profile_data["location_prefecture"],
                location_city=profile_data.get("location_city"),
                salary_min=profile_data["salary_min"],
                salary_max=profile_data["salary_max"],
                employment_type=profile_data.get("employment_type", "正社員"),
                remote_option=profile_data.get("remote_option"),
                flex_time=profile_data.get("flex_time", False),
                tech_stack=profile_data.get("tech_stack"),
                required_skills=profile_data.get("required_skills"),
                preferred_skills=profile_data.get("preferred_skills"),
                team_size=profile_data.get("team_size"),
                work_style_details=profile_data.get("work_style_details"),
                status=profile_data.get("status", "active"),
            )
            db.add(profile)
            print(f"  + {profile_data['job_title']}")
        else:
            print(f"  - {profile_data['job_title']} (既存)")

    db.commit()


def seed_user_preferences(db):
    """ユーザー希望条件を投入（user_preferences_profile テーブル）"""
    print("\nユーザー希望条件（user_preferences_profile）を投入中...")

    # 既存の求職者ユーザーを取得
    seekers = db.query(User).filter(User.role == UserRole.SEEKER).all()

    preferences_map = {
        "seeker1@example.com": {
            "job_title": "フルスタックエンジニア",
            "location_prefecture": "東京都",
            "salary_min": 600,
            "salary_max": 800,
            "remote_work_preference": "フルリモート希望",
            "employment_type": "正社員",
            "industry_preferences": ["IT・通信", "Web・アプリ開発"],
        },
        "seeker2@example.com": {
            "job_title": "UI/UXデザイナー",
            "location_prefecture": "東京都",
            "salary_min": 500,
            "salary_max": 700,
            "remote_work_preference": "週2-3日リモート",
            "employment_type": "正社員",
            "industry_preferences": ["Web・アプリ開発", "デザイン"],
        },
        "seeker3@example.com": {
            "job_title": "バックエンドエンジニア",
            "location_prefecture": "リモート",
            "salary_min": 700,
            "salary_max": 1000,
            "remote_work_preference": "フルリモート希望",
            "employment_type": "正社員",
            "industry_preferences": ["IT・通信", "金融"],
        },
    }

    for seeker in seekers:
        pref_data = preferences_map.get(seeker.email)
        if not pref_data:
            continue

        existing = db.query(UserPreferencesProfile).filter(
            UserPreferencesProfile.user_id == seeker.id
        ).first()

        if not existing:
            pref = UserPreferencesProfile(
                user_id=seeker.id,
                job_title=pref_data["job_title"],
                location_prefecture=pref_data["location_prefecture"],
                salary_min=pref_data["salary_min"],
                salary_max=pref_data["salary_max"],
                remote_work_preference=pref_data["remote_work_preference"],
                employment_type=pref_data["employment_type"],
                industry_preferences=pref_data["industry_preferences"],
            )
            db.add(pref)
            print(f"  + {seeker.email}")
        else:
            print(f"  - {seeker.email} (既存)")

    db.commit()


def main():
    """メイン処理"""
    print("=" * 50)
    print("データベース初期化 & ダミーデータ投入")
    print("=" * 50)

    # テーブル作成
    print("\n1. テーブル作成")
    engine = get_engine()
    print(f"   接続先: {engine.url}")
    Base.metadata.create_all(bind=engine)

    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"   テーブル数: {len(tables)}")

    # ダミーデータ投入
    print("\n2. ダミーデータ投入")
    db = SessionLocal()
    try:
        # 基本テーブル
        employers = seed_users(db)
        seed_jobs(db, employers)

        # マッチング用テーブル
        companies = seed_companies(db)
        seed_company_profiles(db, companies)
        seed_user_preferences(db)

        print("\n" + "=" * 50)
        print("完了しました！")
        print("=" * 50)
        print("\nテストアカウント:")
        print("  求職者: seeker1@example.com / password123")
        print("  企業:   employer1@example.com / password123")
        print("\n作成されたテーブル:")
        print("  - users, jobs, applications, scouts, resumes (基本)")
        print("  - company_date, company_profile (マッチング用企業・求人)")
        print("  - user_preferences_profile (ユーザー希望条件)")
        print("  - conversation_sessions, conversation_logs, chat_sessions (会話)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
