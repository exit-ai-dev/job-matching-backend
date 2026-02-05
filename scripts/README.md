# サブスクリプションテーブル セットアップスクリプト

サブスクリプション課金機能に必要なテーブル作成とシードデータ投入用スクリプトです。

## 新規作成テーブル

| テーブル名 | 説明 |
|-----------|------|
| `subscription_plans` | サブスクリプションプラン定義 |
| `subscriptions` | ユーザーのサブスクリプション状態 |
| `usage_tracking` | 月間使用量追跡 |
| `payment_history` | 決済履歴 |

## usersテーブルへの追加カラム

| カラム名 | 型 | 説明 |
|---------|-----|------|
| `gmo_member_id` | VARCHAR(100) | GMOペイメント会員ID |
| `subscription_tier` | VARCHAR(50) | 現在のプラン階層（デフォルト: 'free'） |

## シードデータ（プラン）

### 求職者向け
| プラン | 月額 | AIチャット | 応募 |
|-------|------|-----------|------|
| フリー | ¥0 | 0回/月 | 5件/月 |
| スタンダード | ¥980 | 20回/月 | 30件/月 |
| プレミアム | ¥2,980 | 無制限 | 無制限 |

### 企業向け
| プラン | 月額 | スカウト | 求人掲載 | 候補者閲覧 |
|-------|------|---------|---------|-----------|
| フリー | ¥0 | 3件/月 | 1件 | 5件/月 |
| スターター | ¥9,800 | 15件/月 | 3件 | 30件/月 |
| ビジネス | ¥29,800 | 50件/月 | 10件 | 100件/月 |

---

## 使用方法

### 方法1: Pythonスクリプト

```bash
# 依存パッケージインストール
pip install psycopg2-binary

# 環境変数を使用
export DATABASE_URL="postgresql://user:password@your-server.postgres.database.azure.com:5432/job_matching?sslmode=require"
python scripts/setup_subscription_tables.py

# または直接接続情報を指定
python scripts/setup_subscription_tables.py \
    --host your-server.postgres.database.azure.com \
    --database job_matching \
    --user admin@your-server \
    --password yourpassword
```

#### オプション
- `--skip-seed`: シードデータ投入をスキップ
- `--dry-run`: 実行せずにSQLを表示のみ

### 方法2: Azure CLI + psql

```bash
# Azure CLIでログイン
az login

# PostgreSQLサーバーのファイアウォールルールを追加（必要に応じて）
az postgres flexible-server firewall-rule create \
    --resource-group your-resource-group \
    --name your-server \
    --rule-name AllowMyIP \
    --start-ip-address your-ip \
    --end-ip-address your-ip

# SQLファイルを実行
PGPASSWORD=yourpassword psql \
    -h your-server.postgres.database.azure.com \
    -U admin@your-server \
    -d job_matching \
    -f scripts/subscription_tables.sql
```

### 方法3: Azure Portal (Query Editor)

1. Azure Portal > PostgreSQL サーバー > 接続のセキュリティ
2. ファイアウォールルールで自分のIPを許可
3. データベース > クエリエディター
4. `subscription_tables.sql` の内容をコピー＆実行

---

## 検証

テーブルが正しく作成されたか確認：

```sql
-- テーブル一覧
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('subscription_plans', 'subscriptions', 'usage_tracking', 'payment_history');

-- プラン確認
SELECT name, display_name, user_role, price_jpy FROM subscription_plans ORDER BY user_role, display_order;

-- usersテーブルのカラム確認
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'users' AND column_name IN ('gmo_member_id', 'subscription_tier');
```
