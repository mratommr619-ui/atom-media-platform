@echo off
title Atom Media - VPS Deployment

echo ============================================
echo Atom Media Platform - VPS Deployment
echo ============================================
echo.

set VPS_IP=93.127.139.154
set VPS_USER=administrator
set VPS_PATH=/home/administrator/atom_media_platform

echo [1/4] Creating folder on VPS...
ssh %VPS_USER%@%VPS_IP% mkdir -p %VPS_PATH%

echo.
echo [2/4] Uploading files...
scp -r .env docker-compose.yml nginx.conf alembic.ini alembic backend %VPS_USER%@%VPS_IP%:%VPS_PATH%/

echo.
echo [3/4] Starting Docker on VPS...
ssh %VPS_USER%@%VPS_IP% "cd %VPS_PATH% && docker-compose down && docker-compose up -d --build"

echo.
echo [4/4] Waiting for services...
timeout /t 10 /nobreak >nul
echo Checking API...
curl -s http://%VPS_IP%/api/v1/auth/login -X POST -H "Content-Type: application/json" -d "{\"telegram_id\":1715890141}" >nul 2>&1
if %errorlevel% equ 0 (
    echo API is running
) else (
    echo API not ready yet
)

echo.
echo ============================================
pause