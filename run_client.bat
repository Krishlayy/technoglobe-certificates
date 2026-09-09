@echo off
echo ============================================================
echo Starting Vite Dev Server (Port 3000 with Proxy to 8000)
echo URL: http://127.0.0.1:3000
echo ============================================================
cd /d "%~dp0client"
npm run dev
pause
