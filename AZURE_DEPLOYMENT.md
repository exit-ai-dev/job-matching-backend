# Azure App Service デプロイガイド

## 🔴 現在のエラー原因

### Application Error - 依存関係が見つからない
**エラーログ**:
```
WARNING: Could not find virtual environment directory /home/site/wwwroot/antenv.
WARNING: Could not find package directory /home/site/wwwroot/__oryx_packages__.
ModuleNotFoundError: No module named 'uvicorn'
```

**原因**: Azure Oryxがデプロイ時にPython依存関係をビルドしていない。`SCM_DO_BUILD_DURING_DEPLOYMENT`が無効になっているため、requirements.txtからパッケージがインストールされない。

**影響**: uvicornを含むすべての依存関係がインストールされないため、アプリケーションが起動できない。

---

## ✅ 解決方法（最優先）

### クイックフィックス: Oryxビルドを有効化

以下のスクリプトを実行して、Azure Oryxビルドを有効化します。

#### Windows (PowerShell):
```powershell
cd C:\Users\Exitotrinity-13\job-matching-backend
.\azure-enable-build.ps1
```

#### Linux/Mac:
```bash
cd ~/job-matching-backend
chmod +x azure-enable-build.sh
./azure-enable-build.sh
```

#### 手動で設定する場合:
```bash
az webapp config appsettings set \
  --name job-ai-app-affnfdgqbue2euf0 \
  --resource-group <your-resource-group> \
  --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true ENABLE_ORYX_BUILD=true

az webapp config set \
  --name job-ai-app-affnfdgqbue2euf0 \
  --resource-group <your-resource-group> \
  --startup-file "python -m uvicorn main:app --host 0.0.0.0 --port \$PORT"
```

### 設定後の手順:
1. **GitHub Actions ワークフローを再実行**
   - GitHubリポジトリ → Actions タブ
   - 最新のワークフローを選択 → "Re-run jobs"

2. **デプロイログを確認**
   ```bash
   az webapp log tail --name job-ai-app-affnfdgqbue2euf0 --resource-group <your-resource-group>
   ```
   正常な場合、以下のようなログが表示されます:
   ```
   Oryx Build Command: python -m pip install -r requirements.txt
   Collecting fastapi==0.115.5
   Installing collected packages: ...
   Successfully installed fastapi-0.115.5 uvicorn-0.34.0 ...
   ```

3. **ヘルスチェック**
   ```bash
   curl https://job-ai-app-affnfdgqbue2euf0.azurewebsites.net/health
   # 期待される応答: {"status":"healthy"}
   ```

---

## 📋 その他の考慮事項

### 以前のエラー: 504 Gateway Timeout / 503 Service Unavailable
**原因**: `requirements.txt`に含まれる重いML/AIパッケージ（torch, sentence-transformers等）がAzureのスタートアップタイムアウト（230秒）内にインストール・起動できない

**解決済み**: 現在のrequirements.txtは軽量版に置き換え済み（torch等を除外）

---

## 🔧 詳細な設定手順

### ステップ1: 軽量版requirements.txtを使用

Azureポータルで以下を設定：

**App Service > 構成 > アプリケーション設定**
```
REQUIREMENTS_FILE=requirements.production.txt
```

または、`requirements.txt`を`requirements.production.txt`の内容で上書き

---

### ステップ2: スタートアップコマンド設定

**App Service > 構成 > 全般設定 > スタートアップ コマンド**

#### オプションA: Uvicorn（シンプル）
```bash
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### オプションB: Gunicorn（本番推奨）
```bash
gunicorn -c gunicorn.conf.py main:app
```

---

### ステップ3: 環境変数設定

**App Service > 構成 > アプリケーション設定**

必須の環境変数：
```
DATABASE_URL=postgresql://username:password@hostname/dbname?sslmode=require
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=https://your-frontend-url.azurewebsites.net
DEBUG=False
LOG_LEVEL=INFO
```

---

### ステップ4: データベース設定

#### Azure Database for PostgreSQL使用時

1. **接続文字列を取得**
   ```
   postgres://username:password@hostname.postgres.database.azure.com/dbname?sslmode=require
   ```

2. **DATABASE_URL環境変数に設定**

3. **初回デプロイ後、SSHで接続してテーブル作成**
   ```bash
   cd /home/site/wwwroot
   python init_db.py
   python seed_db.py
   ```

#### SQLite使用時（開発・テスト用）

- DATABASE_URL: `sqlite:///./job_matching.db`
- 注意: Azureの再起動でデータが消える可能性あり

---

### ステップ5: デプロイ

#### VS Code拡張機能使用
1. Azure拡張機能インストール
2. App Serviceを右クリック > Deploy to Web App

#### Azure CLI使用
```bash
cd C:\Users\Exitotrinity-13\job-matching-backend
az webapp up --name your-app-name --resource-group your-rg --runtime PYTHON:3.10
```

#### Git Deploy使用
```bash
git remote add azure https://your-app-name.scm.azurewebsites.net/your-app-name.git
git push azure main
```

---

## 📊 デプロイ後の確認

### 1. ヘルスチェック
```bash
curl https://your-app-name.azurewebsites.net/health
# 期待される応答: {"status":"healthy","version":"1.0.0"}
```

### 2. データベース接続確認
```bash
curl https://your-app-name.azurewebsites.net/health/db
# 期待される応答: {"status":"healthy","database":"reachable"}
```

### 3. API仕様書アクセス
```
https://your-app-name.azurewebsites.net/docs
```

### 4. ログ確認
**Azure Portal > App Service > ログストリーム**

または CLI:
```bash
az webapp log tail --name your-app-name --resource-group your-rg
```

---

## 🔧 トラブルシューティング

### 問題: アプリが起動しない

**確認事項**:
1. ログストリームでエラーメッセージ確認
2. 環境変数が正しく設定されているか
3. requirements.production.txtを使用しているか
4. PORT環境変数が正しく渡されているか

**コマンド**:
```bash
# SSHで接続
az webapp ssh --name your-app-name --resource-group your-rg

# ログ確認
cat /var/log/supervisor/*.log
```

### 問題: データベース接続エラー

**確認事項**:
1. DATABASE_URLが正しいか
2. PostgreSQLのファイアウォールルールでAzure Servicesを許可しているか
3. SSL接続設定（`?sslmode=require`）があるか

### 問題: CORS エラー

**確認事項**:
1. CORS_ORIGINS環境変数にフロントエンドURLが含まれているか
2. プロトコル（https://）が正しいか
3. カンマ区切りで複数設定可能

例:
```
CORS_ORIGINS=https://your-frontend.azurewebsites.net,https://www.your-domain.com
```

---

## 🚀 推奨構成

### Basic B1 プラン以上
- CPU: 1コア以上
- メモリ: 1.75GB以上
- 理由: データベース接続とAPI処理に十分なリソースが必要

### データベース
- **開発**: Azure Database for PostgreSQL - Single Server (Basic)
- **本番**: Azure Database for PostgreSQL - Flexible Server (General Purpose)

### 監視
- Application Insights有効化
- アラート設定（応答時間、エラー率）

---

## 📝 重要な注意点

### 1. ML/AI機能を使用する場合

重いパッケージが必要な場合：
- **Premium V2プラン以上**を使用（メモリ3.5GB以上）
- **スタートアップタイムアウトを延長**（最大1800秒）
  ```bash
  az webapp config appsettings set --name your-app-name --resource-group your-rg --settings WEBSITES_CONTAINER_START_TIME_LIMIT=1800
  ```
- または、**Azure Container Instances**や**Azure Kubernetes Service**を検討

### 2. ファイルストレージ

SQLiteやローカルファイルは再起動で消える可能性があるため：
- **Azure Blob Storage**使用を推奨
- または **Azure Files**をマウント

### 3. SECRET_KEY

本番環境では必ず変更：
```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## 🔄 再デプロイ手順

1. コード修正
2. Git commit
3. Git push azure main（または VS Code拡張機能でデプロイ）
4. ログストリームで起動確認
5. ヘルスチェック実行

---

## 📞 サポート

問題が解決しない場合：
1. Azureサポートチケット作成
2. ログストリームの全内容をコピー
3. 構成設定をスクリーンショット
