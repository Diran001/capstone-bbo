@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem =========================================================
rem cap_scr_v010_archive_zips.cmd
rem
rem Maintenance utility for CapStone_BBO.
rem Moves root-level zip clutter into archive\ subfolders.
rem It does not touch live folders under data/, notebooks/, docs/, or scripts.
rem =========================================================

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI"
cd /d "%ROOT%"

set "AROOT=archive"
set "RZ=%AROOT%\root_zips"
set "PZ=%AROOT%\processed_zips"
set "NZ=%AROOT%\notebook_zips"
set "MZ=%AROOT%\misc_zips"

if not exist "%AROOT%" mkdir "%AROOT%"
if not exist "%RZ%" mkdir "%RZ%"
if not exist "%PZ%" mkdir "%PZ%"
if not exist "%NZ%" mkdir "%NZ%"
if not exist "%MZ%" mkdir "%MZ%"

echo Archiving root-level zip files from %ROOT% ...

for %%F in (*.zip) do (
    set "FN=%%~nxF"
    set "DEST=%RZ%"
    echo !FN! | findstr /i /c:"Capstone Project" >nul && set "DEST=%PZ%"
    echo !FN! | findstr /i /c:"notebook" >nul && set "DEST=%NZ%"
    echo !FN! | findstr /i /c:"initial_data" /c:"logs" /c:"plots" /c:"submissions" >nul && set "DEST=%MZ%"
    move /Y "%%~fF" "!DEST!\%%~nxF" >nul
    echo Moved: %%~nxF ^> !DEST!
)

echo.
echo Done.
exit /b 0
