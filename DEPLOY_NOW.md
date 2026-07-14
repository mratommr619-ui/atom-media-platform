# Atom Media Platform - Deploy to VPS

## Prerequisites
- VPS IP: 93.127.139.154
- VPS User: administrator
- VPS Password: 253619Aunthtoonaung$$

## Step 1: Upload Files to VPS

Open PowerShell and run these commands one by one:

```powershell
# Create directory on VPS
ssh administrator@93.127.139.154 "mkdir -p /home/administrator/atom_media_platform"
```

When prompted for password, enter: `253619Aunthtoonaung$$`

```powershell
# Upload all project files
scp -r .env docker-compose.yml nginx.conf alembic.ini alembic backend administrator@93.127.139.154:/home/administrator/atom_media_platform/
```

## Step 2: Start Services on VPS

```powershell
# SSH into VPS and start Docker
ssh administrator@93.127.139.154 "cd /home/administrator/atom_media_platform && docker-compose down && docker-compose up -d --build"
```

## Step 3: Run Database Migrations

```powershell
ssh administrator@93.127.139.154 "cd /home/administrator/atom_media_platform && docker-compose exec backend alembic upgrade head"
```

## Step 4: Promote Admin User

```powershell
# Connect to PostgreSQL and set admin role
ssh administrator@93.127.139.154 "docker-compose exec db psql -U atom_user -d atom_db -c 'UPDATE users SET role = '\''admin'\'' WHERE telegram_id = 1715890141;'"
```

## Step 5: Build Admin App

```powershell
cd atom_admin
flutter build apk --release --dart-define=API_BASE_URL=http://93.127.139.154/api/v1
flutter build windows --release --dart-define=API_BASE_URL=http://93.127.139.154/api/v1
```

The APK will be at: `atom_admin/build/app/outputs/flutter-apk/app-release.apk`

## Step 6: Verify Deployment

```powershell
# Check if backend is running
curl http://93.127.139.154/api/v1/auth/login -X POST -H "Content-Type: application/json" -d "{\"telegram_id\":1715890141}"

# Check Docker logs
ssh administrator@93.127.139.154 "docker-compose -f /home/administrator/atom_media_platform/docker-compose.yml logs -f backend"
```

## Step 7: Configure Telegram Bot

1. Open Telegram and send `/start` to your bot
2. The bot should respond with language selection
3. Admin features will be available after database migration

## Troubleshooting

Check backend logs:
```powershell
ssh administrator@93.127.139.154 "cd /home/administrator/atom_media_platform && docker-compose logs -f"
```

Restart services:
```powershell
ssh administrator@93.127.139.154 "cd /home/administrator/atom_media_platform && docker-compose restart"
```

Check service status:
```powershell
ssh administrator@93.127.139.154 "docker-compose -f /home/administrator/atom_media_platform/docker-compose.yml ps"
```

## Admin App Configuration

The admin app is already configured to connect to `http://93.127.139.154/api/v1`.

To install:
- Android: Transfer `app-release.apk` to your device and install
- Windows: Run `atom_admin/build/windows/x64/runner/Release/atom_admin.exe`

## Important Notes

1. Keep the `.env` file secure - it contains sensitive credentials
2. The bot token and API credentials are already configured
3. Admin user with telegram_id `1715890141` will have admin privileges
4. Firebase mini app URL is set to `https://sdhd-7a835.web.app`

## Next Steps After Deployment

1. Test the Telegram bot by sending `/start`
2. Open admin app and login with Telegram
3. Upload movies/series content through admin panel
4. Test video playback and ad system