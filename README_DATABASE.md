# データベースセットアップガイド

## 📋 概要

求人マッチングプラットフォームのデータベーススキーマとダミーデータ生成ツールです。

## 🎯 データベース構成

### テーブル一覧（10テーブル）

| No | テーブル名 | 説明 | レコード数（ダミー） |
|----|----------|------|------------------|
| 1 | personal_date | ユーザー基本情報 | 1,000 |
| 2 | user_profile | ユーザー希望条件 | 1,000 |
| 3 | company_date | 企業マスタ | 100 |
| 4 | company_profile | 求人情報 | 1,000 |
| 5 | user_interactions | ユーザー行動履歴 | 10,000 |
| 6 | chat_history | チャット履歴 | 3,000 |
| 7 | dynamic_questions | 動的質問マスタ | 12 |
| 8 | user_question_responses | 質問回答 | 2,000 |
| 9 | job_attributes | 求人属性（多軸評価） | 1,000 |
| 10 | user_preferences | ユーザープロファイル | 500 |

### ビュー一覧（3ビュー）

| No | ビュー名 | 説明 |
|----|---------|------|
| 1 | user_interaction_summary | ユーザー行動サマリー |
| 2 | job_stats | 求人統計 |
| 3 | popular_jobs | 人気求人ランキング |

### インデックス一覧（27個）

パフォーマンス最適化のため、主要カラムにインデックスを設定済み。

### トリガー一覧（7個）

updated_at カラムの自動更新トリガーを各テーブルに設定。

## 🚀 セットアップ手順

### 前提条件

- PostgreSQL 14+ がインストール済み
- Python 3.8+ がインストール済み
- 必要なPythonライブラリ

```bash
pip install psycopg2-binary faker werkzeug numpy
```

### 1. データベースの作成

```bash
# PostgreSQLに接続
psql -U postgres

# データベースを作成
CREATE DATABASE jobmatch;

# ユーザーを作成（必要に応じて）
CREATE USER devuser WITH PASSWORD 'devpass';
GRANT ALL PRIVILEGES ON DATABASE jobmatch TO devuser;

# 接続確認
\c jobmatch
```

### 2. 拡張機能のインストール

```sql
-- UUIDサポート
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- pgvector（ベクトル検索）
CREATE EXTENSION IF NOT EXISTS vector;
```

**pgvectorのインストール方法（未インストールの場合）:**

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-14-pgvector

# macOS (Homebrew)
brew install pgvector

# ソースからビルド
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### 3. スキーマの作成

```bash
# SQLファイルを実行
psql -U devuser -d jobmatch -f complete_schema.sql
```

または、psql内で実行:

```sql
\i complete_schema.sql
```

### 4. ダミーデータの生成

```bash
# Pythonスクリプトを実行
python generate_dummy_data_10k.py
```

実行時間: 約2-5分（データ量に応じて）

## 📊 生成されるデータ

### ユーザーデータ

- **1,000人のユーザー**
  - メールアドレス: `user1@example.com` ～ `user1000@example.com`
  - パスワード: `password123`（全員共通、ハッシュ化済み）
  - 名前: ランダムな日本人名
  - 希望職種: エンジニア、デザイナー、営業など27種類
  - 希望勤務地: 全都道府県からランダム
  - 希望年収: 300万～1,000万円

### 企業・求人データ

- **100社の企業**
  - 企業名: ランダムな会社名（株式会社テックイノベーション等）
  - メールアドレス: `company1@example.com` ～ `company100@example.com`
  - パスワード: `password123`

- **1,000件の求人**
  - 職種: 27種類からランダム
  - 年収: 300万～1,200万円
  - 勤務地: 全都道府県からランダム
  - エンベディング: 1536次元のランダムベクトル（正規化済み）

### 行動データ

- **10,000件のユーザー行動**
  - クリック、お気に入り、応募、閲覧、チャット言及
  - 過去30日間のランダムな日時
  - メタデータ付き（ソース、デバイス情報）

- **3,000件のチャットメッセージ**
  - ユーザーとボットの会話
  - セッションごとに2-3メッセージ
  - 意図抽出データ付き

- **2,000件の質問回答**
  - 12個の基本質問への回答
  - 正規化された回答データ
  - 確信度スコア（0.7-1.0）

### 属性データ

- **1,000件の求人属性**
  - 企業文化（スタートアップ、ベンチャー等）
  - 働き方の柔軟性（リモート、フレックス等）
  - キャリアパス（成長機会、研修等）

- **500件のユーザープロファイル**
  - エンベディングベクトル
  - カテゴリ別の好み（JSONB形式）

## 🔍 データ確認方法

### 基本的な確認

```sql
-- テーブルの件数を確認
SELECT 
    'personal_date' as table_name, COUNT(*) as count FROM personal_date
UNION ALL
SELECT 'user_profile', COUNT(*) FROM user_profile
UNION ALL
SELECT 'company_date', COUNT(*) FROM company_date
UNION ALL
SELECT 'company_profile', COUNT(*) FROM company_profile
UNION ALL
SELECT 'user_interactions', COUNT(*) FROM user_interactions
UNION ALL
SELECT 'chat_history', COUNT(*) FROM chat_history
UNION ALL
SELECT 'dynamic_questions', COUNT(*) FROM dynamic_questions
UNION ALL
SELECT 'user_question_responses', COUNT(*) FROM user_question_responses
UNION ALL
SELECT 'job_attributes', COUNT(*) FROM job_attributes
UNION ALL
SELECT 'user_preferences', COUNT(*) FROM user_preferences;
```

### サンプルデータの表示

```sql
-- ユーザー情報
SELECT * FROM personal_date LIMIT 5;

-- 求人情報（エンベディングは除外）
SELECT id, job_title, location_prefecture, salary_min, salary_max, click_count
FROM company_profile
ORDER BY click_count DESC
LIMIT 10;

-- 人気求人ランキング
SELECT * FROM popular_jobs LIMIT 10;

-- ユーザー行動サマリー
SELECT * FROM user_interaction_summary LIMIT 10;
```

### 統計情報

```sql
-- 職種別求人数
SELECT job_title, COUNT(*) as count
FROM company_profile
GROUP BY job_title
ORDER BY count DESC;

-- 都道府県別求人数
SELECT location_prefecture, COUNT(*) as count
FROM company_profile
GROUP BY location_prefecture
ORDER BY count DESC;

-- インタラクションタイプ別集計
SELECT interaction_type, COUNT(*) as count
FROM user_interactions
GROUP BY interaction_type
ORDER BY count DESC;

-- チャットセッション数
SELECT COUNT(DISTINCT session_id) as session_count
FROM chat_history;
```

## 🧪 テストクエリ

### エンベディング類似度検索

```sql
-- ランダムな求人と類似した求人を検索
WITH sample AS (
    SELECT embedding FROM company_profile WHERE embedding IS NOT NULL LIMIT 1
)
SELECT 
    cp.id,
    cp.job_title,
    cp.location_prefecture,
    cp.salary_min,
    1 - (cp.embedding <=> sample.embedding) AS similarity
FROM company_profile cp, sample
WHERE cp.embedding IS NOT NULL
ORDER BY cp.embedding <=> sample.embedding
LIMIT 10;
```

### JSONB検索

```sql
-- リモートワーク可能な求人を検索
SELECT 
    cp.job_title,
    ja.work_flexibility->>'remote' as remote,
    ja.work_flexibility->>'flex_time' as flex_time
FROM company_profile cp
JOIN job_attributes ja ON cp.id = ja.job_id
WHERE ja.work_flexibility->>'remote' = 'true';

-- スタートアップ企業の求人
SELECT 
    cp.job_title,
    ja.company_culture->>'type' as culture_type,
    ja.company_culture->>'atmosphere' as atmosphere
FROM company_profile cp
JOIN job_attributes ja ON cp.id = ja.job_id
WHERE ja.company_culture->>'type' = 'startup';
```

### 協調フィルタリング用データ

```sql
-- ユーザー×求人のインタラクションマトリックス
SELECT 
    user_id,
    job_id,
    interaction_type,
    CASE interaction_type
        WHEN 'apply' THEN 5.0
        WHEN 'favorite' THEN 3.0
        WHEN 'click' THEN 1.0
        WHEN 'view' THEN 0.5
        ELSE 0.0
    END as score
FROM user_interactions
ORDER BY user_id, job_id;
```

## 🛠️ トラブルシューティング

### pgvector拡張が見つからない

```sql
-- エラー: extension "vector" is not available
```

**解決方法:**
1. pgvectorをインストール（上記の手順参照）
2. PostgreSQLを再起動
3. 拡張を有効化: `CREATE EXTENSION vector;`

### メモリ不足エラー

```
MemoryError: Unable to allocate array
```

**解決方法:**
- ダミーデータ生成数を減らす
- `generate_dummy_data_10k.py` の以下の定数を変更:

```python
NUM_USERS = 500  # 1000 → 500
NUM_JOBS = 500   # 1000 → 500
NUM_INTERACTIONS = 5000  # 10000 → 5000
```

### 接続エラー

```
psycopg2.OperationalError: could not connect to server
```

**解決方法:**
- PostgreSQLが起動しているか確認: `sudo systemctl status postgresql`
- 接続情報を確認: `generate_dummy_data_10k.py` の `DB_CONFIG`

## 📚 参考資料

### データベース設計

- [PostgreSQL公式ドキュメント](https://www.postgresql.org/docs/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [JSONB型の使い方](https://www.postgresql.org/docs/current/datatype-json.html)

### エンベディング

- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- text-embedding-3-small: 1536次元ベクトル

### 推薦システム

- 協調フィルタリング（Collaborative Filtering）
- コンテンツベースフィルタリング（Content-Based Filtering）
- ハイブリッド推薦システム

## 🎉 完了

これでデータベースのセットアップとダミーデータの生成が完了しました！

次のステップ:
1. アプリケーションを起動: `python app.py`
2. ブラウザで確認: `http://localhost:5000`

## 📞 サポート

問題が発生した場合は、以下を確認してください:
- PostgreSQLのバージョン: `psql --version`
- Pythonのバージョン: `python --version`
- 必要なライブラリがインストールされているか: `pip list`