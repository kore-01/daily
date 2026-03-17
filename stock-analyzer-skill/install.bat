@echo off
chcp 65001 >nul
echo ========================================
echo   Stock Analyzer Skill Installer
echo ========================================
echo.

set SKILLS_DIR=%USERPROFILE%\.claude\skills

echo [1/3] Creating skills directory...
if not exist "%SKILLS_DIR%" mkdir "%SKILLS_DIR%"

echo [2/3] Installing skill file...
copy /Y "%~dp0stock-analyzer.md" "%SKILLSDIR%\" >nul

if exist "%SKILLS_DIR%\stock-analyzer.md" (
    echo [3/3] Installation successful!
    echo.
    echo Skill installed to:
    echo   %SKILLS_DIR%\stock-analyzer.md
    echo.
    echo Usage:
    echo   1. Restart Claude Code or reload skills
    echo   2. Type a stock code like '300766' or 'analyze 000301'
    echo   3. Claude will automatically call the API and return raw data
    echo.
    echo API Server: http://193.112.101.212:8000
    echo Web UI:     http://193.112.101.212:8000
    echo.
) else (
    echo [ERROR] Installation failed!
    pause
    exit /b 1
)

pause
