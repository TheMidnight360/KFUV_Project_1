@echo off
cd .\Admin
start /B "Admin" Admin.bat
cd ..
cd .\Authorization
start /B "Authorization" Authorization.bat 
cd ..
cd .\Database
start /B "Database" Database.bat
cd ..
cd .\Bot
start /B "Bot" Bot.bat
cd ..
echo All modules have been successfully launched!
set /p pressedKey= Press any key to close the project . . . 
echo Closing all processes . . . 
taskkill /IM python.exe /T /F >nul 2>nul
taskkill /IM admin.exe /T /F >nul 2>nul
taskkill /IM go.exe /T /F >nul 2>nul
timeout /t 1 >nul
exit 0