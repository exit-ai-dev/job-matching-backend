#!/usr/bin/env python3
"""
FastAPI エンドポイントのテストスクリプト
"""
import sys
import io
import requests
import json

# Windows環境でのUnicode出力対応
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8888"

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


def test_health():
    """ヘルスチェック"""
    print("=" * 80)
    print("🔍 ヘルスチェックテスト")
    print("=" * 80)

    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンス: {response.json()}")
        print("✅ ヘルスチェック成功\n")
        return True
    except Exception as e:
        print(f"❌ エラー: {str(e)}\n")
        return False


def test_matching_health():
    """マッチングサービスのヘルスチェック"""
    print("=" * 80)
    print("🔍 マッチングサービスヘルスチェック")
    print("=" * 80)

    try:
        response = requests.get(f"{BASE_URL}/api/matching/health")
        print(f"ステータスコード: {response.status_code}")
        data = response.json()
        print(f"レスポンス: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print("✅ マッチングサービス起動確認\n")
        return True
    except Exception as e:
        print(f"❌ エラー: {str(e)}\n")
        return False


def test_recommend():
    """レコメンデーションAPI"""
    print("=" * 80)
    print("🤖 レコメンデーションAPIテスト")
    print("=" * 80)

    payload = {
        "seeker_profile": SAMPLE_SEEKER,
        "available_jobs": SAMPLE_JOBS,
        "top_k": 10
    }

    try:
        print("📤 リクエスト送信中...")
        response = requests.post(
            f"{BASE_URL}/api/matching/recommend",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"ステータスコード: {response.status_code}\n")

        if response.status_code == 200:
            data = response.json()

            print(f"📊 レコメンデーション結果:")
            print(f"  処理した求人数: {data['total_jobs']}件")
            print(f"  フィルタリング後: {data['filtered_jobs']}件")
            print(f"  レコメンド数: {len(data['recommendations'])}件\n")

            print("=" * 80)
            print("📋 レコメンデーション詳細:\n")

            for i, rec in enumerate(data['recommendations'], 1):
                print(f"【{i}位】 マッチスコア: {rec['match_score']:.1f}/100")
                print(f"  求人ID: {rec['job_id']}")
                print(f"  職種: {rec['job']['title']}")
                print(f"  勤務地: {rec['job']['location']}")
                print(f"  年収: {rec['job']['salary_min']:,}円 〜 {rec['job']['salary_max']:,}円")
                print(f"  マッチング理由:")
                for reason in rec['match_reasons']:
                    print(f"    ・{reason}")
                print()

            print("✅ レコメンデーションAPI成功\n")
            return True
        else:
            print(f"❌ エラー: {response.text}\n")
            return False

    except Exception as e:
        print(f"❌ エラー: {str(e)}\n")
        return False


def main():
    """メイン処理"""
    print("\n")
    print("🚀 FastAPI エンドポイントテスト開始")
    print("=" * 80)
    print(f"APIベースURL: {BASE_URL}")
    print("=" * 80)
    print()

    # テスト実行
    results = []

    results.append(("ヘルスチェック", test_health()))
    results.append(("マッチングヘルスチェック", test_matching_health()))
    results.append(("レコメンデーションAPI", test_recommend()))

    # 結果サマリー
    print("=" * 80)
    print("📈 テスト結果サマリー")
    print("=" * 80)

    for name, result in results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"  {name}: {status}")

    success_count = sum(1 for _, r in results if r)
    total_count = len(results)

    print()
    print(f"成功: {success_count}/{total_count}")
    print("=" * 80)


if __name__ == "__main__":
    main()
