@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem =========================================================
rem cap_scr_v010_copy_processed_outputs.cmd
rem
rem Purpose:
rem   Standalone utility. Copies outputs.txt from the processed
rem   drop-zone into submissions\week_xx\outputs.txt.
rem
rem Processed folder convention:
rem   data\processed\Capstone_Project_WeekXXSubmissionProcessed\outputs.txt
rem =========================================================

if "%~1"=="" (
    echo Usage: %~nx0 ^<week_number^>
    exit /b 1
)

set "WRAW=%~1"
for /f "delims=0123456789" %%A in ("%WRAW%") do (
    echo [ERROR] Week must be numeric. Got: %WRAW%
    exit /b 1
)

set /a WNUM=%WRAW% 2>nul
if %WNUM% LSS 1 ( echo [ERROR] Week must be between 1 and 99. & exit /b 1 )
if %WNUM% GTR 99 ( echo [ERROR] Week must be between 1 and 99. & exit /b 1 )
if %WNUM% LSS 10 ( set "WEEK=0%WNUM%" ) else ( set "WEEK=%WNUM%" )

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT=%%~fI"
cd /d "%ROOT%"

set "SRC=data\processed\Capstone_Project_Week%WEEK%SubmissionProcessed\outputs.txt"
set "DSTDIR=data\submissions\week_%WEEK%"
set "DST=%DSTDIR%\outputs.txt"
set "LOGFILE=data\logs\ingest_log.txt"

if not exist "%SRC%" (
    echo [ERROR] Could not find processed outputs.txt for Week %WEEK%.
    echo Checked:
    echo   %SRC%
    exit /b 1
)

echo.
echo ==========================================
echo  Week %WEEK% - copy processed outputs.txt
echo ==========================================
echo  Source : %SRC%
echo  Target : %DST%
echo.

set /a NONEMPTY=0
set "BADLINE="

for /f "usebackq delims=" %%L in ("%SRC%") do (
    set "LINE=%%L"
    if not "!LINE!"=="" (
        set /a NONEMPTY+=1
        echo(!LINE!| findstr /c:"	" >nul && set "BADLINE=tab"
        echo(!LINE!| findstr /c:"," >nul && set "BADLINE=comma"
        echo(!LINE!| findstr /c:"np.float64" >nul && set "BADLINE=np.float64 wrapper"
    )
)

if defined BADLINE (
    echo [ERROR] Source file does not look like one value per line.
    echo Found a line containing: %BADLINE%
    echo Review: %SRC%
    exit /b 1
)

if not %NONEMPTY%==8 (
    echo [ERROR] Source must contain exactly 8 non-empty lines. Found: %NONEMPTY%
    echo Review: %SRC%
    exit /b 1
)

echo [OK] Source format valid: 8 non-empty lines, one value per line.
echo.

echo Source contents:
echo ------------------------------------------
type "%SRC%"
echo ------------------------------------------
echo.

if exist "%DST%" (
    echo Existing destination contents:
    echo ------------------------------------------
    type "%DST%"
    echo ------------------------------------------
    echo.
    set "STAMP="
    for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss" 2^>nul') do set "STAMP=%%I"
    if not defined STAMP set "STAMP=backup"
    copy /y "%DST%" "%DSTDIR%\outputs_before_overwrite_%STAMP%.bak" >nul
    echo [OK] Backup: %DSTDIR%\outputs_before_overwrite_%STAMP%.bak
    echo.
) else (
    echo No existing destination file. A new one will be created.
    echo.
)

if not exist "%DSTDIR%\" mkdir "%DSTDIR%"

set /p "CONFIRM= Overwrite %DST% with processed Week %WEEK% outputs? (Y/N): "
if /I not "%CONFIRM%"=="Y" ( echo Cancelled. & exit /b 0 )

copy /y "%SRC%" "%DST%" >nul
if errorlevel 1 ( echo [ERROR] Copy failed. & exit /b 1 )

if not exist "data\logs\" mkdir "data\logs"
set "DT="
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss" 2^>nul') do set "DT=%%I"
if not defined DT set "DT=unknown_time"
echo [%DT%] Week %WEEK% outputs.txt copied from "%SRC%" (copy_processed_outputs) >> "%LOGFILE%"

echo.
echo [OK] Copied successfully.
echo Final destination:
echo ------------------------------------------
type "%DST%"
echo ------------------------------------------
echo.
echo [LOG] Appended to %LOGFILE%
echo.

exit /b 0
