# Atom Media Platform Deployment

## Build Outputs

- Admin Android APK: `atom_admin/build/app/outputs/flutter-apk/app-release.apk`
- Admin Windows EXE: `atom_admin/build/windows/x64/runner/Release/atom_admin.exe`
- Telegram Mini App web bundle: `mini_app/build/web`

## Backend VPS

The VPS target from `vps.txt` is `93.127.139.154`. Create a production `.env` on the VPS with these keys:

```env
SECRET_KEY=<generate-a-long-random-secret>
DATABASE_URL=postgresql+asyncpg://atom_user:atom_pass@db:5432/atom_db
REDIS_URL=redis://redis:6379/0
BOT_TOKEN=<telegram-bot-token>
TELEGRAM_API_ID=<telegram-api-id>
TELEGRAM_API_HASH=<telegram-api-hash>
MINI_APP_URL=https://sdhd-7a835.web.app
ADMIN_CHAT_ID=<telegram-admin-chat-id>
ADMIN_TELEGRAM_IDS=[<telegram-admin-chat-id>]
BACKEND_CORS_ORIGINS=["https://sdhd-7a835.web.app","https://93-127-139-154.nip.io","http://93.127.139.154"]
AD_DURATION_SECONDS=15
```

Then deploy:

```powershell
scp -r backend alembic alembic.ini docker-compose.yml nginx.conf administrator@93.127.139.154:/opt/atom_media_platform
ssh administrator@93.127.139.154
cd /opt/atom_media_platform
docker compose up -d --build
docker compose exec backend alembic upgrade head
```

For production HTTPS on the backend API, point a domain to the VPS and replace `your-domain.com` in `nginx.conf`, then issue a Let's Encrypt certificate.

## Firebase Mini App

Build the mini app with the VPS API URL:

```powershell
cd mini_app
flutter build web --release --dart-define=API_BASE_URL=https://93-127-139-154.nip.io/api/v1
firebase login
firebase use atom-media-platform
firebase deploy --only hosting
```

After Firebase returns the hosting URL, set backend `MINI_APP_URL` to that HTTPS URL and restart the backend:

```powershell
docker compose up -d --build backend
```

## Telegram Bot

1. Start the backend container so aiogram polling starts.
2. Send `/start` to the bot.
3. Promote the admin Telegram user in PostgreSQL:

```sql
update users set role = 'admin' where telegram_id = <admin-telegram-id>;
```

4. Login to the admin app with that Telegram ID.

## Admin App Builds

```powershell
cd atom_admin
flutter build apk --release --dart-define=API_BASE_URL=https://93-127-139-154.nip.io/api/v1
flutter build windows --release --dart-define=API_BASE_URL=https://93-127-139-154.nip.io/api/v1
```
