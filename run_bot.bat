@echo off
chcp 65001 >nul
cd /d d:\atom_media_platform
echo =====================================================
echo  Atom Media Platform - Telegram Bot Launcher
echo  အက်တမ်မီဒီယာ - တယ်လီဂရမ်ဘော့တ် စတင်ရန်
echo =====================================================
echo.
echo  EN: Starting bot with credentials from telegram.txt...
echo  MM: telegram.txt မှ အချက်အလက်များဖြင့် ဘော့တ်စတင်နေသည်...
echo.
echo  EN: Make sure PostgreSQL and Redis are running.
echo  MM: PostgreSQL နှင့် Redis အလုပ်လုပ်နေရန်လိုအပ်ပါသည်။
echo.

python backend/run_bot.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  EN: Bot stopped with error code: %ERRORLEVEL%
    echo  MM: ဘော့တ် ရပ်ဆိုင်းသွားပါသည်။ Error code: %ERRORLEVEL%
    echo.
    pause
)