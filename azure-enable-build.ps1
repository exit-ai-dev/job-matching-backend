# Azure App Service - 依存関係ビルドを有効化 (PowerShell)

$APP_NAME = "job-ai-app-affnfdgqbue2euf0"

Write-Host "=== Azure Oryx ビルドを有効化 ===" -ForegroundColor Green
Write-Host "App Name: $APP_NAME"
Write-Host ""

# リソースグループを自動取得
Write-Host "[1/3] リソースグループを取得中..." -ForegroundColor Yellow
$RESOURCE_GROUP = az webapp show --name $APP_NAME --query resourceGroup -o tsv

if (-not $RESOURCE_GROUP) {
    Write-Host "エラー: アプリが見つかりません。az login を実行してログインしてください。" -ForegroundColor Red
    exit 1
}

Write-Host "Resource Group: $RESOURCE_GROUP" -ForegroundColor Cyan
Write-Host ""

# デプロイ時のビルドを有効化
Write-Host "[2/3] デプロイ時のビルドを有効化中..." -ForegroundColor Yellow
az webapp config appsettings set `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true ENABLE_ORYX_BUILD=true

# スタートアップコマンドを設定
Write-Host "[3/3] スタートアップコマンドを設定中..." -ForegroundColor Yellow
az webapp config set `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --startup-file "python -m uvicorn main:app --host 0.0.0.0 --port `$PORT"

Write-Host ""
Write-Host "=== 完了 ===" -ForegroundColor Green
Write-Host ""
Write-Host "次のステップ:" -ForegroundColor Cyan
Write-Host "1. GitHub Actions ワークフローを再実行してください"
Write-Host "2. デプロイ完了後、以下でログを確認:"
Write-Host "   az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. ヘルスチェック:"
Write-Host "   curl https://$APP_NAME.azurewebsites.net/health" -ForegroundColor Yellow
