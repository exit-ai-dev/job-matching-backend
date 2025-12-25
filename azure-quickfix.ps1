# Azure App Service クイックフィックススクリプト (PowerShell)

# 設定（実際の値に置き換えてください）
$APP_NAME = "job-ai-app-affnfdgqbue2euf0"
$RESOURCE_GROUP = "your-resource-group"

Write-Host "=== Azure App Service クイックフィックス ===" -ForegroundColor Green
Write-Host "App Name: $APP_NAME"
Write-Host ""

# 1. スタートアップタイムアウトを延長
Write-Host "[1/6] スタートアップタイムアウトを延長中..." -ForegroundColor Yellow
az webapp config appsettings set `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --settings WEBSITES_CONTAINER_START_TIME_LIMIT=600

# 2. スタートアップコマンド設定
Write-Host "[2/6] スタートアップコマンドを設定中..." -ForegroundColor Yellow
az webapp config set `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --startup-file "python -m uvicorn main:app --host 0.0.0.0 --port `$PORT"

# 3. Python バージョン確認
Write-Host "[3/6] Python バージョンを確認中..." -ForegroundColor Yellow
az webapp config show `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --query linuxFxVersion

# 4. アプリケーション設定確認
Write-Host "[4/6] 環境変数を確認中..." -ForegroundColor Yellow
az webapp config appsettings list `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --query "[].{Name:name, Value:value}" -o table

# 5. ログストリーミング有効化
Write-Host "[5/6] ログストリーミングを有効化中..." -ForegroundColor Yellow
az webapp log config `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --application-logging filesystem `
  --level information

# 6. アプリを再起動
Write-Host "[6/6] アプリケーションを再起動中..." -ForegroundColor Yellow
az webapp restart `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP

Write-Host ""
Write-Host "=== 完了 ===" -ForegroundColor Green
Write-Host "ログを確認するには以下を実行:"
Write-Host "az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP" -ForegroundColor Cyan
Write-Host ""
Write-Host "ヘルスチェック:"
Write-Host "curl https://$APP_NAME.azurewebsites.net/health" -ForegroundColor Cyan
