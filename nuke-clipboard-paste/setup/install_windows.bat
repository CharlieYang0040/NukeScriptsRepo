@echo off
setlocal enabledelayedexpansion

REM --- Configuration ---
echo.
echo ========================================
echo  Nuke Clipboard Paste Plugin Installer
echo ========================================
echo.

REM --- Find Nuke Python Executable ---
SET "NUKE_PYTHON_EXE="
SET "LATEST_NUKE_PATH="

REM 1. Attempt to find the latest Nuke version from the correct registry path
echo Searching for Nuke installation in the Foundry registry...
FOR /F "tokens=*" %%G IN ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Foundry" /s /f "Nuke *" /k ^| findstr /I "HKEY_LOCAL_MACHINE"') DO (
    FOR /F "tokens=2*" %%A IN ('reg query "%%G" /v "Path" 2^>nul') DO (
        SET "LATEST_NUKE_PATH=%%B"
    )
)

IF DEFINED LATEST_NUKE_PATH (
    IF EXIST "%LATEST_NUKE_PATH%\python.exe" (
        SET "NUKE_PYTHON_EXE=%LATEST_NUKE_PATH%\python.exe"
    )
)

IF DEFINED NUKE_PYTHON_EXE (
    echo ---
    echo Automatically found Nuke Python at: %NUKE_PYTHON_EXE%
    echo ---
    goto :installation_start
)

echo Automatic search failed. Please provide the path manually.
echo.

:ask_path
echo Please enter the full path to your Nuke installation directory.
echo (You can drag and drop the Nuke shortcut here to see the path)
echo.
echo Example: C:\Program Files\Nuke16.0v6
echo.
set /p NUKE_INSTALL_DIR_INPUT="Nuke Path: "

REM Clean up potential quotes from drag-and-drop
SET NUKE_INSTALL_DIR_INPUT=%NUKE_INSTALL_DIR_INPUT:"=%

IF NOT DEFINED NUKE_INSTALL_DIR_INPUT (
    echo [ERROR] The path cannot be empty. Please try again.
    echo.
    goto :ask_path
)

IF EXIST "%NUKE_INSTALL_DIR_INPUT%\python.exe" (
    SET "NUKE_PYTHON_EXE=%NUKE_INSTALL_DIR_INPUT%\python.exe"
) ELSE (
    echo.
    echo [ERROR] 'python.exe' not found in the directory you provided.
    echo          Please make sure you entered the main Nuke installation folder.
    echo.
    goto :ask_path
)

:installation_start
echo.
echo Using Nuke Python at: %NUKE_PYTHON_EXE%
echo.

REM --- Installation Steps ---

REM 1) Copy plugin files to .nuke folder
echo Copying plugin files to "%USERPROFILE%\.nuke\nuke-clipboard-paste" ...
xcopy /E /I /Y "%~dp0\..\plugin" "%USERPROFILE%\.nuke\nuke-clipboard-paste" > nul
echo Done.
echo.

REM 2) Install dependency packages
echo Installing required packages (Pillow, pywin32) into Nuke's Python environment...
echo Upgrading pip...
"%NUKE_PYTHON_EXE%" -m pip install --upgrade pip
echo Installing packages from requirements.txt...
"%NUKE_PYTHON_EXE%" -m pip install -r "%~dp0\..\requirements.txt" --no-cache-dir

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to install Python packages.
    echo Please check your internet connection and permissions.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Installation successful!
echo ========================================
echo.
echo Please restart Nuke to use the plugin.
echo.
pause
exit /b
