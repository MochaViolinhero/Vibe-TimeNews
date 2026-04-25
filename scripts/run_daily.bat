@echo off
chcp 65001 > nul
cd /d "%~dp0.."
call .venv\Scripts\python.exe src\run.py >> output\scheduler.log 2>&1
