@echo off
echo Starting Genie Whisper Development Environment

echo Starting WebSocket Server...
start cmd /k "python websocket_server.py"

echo Starting Frontend...
start cmd /k "npm run dev"

echo Development environment started!
echo - WebSocket Server: ws://localhost:8000
echo - Frontend: http://localhost:3000 (or as configured in your dev server)
echo.
echo Press any key to shut down all processes...
pause > nul

echo Shutting down...
taskkill /f /im node.exe > nul 2>&1
taskkill /f /im python.exe > nul 2>&1
echo Done!
