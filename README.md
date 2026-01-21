# JobMatch AI システム - DB情報とダミーデータ生成

このディレクトリには、JobMatch AIシステムのデータベーススキーマ情報とダミーデータ生成ツールが含まれています。

## 📁 ファイル構成

- `db_schema_summary.md` - データベーススキーマの完全なドキュメント
- `generate_dummy_data.py` - ダミーデータ生成スクリプト
- `requirements_dummy_data.txt` - Pythonパッケージの依存関係

## 📊 データベーススキーマ概要

### テーブル数
合計 **30テーブル** + 1ビュー

### 主要カテゴリ
1. **ユーザー関連** (5テーブル)
   - personal_date, user_profile, user_preferences_profile, user_personality_analysis, user_sessions

2. **企業・求人関連** (4テーブル)
   - company_date, company_profile, job_attributes, job_additional_answers

3. **会話・マッチング関連** (7テーブル)
   - conversation_logs, conversation_sessions, conversation_turns, user_insights, score_history, chat_history, chat_sessions

4. **ユーザー行動追跡** (3テーブル)
   - user_interactions, user_interaction_summary (ビュー), search_history

5. **エンリッチメント・トレンド** (5テーブル)
   - missing_job_info_log, company_enrichment_requests, global_preference_trends, trend_thresholds, current_weekly_trends

6. **基本項目管理** (1テーブル)
   - baseline_job_fields

7. **スカウト関連** (1テーブル)
   - scout_messages

8. **動的質問関連** (2テーブル)
   - dynamic_questions, user_question_responses

## 🚀 ダミーデータ生成の使い方

### 1. 前提条件

- PostgreSQL 12以上がインストールされていること
- pgvector拡張機能がインストールされていること（求人のベクトル埋め込み用）
- Python 3.8以上

### 2. 環境セットアップ

```bash
# 必要なPythonパッケージをインストール
pip install -r requirements_dummy_data.txt
```

### 3. データベースの準備

```bash
# PostgreSQLに接続してデータベースを作成
createdb jobmatch

# スキーマを適用（元のプロジェクトのSQLファイルを使用）
psql -d jobmatch -f db_schema_complete.sql
psql -d jobmatch -f create_chat_sessions.sql

# pgvector拡張を有効化
psql -d jobmatch -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 4. ダミーデータの生成

```bash
# 基本的な使い方
python generate_dummy_data.py --password your_password

# カスタムオプション
python generate_dummy_data.py \
  --host localhost \
  --database jobmatch \
  --user postgres \
  --password your_password \
  --port 5432
```

### 5. 生成されるデータ量

| カテゴリ | データ件数 |
|---------|-----------|
| ユーザー | 50人 |
| 企業 | 20社 |
| 求人 | 100件 |
| 会話セッション | 30セッション |
| ユーザーインタラクション | 500件 |
| スカウトメッセージ | 80件 |
| その他 | 各テーブルに応じた適切な量 |

## 📖 スキーマドキュメントの見方

`db_schema_summary.md`ファイルには以下の情報が含まれています：

1. **テーブル定義**: 各テーブルのカラム名、データ型、制約、説明
2. **インデックス一覧**: パフォーマンス最適化用のインデックス
3. **テーブル関係図**: 主要な外部キー関係
4. **初期データ**: システムに必要な初期設定値

## 🔧 カスタマイズ

### データ量の調整

`generate_dummy_data.py`の以下のパラメータを変更することで、生成されるデータ量を調整できます：

```python
# generate_all_data()メソッド内
user_ids = self.generate_users(50)  # ← ユーザー数を変更
company_ids = self.generate_companies(20)  # ← 企業数を変更
job_ids = self.generate_jobs(company_ids, 100)  # ← 求人数を変更
```

### データ内容のカスタマイズ

各テーブルの生成ロジックは個別のメソッドに分かれているため、必要に応じて修正できます：

- `generate_users()` - ユーザーデータ
- `generate_jobs()` - 求人データ
- `generate_conversation_sessions()` - 会話セッションデータ
- など

## ⚠️ 注意事項

1. **既存データの削除**: スクリプトは既存データを削除せず、追加のみ行います。データをリセットする場合は手動でテーブルをTRUNCATEしてください。

2. **パスワードハッシュ**: 生成されるパスワードは平文です。本番環境では適切にハッシュ化してください。

3. **ベクトル埋め込み**: `company_profile.embedding`カラムはNULLのままです。実際の埋め込みは別途生成する必要があります。

4. **外部キー整合性**: スクリプトは外部キー制約を考慮していますが、大量データ生成時にはパフォーマンスに注意してください。

## 🐛 トラブルシューティング

### pgvector拡張が見つからない

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-XX-pgvector

# macOS
brew install pgvector
```

### 接続エラー

```bash
# PostgreSQLが起動しているか確認
sudo systemctl status postgresql

# 接続設定を確認
psql -h localhost -U postgres -d jobmatch
```

### メモリ不足エラー

大量のデータを生成する場合、バッチサイズを調整してください：

```python
# execute_values()のpage_sizeパラメータを調整
execute_values(self.cur, query, data, page_size=100)
```

## 📚 参考情報

- PostgreSQL公式ドキュメント: https://www.postgresql.org/docs/
- pgvector: https://github.com/pgvector/pgvector
- Faker: https://faker.readthedocs.io/

## 🤝 サポート

問題が発生した場合は、以下を確認してください：

1. PostgreSQLのバージョン
2. pgvector拡張のインストール状況
3. データベースの接続情報
4. エラーメッセージの完全な内容

---

**作成日**: 2026年1月20日
**対象システム**: JobMatch AI (FastAPI版)
