@echo off
title TechnoGlobe - Public Cloud Tunnel
echo =========================================================
echo TechnoGlobe Public Cloud Tunnel (Cloudflare Edge Network)
echo =========================================================
echo.
echo Forwarding port 8000 to Cloudflare secure public HTTPS...
echo.
"C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://127.0.0.1:8000
pause
