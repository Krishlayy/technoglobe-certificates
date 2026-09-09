@echo off
echo ============================================================
echo Starting TechnoGlobe Bharatpur Internship Management System
echo URL: http://127.0.0.1:8000
echo ============================================================
cd /d "%~dp0server"
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
