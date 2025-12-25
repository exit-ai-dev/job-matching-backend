#!/usr/bin/env python3
"""
AIマッチング機能のテストスクリプト
"""
import sys
import os
import io

# Windows環境でのUnicode出力対応
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# プロジェクトのルートをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ml import get_matching_service

# テストデータ
SAMPLE_JOBS = [
    {
        "id": "job-1",
        "title": "Reactフロントエンドエンジニア",
        "description": "React、TypeScript、Next.jsを使ったWebアプリケーション開発。モダンなフロントエンド技術を使って、ユーザー体験の向上に貢献していただきます。",
        "location": "東京都渋谷区",
        "salary_min": 5000000,
        "salary_max": 8000000,
        "employment_type": "full_time",
        "tags": ["React", "TypeScript", "Next.js", "JavaScript", "CSS"],
        "status": "published"
    },
    {
        "id": "job-2",
        "title": "バックエンドエンジニア（Python）",
        "description": "FastAPI、Django等のフレームワークを使用したAPI開発。データベース設計、マイクロサービスアーキテクチャの経験者歓迎。",
        "location": "東京都港区",
        "salary_min": 6000000,
        "salary_max": 9000000,
        "employment_type": "full_time",
        "tags": ["Python", "FastAPI", "Django", "PostgreSQL", "Docker"],
        "status": "published"
    },
    {
        "id": "job-3",
        "title": "フルスタックエンジニア",
        "description": "React + Node.js/Pythonでのフルスタック開発。スタートアップ環境で幅広い技術を学べます。",
        "location": "大阪府大阪市",
        "salary_min": 4500000,
        "salary_max": 7000000,
        "employment_type": "full_time",
        "tags": ["React", "Node.js", "Python", "MongoDB", "AWS"],
        "status": "published"
    },
    {
        "id": "job-4",
        "title": "データサイエンティスト",
        "description": "機械学習モデルの開発・運用。Python、scikit-learn、TensorFlowを使用したデータ分析業務。",
        "location": "東京都千代田区",
        "salary_min": 7000000,
        "salary_max": 12000000,
        "employment_type": "full_time",
        "tags": ["Python", "機械学習", "TensorFlow", "データ分析", "SQL"],
        "status": "published"
    },
    {
        "id": "job-5",
        "title": "Webデザイナー（アルバイト）",
        "description": "Figma、Adobe XDを使用したUI/UXデザイン。週3日〜勤務可能。",
        "location": "東京都新宿区",
        "salary_min": 1500,
        "salary_max": 2000,
        "employment_type": "part_time",
        "tags": ["Figma", "UI/UX", "デザイン"],
        "status": "published"
    }
]

SAMPLE_SEEKER = {
    "name": "田中太郎",
    "skills": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "Git"],
    "experience": "Webフロントエンド開発3年。Reactを使用したSPA開発の経験があります。TypeScriptでの型安全な開発を得意としています。",
    "education": "情報工学科卒業",
    "location": "東京",
    "desired_salary_min": 5000000,
    "preferred_employment_types": ["full_time"]
}


def print_separator():
    print("\n" + "="*80 + "\n")


def test_matching():
    """マッチング機能のテスト"""
    print("🚀 AIマッチング機能のテストを開始します...")
    print_separator()

    # マッチングサービスの初期化
    print("📦 マッチングサービスを初期化中...")
    matching_service = get_matching_service()
    print("✅ 初期化完了")
    print_separator()

    # 求職者プロフィール表示
    print("👤 求職者プロフィール:")
    print(f"  名前: {SAMPLE_SEEKER['name']}")
    print(f"  スキル: {', '.join(SAMPLE_SEEKER['skills'])}")
    print(f"  希望勤務地: {SAMPLE_SEEKER['location']}")
    print(f"  希望年収: {SAMPLE_SEEKER['desired_salary_min']:,}円〜")
    print(f"  希望雇用形態: {', '.join(SAMPLE_SEEKER['preferred_employment_types'])}")
    print_separator()

    # レコメンデーション実行
    print("🤖 AIマッチングを実行中...")
    recommendations = matching_service.recommend_jobs(
        seeker_profile=SAMPLE_SEEKER,
        available_jobs=SAMPLE_JOBS,
        top_k=5
    )
    print(f"✅ {len(recommendations)}件の求人をレコメンドしました")
    print_separator()

    # 結果表示
    print("📊 レコメンデーション結果（スコア順）:\n")

    for i, rec in enumerate(recommendations, 1):
        print(f"【{i}位】 マッチスコア: {rec.match_score:.1f}/100")
        print(f"  求人ID: {rec.job_id}")
        print(f"  職種: {rec.job_data['title']}")
        print(f"  勤務地: {rec.job_data['location']}")
        print(f"  年収: {rec.job_data['salary_min']:,}円 〜 {rec.job_data['salary_max']:,}円")
        print(f"  雇用形態: {rec.job_data['employment_type']}")
        print(f"  必要スキル: {', '.join(rec.job_data['tags'][:5])}")
        print(f"  マッチング理由:")
        for reason in rec.match_reasons:
            print(f"    ・{reason}")
        print()

    print_separator()
    print("✨ テスト完了！")

    # 統計情報
    print("\n📈 統計情報:")
    print(f"  処理した求人数: {len(SAMPLE_JOBS)}件")
    print(f"  フィルタリング後: {len(recommendations)}件")
    avg_score = sum(r.match_score for r in recommendations) / len(recommendations) if recommendations else 0
    print(f"  平均マッチスコア: {avg_score:.1f}/100")


if __name__ == "__main__":
    test_matching()
