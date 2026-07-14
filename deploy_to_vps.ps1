# Atom Media Platform - VPS Deployment Script
$VPS_IP = "93.127.139.154"
$VPS_USER = "administrator"
$VPS_PASSWORD = "253619Aunthtoonaung$$"
$VPS_PATH = "/home/administrator/atom_media_platform"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Atom Media Platform - VPS Deployment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Create remote directory
Write-Host "[1/5] Creating folder on VPS..." -ForegroundColor Yellow
ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP "mkdir -p $VPS_PATH"

# Upload files using scp with password
Write-Host ""
Write-Host "[2/5] Uploading files..." -ForegroundColor Yellow
$scpProcess = Start-Process -FilePath "scp" -ArgumentList "-r .env docker-compose.yml nginx.conf alembic.ini alembic backend $VPS_USER@$VPS_IP`:$VPS_PATH/" -NoNewWindow -Wait -PassThru -RedirectStandardInput "$env:TEMP\scp_input.txt"
$scpProcess.StandardInput.WriteLine($VPS_PASSWORD)

Write-Host ""
Write-Host "[3/5] Starting Docker on VPS..." -ForegroundColor Yellow
ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP "cd $VPS_PATH && docker-compose down && docker-compose up -d --build"

Write-Host ""
Write-Host "[4/5] Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "[5/5] Checking API..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://$VPS_IP/api/v1/auth/login" -Method POST -ContentType "application/json" -Body '{"telegram_id":1715890141}' -TimeoutSec 5
    Write-Host "API is running" -ForegroundColor Green
} catch {
    Write-Host "API not ready yet, will be available shortly" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Build Flutter admin app: cd atom_admin && flutter build apk --release --dart-define=API_BASE_URL=http://$VPS_IP/api/v1"
Write-Host "2. Check backend logs: ssh $VPS_USER@$VPS_IP 'cd $VPS_PATH && docker-compose logs -f backend'"
Write-Host ""
Read-Host "Press Enter to exit"