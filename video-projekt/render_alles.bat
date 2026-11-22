@echo off
cd /d "%~dp0"
python build.py render
python build.py zusammenfuegen
python build.py web
echo Fertig. Die Videos liegen im Ordner "ausgabe".
pause
