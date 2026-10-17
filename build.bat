@echo off
setlocal

taskkill /F /IM ProCrushFV01.exe /T 2>nul

echo IMPORTANT: This is a temporary evaluation build.
 echo The API key is only for the pilot evaluation window and should be replaced later by each user.

if not defined GOOGLE_API_KEY (
    echo Enter the temporary evaluation Gemini API key when prompted.
    set /p "GOOGLE_API_KEY=GOOGLE_API_KEY="
)

if not defined GOOGLE_API_KEY (
    echo ERROR: No temporary evaluation API key was provided.
    echo Set the environment variable beforehand or type it in when prompted.
    exit /b 1
)

echo 📦 Building Isolated Standalone Target Executable...
pyinstaller --clean --noconsole --onefile --name "ProCrushFV01" --add-data "src;src" main.py

REM Clear the temporary evaluation key from this shell before exit.
set GOOGLE_API_KEY=

echo ✨ Evaluation Build Finalized Successfully!
endlocal
pause
