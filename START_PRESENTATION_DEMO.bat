@echo off
cd /d "%~dp0"
echo Starting server and three connected GUI clients...
start "Monitoring Server" cmd /k "cd /d %~dp0 && python -B server.py"
timeout /t 2 /nobreak > nul
start "Client1 GUI" cmd /k "cd /d %~dp0 && python -B launch_named_gui.py Client1"
timeout /t 1 /nobreak > nul
start "Client2 GUI" cmd /k "cd /d %~dp0 && python -B launch_named_gui.py Client2"
timeout /t 1 /nobreak > nul
start "Client3 GUI" cmd /k "cd /d %~dp0 && python -B launch_named_gui.py Client3"
echo Done. Do not close the server terminal during presentation.
pause
