@echo off
cd /d "C:\Certificate"
start /B "" python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
timeout /t 3 /nobreak >nul
start /B "" "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://127.0.0.1:8000
