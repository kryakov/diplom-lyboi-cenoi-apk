@echo off
rem Build Diplom.exe: double-click this file. The result is dist\Diplom.exe (dist is in .gitignore).
cd /d "%~dp0.."
python -m pip install -r requirements.txt pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name Diplom --add-data "%CD%\data;data" --add-data "%CD%\assets;assets" --workpath "%TEMP%\diplom_work" --specpath "%TEMP%\diplom_spec" --distpath "%CD%\dist" "%CD%\main.py"
echo Done: %CD%\dist\Diplom.exe
pause
