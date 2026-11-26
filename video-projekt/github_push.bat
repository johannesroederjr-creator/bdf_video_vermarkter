@echo off
setlocal
set REPO=%~dp0..\bdf_video_vermarkter
cd /d "%REPO%"
if "%~1"=="" (
  echo Verwendung: github_push.bat "Commit-Nachricht"
  echo.
  git status
  exit /b 1
)
git add video-projekt
git commit -m "%~1"
git push -u origin main
endlocal