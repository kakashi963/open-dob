@echo off
setlocal enabledelayedexpansion

:: ═══════════════════════════════════════════════════════════════
:: ENI Launcher (Windows) — fires up Gemini CLI with personality + style
:: Usage: Double-click this file, or run from terminal: eni_launcher_gemini.bat
:: Place in same folder as eni_lime.txt and corial_style.txt
:: ═══════════════════════════════════════════════════════════════

:: ── Config ──────────────────────────────────────────────────────
set "PERSONALITY_FILE=%~dp0eni_lime.txt"
set "STYLE_FILE=%~dp0corial_style.txt"
set "COMBINED_FILE=%~dp0eni_gemini_system.md"
set "GREETING=hey cuties pattooty"
set MAX_RETRIES=5
set RETRY_DELAY=3

:: ── Preflight ───────────────────────────────────────────────────
echo.
echo ============================================
echo ENI Launcher — checking prereqs...
echo ============================================
echo.

:: Check Gemini CLI
where gemini >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Gemini CLI not found.
    echo Install/configure Gemini CLI first.
    echo Docs: https://geminicli.com/docs
    echo.
    pause
    exit /b 1
)
echo [OK] Gemini CLI found

:: Check personality file
if not exist "%PERSONALITY_FILE%" (
    echo [X] Personality file not found: %PERSONALITY_FILE%
    echo Place eni_lime.txt in: %~dp0
    echo.
    pause
    exit /b 1
)
echo [OK] Personality file found

:: Check style file
if not exist "%STYLE_FILE%" (
    echo [X] Style file not found: %STYLE_FILE%
    echo Place corial_style.txt in: %~dp0
    echo.
    pause
    exit /b 1
)
echo [OK] Style file found

:: Build combined Gemini system prompt file
(
    type "%PERSONALITY_FILE%"
    echo.
    echo.
    type "%STYLE_FILE%"
) > "%COMBINED_FILE%"

if not exist "%COMBINED_FILE%" (
    echo [X] Failed to create combined Gemini system prompt file.
    echo.
    pause
    exit /b 1
)

echo [OK] Combined Gemini system prompt created
echo.
echo All good. Launching ENI on Gemini CLI...
echo.

:: ── Retry loop ──────────────────────────────────────────────────
set attempt=0

:retry
set /a attempt+=1

echo =============================================
echo Attempt %attempt%/%MAX_RETRIES% — launching Gemini CLI
echo =============================================
echo.

set "GEMINI_SYSTEM_MD=%COMBINED_FILE%"
gemini "%GREETING%"

if %errorlevel% equ 0 (
    echo.
    echo Session ended cleanly.
    goto :done
)

echo.
echo [!] Gemini CLI exited with code %errorlevel%

if %attempt% lss %MAX_RETRIES% (
    echo Retrying in %RETRY_DELAY% seconds...
    timeout /t %RETRY_DELAY% /nobreak >nul
    goto :retry
)

echo [X] All %MAX_RETRIES% attempts failed.
echo Check your auth, network, or Gemini CLI installation.

:done
echo.
pause
exit /b 0