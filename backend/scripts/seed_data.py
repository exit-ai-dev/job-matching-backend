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
        employers = seed_users(db)
        seed_jobs(db, employers)
        print("\n" + "=" * 50)
        print("完了しました！")
        print("=" * 50)
        print("\nテストアカウント:")
        print("  求職者: seeker1@example.com / password123")
        print("  企業:   employer1@example.com / password123")
    finally:
        db.close()


if __name__ == "__main__":
    main()
