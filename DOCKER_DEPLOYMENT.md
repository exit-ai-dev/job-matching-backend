# Dockerコンテナデプロイガイド

## 🎯 概要

Dockerコンテナ化により、以下の問題を解決します:
- ✅ Azureのビルドタイムアウト問題
- ✅ 依存関係のインストール失敗
- ✅ 環境の一貫性
- ✅ 高速なデプロイと起動

## 🚀 デプロイ手順

### ステップ1: ローカルでDockerイメージをテスト

```powershell
cd C:\Users\Exitotrinity-13\job-matching-backend

# Dockerイメージをビルド
docker build -t job-matching-backend .

# コンテナを起動（単体）
docker run -p 8888:8000 --env-file .env job-matching-backend

# または docker-compose で起動
docker-compose up -d

# ヘルスチェック
curl http://localhost:8888/health

# ログ確認
docker logs -f <container-id>

# 停止
docker-compose down
```

### ステップ2: GitHubリポジトリの準備

#### オプションA: リポジトリをパブリックにする（簡単）

1. GitHub → リポジトリ → Settings → General
2. Danger Zone → Change visibility → Make public

#### オプションB: プライベートのまま（推奨、GitHub PATが必要）

1. **GitHub Personal Access Token (PAT) を作成**
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - "Generate new token (classic)" をクリック
   - Note: `Azure Container Pull`
   - 権限: `read:packages` をチェック
   - "Generate token" をクリック
   - **トークンをコピーして保存**（後で使用）

2. **GitHub Secretsを確認**
   - リポジトリ → Settings → Secrets and variables → Actions
   - 以下が設定されていることを確認:
     - `AZURE_WEBAPP_NAME`: `job-ai-app-affnfdgqbue2euf0`
     - `AZURE_WEBAPP_PUBLISH_PROFILE`: Azure Portalからダウンロードした発行プロファイル

### ステップ3: Azure App Serviceをコンテナモードに設定

```powershell
cd C:\Users\Exitotrinity-13\job-matching-backend

# Azure CLIでログイン
az login

# コンテナ設定スクリプトを実行
.\azure-setup-container.ps1
```

スクリプトが表示する指示に従って、必要に応じて認証情報を設定します。

#### プライベートリポジトリの場合、追加で実行:

```powershell
# GitHubユーザー名とPATを使用
az webapp config container set `
  --name job-ai-app-affnfdgqbue2euf0 `
  --resource-group <your-resource-group> `
  --docker-custom-image-name ghcr.io/<your-github-username>/job-matching-backend:latest `
  --docker-registry-server-url https://ghcr.io `
  --docker-registry-server-user <your-github-username> `
  --docker-registry-server-password <your-github-pat>
```

### ステップ4: GitHub Actionsでデプロイ

1. **リポジトリにコミット&プッシュ**
   ```bash
   git add .
   git commit -m "Add Docker support for Azure deployment"
   git push origin main
   ```

2. **GitHub Actionsを確認**
   - GitHubリポジトリ → Actions タブ
   - "Deploy Docker Container to Azure" ワークフローが自動実行される
   - ワークフローの進行状況を確認:
     - ✅ Build and push Docker image
     - ✅ Deploy to Azure Web App
     - ✅ Health check

3. **デプロイ完了まで待つ**（約5-10分）
   - Dockerイメージのビルド: 3-5分
   - Azureへのプッシュ: 1-2分
   - デプロイと起動: 1-2分

### ステップ5: デプロイ確認

```powershell
# ヘルスチェック
curl https://job-ai-app-affnfdgqbue2euf0.azurewebsites.net/health

# 期待される応答
{"status":"healthy"}

# API仕様書を確認
Start-Process "https://job-ai-app-affnfdgqbue2euf0.azurewebsites.net/docs"

# ログストリームを確認
az webapp log tail --name job-ai-app-affnfdgqbue2euf0 --resource-group <your-rg>
```

## 🔍 ログの確認

### Dockerコンテナログ（Azure Portal）

1. Azure Portal → App Service → `job-ai-app-affnfdgqbue2euf0`
2. 左メニュー → **ログ ストリーム**

正常な起動ログ:
```
Starting application...
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### GitHub Actionsログ

GitHub → Actions → 最新のワークフロー → ログを確認

## 🛠️ トラブルシューティング

### 問題1: "Image pull failed"

**原因**: Azure App ServiceがGitHub Container Registryからイメージをプルできない

**解決策**:
1. リポジトリがパブリックか確認
2. プライベートの場合、GitHub PATが正しく設定されているか確認
3. イメージ名が正しいか確認: `ghcr.io/<username>/<repo>:latest`

### 問題2: "Container didn't respond to HTTP ping"

**原因**: アプリケーションがポート8000でリッスンしていない

**解決策**:
1. Azureアプリ設定で `WEBSITES_PORT=8000` が設定されているか確認
2. Dockerfileの `EXPOSE 8000` を確認
3. main.pyで `--port 8000` を確認

### 問題3: GitHub Actions で "denied: permission_denied"

**原因**: GitHub Actionsがパッケージをプッシュする権限がない

**解決策**:
1. リポジトリ → Settings → Actions → General
2. Workflow permissions で "Read and write permissions" を選択
3. Save

### 問題4: データベース接続エラー

**原因**: DATABASE_URL環境変数が設定されていない

**解決策**:
```powershell
az webapp config appsettings set `
  --name job-ai-app-affnfdgqbue2euf0 `
  --resource-group <your-rg> `
  --settings DATABASE_URL="sqlite:///./job_matching.db"
```

本番環境ではPostgreSQLを使用:
```
DATABASE_URL="postgresql://user:pass@host.postgres.database.azure.com/dbname?sslmode=require"
```

## 📋 環境変数チェックリスト

Azure Portal → App Service → 構成 → アプリケーション設定

必須:
- ✅ `WEBSITES_PORT=8000`
- ✅ `DOCKER_ENABLE_CI=true`
- ✅ `SECRET_KEY=<ランダムな文字列>`
- ✅ `CORS_ORIGINS=<フロントエンドURL>`

オプション:
- ⬜ `DATABASE_URL=<PostgreSQL接続文字列>`
- ⬜ `OPENAI_API_KEY=<OpenAI APIキー>`
- ⬜ `DEBUG=False`
- ⬜ `LOG_LEVEL=INFO`

## 🔄 再デプロイ手順

コードを修正した後:

```bash
git add .
git commit -m "Update backend code"
git push origin main
```

GitHub Actionsが自動的に:
1. 新しいDockerイメージをビルド
2. ghcr.ioにプッシュ
3. Azure App Serviceにデプロイ
4. コンテナを自動再起動

## 🎉 成功の確認

すべて正常に動作している場合:

1. ✅ GitHub Actions ワークフローが緑色のチェックマーク
2. ✅ `curl https://job-ai-app-affnfdgqbue2euf0.azurewebsites.net/health` が `{"status":"healthy"}` を返す
3. ✅ `/docs` でAPI仕様書が表示される
4. ✅ ログストリームでエラーがない
5. ✅ フロントエンドからAPIにアクセスできる

## 📊 パフォーマンス

Dockerコンテナ化の効果:

| 項目 | Oryxビルド | Dockerコンテナ |
|------|-----------|---------------|
| ビルド時間 | 5-15分 | 3-5分（GitHub Actions内） |
| デプロイ時間 | タイムアウト | 1-2分 |
| 起動時間 | - | 30秒-1分 |
| 安定性 | 低 | 高 |
| 再現性 | 低 | 高 |

## 🔐 セキュリティ

1. **Secrets管理**
   - GitHub Secretsを使用
   - .envファイルをコミットしない
   - Azure Key Vaultと連携（オプション）

2. **イメージセキュリティ**
   - 公式Pythonイメージ使用
   - 非rootユーザーで実行
   - 最小限のパッケージのみインストール

3. **ネットワークセキュリティ**
   - HTTPS強制
   - CORS設定
   - レート制限（実装推奨）

## 📚 関連ファイル

- `Dockerfile` - Dockerイメージ定義
- `.dockerignore` - イメージに含めないファイル
- `docker-compose.yml` - ローカル開発環境
- `.github/workflows/azure-container.yml` - CI/CDパイプライン
- `azure-setup-container.ps1` - Azure設定スクリプト

## 🆘 サポート

問題が解決しない場合:

1. GitHub Actionsのログを確認
2. Azureログストリームを確認
3. ローカルでDockerイメージをテスト
4. イシューを作成（ログを含める）
