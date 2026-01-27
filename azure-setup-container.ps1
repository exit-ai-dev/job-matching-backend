# Azure App Service - Dockerコンテナ設定 (PowerShell)

$APP_NAME = "job-ai-app-affnfdgqbue2euf0"

Write-Host "=== Azure App Service - Dockerコンテナ設定 ===" -ForegroundColor Green
Write-Host "App Name: $APP_NAME"
Write-Host ""

# リソースグループを自動取得
Write-Host "[1/5] リソースグループを取得中..." -ForegroundColor Yellow
$RESOURCE_GROUP = az webapp show --name $APP_NAME --query resourceGroup -o tsv

if (-not $RESOURCE_GROUP) {
    Write-Host "エラー: アプリが見つかりません。az login を実行してログインしてください。" -ForegroundColor Red
    exit 1
}

Write-Host "Resource Group: $RESOURCE_GROUP" -ForegroundColor Cyan
Write-Host ""

# Dockerコンテナモードに切り替え
Write-Host "[2/5] Dockerコンテナモードに設定中..." -ForegroundColor Yellow
Write-Host "注意: リポジトリをパブリックにするか、GitHub Personal Access Tokenを設定してください" -ForegroundColor Cyan

# GitHubリポジトリ情報を取得
$GITHUB_REPO = git config --get remote.origin.url
$GITHUB_USER = $GITHUB_REPO -replace '.*github.com[:/]([^/]+)/.*', '$1'
$REPO_NAME = $GITHUB_REPO -replace '.*/', '' -replace '\.git$', ''

Write-Host "GitHub User: $GITHUB_USER" -ForegroundColor Cyan
Write-Host "Repository: $REPO_NAME" -ForegroundColor Cyan
Write-Host ""

$IMAGE_NAME = "ghcr.io/$GITHUB_USER/$REPO_NAME:latest"
Write-Host "Docker Image: $IMAGE_NAME" -ForegroundColor Cyan
Write-Host ""

# コンテナ設定
Write-Host "[3/5] コンテナイメージを設定中..." -ForegroundColor Yellow
az webapp config container set `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --docker-custom-image-name $IMAGE_NAME `
  --docker-registry-server-url https://ghcr.io

# 環境変数設定（必要に応じて追加）
Write-Host "[4/5] 環境変数を設定中..." -ForegroundColor Yellow
az webapp config appsettings set `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --settings `
    WEBSITES_PORT=8000 `
    DOCKER_ENABLE_CI=true `
    SECRET_KEY="your-secret-key-change-in-production" `
    CORS_ORIGINS="https://<your-frontend>.azurewebsites.net" `
    DEBUG=False `
    LOG_LEVEL=INFO

# アプリを再起動
Write-Host "[5/5] アプリケーションを再起動中..." -ForegroundColor Yellow
az webapp restart `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP

Write-Host ""
Write-Host "=== 設定完了 ===" -ForegroundColor Green
Write-Host ""
Write-Host "次のステップ:" -ForegroundColor Cyan
Write-Host "1. GitHubリポジトリをパブリックにするか、プライベートの場合は以下を実行:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   a. GitHub Personal Access Token (PAT) を作成:" -ForegroundColor White
Write-Host "      - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)" -ForegroundColor White
Write-Host "      - 'Generate new token' → 'read:packages' 権限を選択" -ForegroundColor White
Write-Host ""
Write-Host "   b. Azure Web Appに認証情報を設定:" -ForegroundColor White
Write-Host "      az webapp config container set \" -ForegroundColor Gray
Write-Host "        --name $APP_NAME \" -ForegroundColor Gray
Write-Host "        --resource-group $RESOURCE_GROUP \" -ForegroundColor Gray
Write-Host "        --docker-custom-image-name $IMAGE_NAME \" -ForegroundColor Gray
Write-Host "        --docker-registry-server-url https://ghcr.io \" -ForegroundColor Gray
Write-Host "        --docker-registry-server-user <GitHub-Username> \" -ForegroundColor Gray
Write-Host "        --docker-registry-server-password <GitHub-PAT>" -ForegroundColor Gray
Write-Host ""
Write-Host "2. GitHub Actions ワークフローを実行:" -ForegroundColor Yellow
Write-Host "   - GitHubリポジトリ → Actions → 'Deploy Docker Container to Azure' → Run workflow" -ForegroundColor White
Write-Host ""
Write-Host "3. デプロイ後、ログを確認:" -ForegroundColor Yellow
Write-Host "   az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP" -ForegroundColor Gray
Write-Host ""
Write-Host "4. ヘルスチェック:" -ForegroundColor Yellow
Write-Host "   curl https://$APP_NAME.azurewebsites.net/health" -ForegroundColor Gray
