$cmd = 'cmd /c "cd /d E:\Vibe-TimeNews && .venv\Scripts\python.exe src\run.py >> output\scheduler.log 2>&1"'
schtasks /create /tn "Vibe-TimeNews-每日推送" /tr $cmd /sc daily /st 08:00 /ru MOCHA-PC\ROG /f
echo "Done"
