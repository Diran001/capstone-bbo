@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: =============================================================================
:: cap_scr_v010_week.cmd  <command>  [week_number]
::
:: Single entry point for weekly CapStone_BBO operations.
::
:: Run from the repository root, for example:
::   .\scripts\cap_scr_v010_week.cmd prepare 8
::   .\scripts\cap_scr_v010_week.cmd register 8
::   .\scripts\cap_scr_v010_week.cmd check 8
::   .\scripts\cap_scr_v010_week.cmd status
::   .\scripts\cap_scr_v010_week.cmd run 8
::   .\scripts\cap_scr_v010_week.cmd tag 8
::
:: Live folder conventions:
::   data\processed\Capstone_Project_WeekXXSubmissionProcessed\
::   data\submissions\week_XX\
::   data\logs\cmd\
:: =============================================================================

if defined CAPSTONE_CMD_LOGGING goto :route

set "ACTION=%~1"
if not defined ACTION goto :usage

if not defined CAPSTONE_LOG_BASENAME (
    if /i "%ACTION%"=="prepare"  set "CAPSTONE_LOG_BASENAME=prepare_week.log"
    if /i "%ACTION%"=="register" set "CAPSTONE_LOG_BASENAME=register_week.log"
    if /i "%ACTION%"=="check"    set "CAPSTONE_LOG_BASENAME=check_week.log"
    if /i "%ACTION%"=="status"   set "CAPSTONE_LOG_BASENAME=status.log"
    if /i "%ACTION%"=="tag"      set "CAPSTONE_LOG_BASENAME=tag_week.log"
    if /i "%ACTION%"=="run"      set "CAPSTONE_LOG_BASENAME=run_week.log"
    if not defined CAPSTONE_LOG_BASENAME set "CAPSTONE_LOG_BASENAME=cap_scr_v010_week.log"
)

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO=%%~fI"
cd /d "%REPO%"

if not defined CAPSTONE_LOG_RUN_DIR (
    call :timestamp RUNTS
    if not defined RUNTS set "RUNTS=unknown_time"
    if not exist "data\logs" mkdir "data\logs" >nul 2>&1
    if not exist "data\logs\cmd" mkdir "data\logs\cmd" >nul 2>&1
    set "CAPSTONE_LOG_RUN_DIR=%REPO%\data\logs\cmd\log_!RUNTS!"
)
if not exist "%CAPSTONE_LOG_RUN_DIR%" mkdir "%CAPSTONE_LOG_RUN_DIR%" >nul 2>&1

set "LOGFILE=%CAPSTONE_LOG_RUN_DIR%\%CAPSTONE_LOG_BASENAME%"
echo [INFO] Logging to: %LOGFILE%

set "CAPSTONE_CMD_LOGGING=1"
cmd /d /v:on /c ""%~f0" %* > "%LOGFILE%" 2>&1"
set "RC=%ERRORLEVEL%"

echo [INFO] Exit code: %RC%
echo [INFO] Log saved: %LOGFILE%
exit /b %RC%

:route
set "CMD=%~1"
set "WRAW=%~2"
set "ARG3=%~3"

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO=%%~fI"
cd /d "%REPO%"

if /i "%CMD%"=="prepare"  goto :do_prepare
if /i "%CMD%"=="register" goto :do_register
if /i "%CMD%"=="check"    goto :do_check
if /i "%CMD%"=="status"   goto :do_status
if /i "%CMD%"=="tag"      goto :do_tag
if /i "%CMD%"=="run"      goto :do_run

:usage
echo.
echo Usage:
echo   .\scripts\cap_scr_v010_week.cmd prepare ^<week_number^>
echo   .\scripts\cap_scr_v010_week.cmd register ^<week_number^>
echo   .\scripts\cap_scr_v010_week.cmd check ^<week_number^>
echo   .\scripts\cap_scr_v010_week.cmd status
echo   .\scripts\cap_scr_v010_week.cmd run ^<week_number^>
echo   .\scripts\cap_scr_v010_week.cmd tag ^<week_number^>
echo.
exit /b 1

:do_prepare
call :pad_week "%WRAW%" || goto :end
set "PDIR=data\processed\Capstone_Project_Week%WEEK%SubmissionProcessed"
set "SDIR=data\submissions\week_%WEEK%"

if not exist "data" mkdir "data"
if not exist "data\processed" mkdir "data\processed"
if not exist "data\submissions" mkdir "data\submissions"

if not exist "%PDIR%\" (
    mkdir "%PDIR%"
    echo [CREATED]  %PDIR%
) else (
    echo [EXISTS]   %PDIR%
)

if not exist "%SDIR%\" (
    mkdir "%SDIR%"
    echo [CREATED]  %SDIR%
) else (
    echo [EXISTS]   %SDIR%
)

echo.
echo Next: place inputs.txt and outputs.txt into:
echo   %PDIR%\
echo Then run:
echo   .\scripts\cap_scr_v010_week.cmd register %WEEK%
echo.
goto :end

:do_register
call :pad_week "%WRAW%" || goto :end
set "SRC=data\processed\Capstone_Project_Week%WEEK%SubmissionProcessed"
set "DST=data\submissions\week_%WEEK%"
set "INGESTLOG=data\logs\ingest_log.txt"

echo.
echo Registering Week %WEEK%
echo   Source : %SRC%
echo   Target : %DST%
echo.

if not exist "%SRC%\" (
    echo [ERROR] Processed folder not found:
    echo   %SRC%
    echo Run:
    echo   .\scripts\cap_scr_v010_week.cmd prepare %WEEK%
    goto :end
)

set "ABORT=0"
if not exist "%SRC%\inputs.txt"  ( echo [MISSING] %SRC%\inputs.txt  & set "ABORT=1" )
if not exist "%SRC%\outputs.txt" ( echo [MISSING] %SRC%\outputs.txt & set "ABORT=1" )
if "%ABORT%"=="1" (
    echo.
    echo Place both files into the processed folder and re-run.
    goto :end
)

if not exist "%DST%\" mkdir "%DST%"

if exist "%DST%\inputs.txt"  copy /Y "%DST%\inputs.txt"  "%DST%\inputs_prev.txt"  >nul
if exist "%DST%\outputs.txt" copy /Y "%DST%\outputs.txt" "%DST%\outputs_prev.txt" >nul

copy /Y "%SRC%\inputs.txt"  "%DST%\inputs.txt"  >nul
if errorlevel 1 ( echo [ERROR] Failed to copy inputs.txt  & goto :end )

copy /Y "%SRC%\outputs.txt" "%DST%\outputs.txt" >nul
if errorlevel 1 ( echo [ERROR] Failed to copy outputs.txt & goto :end )

echo [OK] inputs.txt   -> %DST%\inputs.txt
echo [OK] outputs.txt  -> %DST%\outputs.txt

if not exist "data\logs" mkdir "data\logs"
call :timestamp DT
if not defined DT set "DT=unknown_time"
echo [%DT%] Week %WEEK% registered from %SRC% >> "%INGESTLOG%"
echo [LOG] Appended to %INGESTLOG%

echo.
echo --- outputs.txt (Week %WEEK%) ---
type "%DST%\outputs.txt"
echo ----------------------------------
echo.
echo Next:
echo   .\scripts\cap_scr_v010_week.cmd check %WEEK%
echo.
goto :end

:do_check
call :pad_week "%WRAW%" || goto :end
set "PDIR=data\processed\Capstone_Project_Week%WEEK%SubmissionProcessed"
set "SDIR=data\submissions\week_%WEEK%"

echo.
echo ==========================================
echo  Check - Week %WEEK%
echo ==========================================
echo.
echo  Processed  [%PDIR%]
call :chk_file "%PDIR%"             "folder"
call :chk_file "%PDIR%\inputs.txt"  "inputs.txt"
call :chk_file "%PDIR%\outputs.txt" "outputs.txt"
echo.
echo  Canonical  [%SDIR%]
call :chk_file "%SDIR%"             "folder"
call :chk_file "%SDIR%\inputs.txt"  "inputs.txt"
call :chk_file "%SDIR%\outputs.txt" "outputs.txt"
echo.
goto :end

:do_status
echo.
echo =============================================================================
echo  CapStone_BBO - Status
echo =============================================================================
echo  Wk   proc\in  proc\out  sub\in  sub\out  State
echo  --   -------  --------  ------  -------  -----

for /L %%W in (1,1,12) do (
    set "WPAD=0%%W"
    if %%W GEQ 10 set "WPAD=%%W"

    set "PDIR=data\processed\Capstone_Project_Week!WPAD!SubmissionProcessed"
    set "SDIR=data\submissions\week_!WPAD!"

    set "PI=--" & set "PO=--" & set "SI=--" & set "SO=--"
    set "STATE="

    if exist "!PDIR!\inputs.txt"  set "PI=OK"
    if exist "!PDIR!\outputs.txt" set "PO=OK"
    if exist "!SDIR!\inputs.txt"  set "SI=OK"
    if exist "!SDIR!\outputs.txt" set "SO=OK"

    if "!SI!"=="OK" if "!SO!"=="OK" set "STATE=complete"
    if "!SI!"=="OK" if "!SO!"=="--" set "STATE=outputs pending"
    if "!PO!"=="OK" if "!SO!"=="--" set "STATE=READY - run register"
    if "!PI!"=="--" if "!SI!"=="--" set "STATE=(not started)"

    echo   !WPAD!   !PI!      !PO!       !SI!     !SO!      !STATE!
)
echo.
goto :end

:do_run
call :pad_week "%WRAW%" || goto :end
set "PDIR=data\processed\Capstone_Project_Week%WEEK%SubmissionProcessed"
set "SDIR=data\submissions\week_%WEEK%"
set "FORCE=0"
if /i "%ARG3%"=="--force" set "FORCE=1"

echo.
echo ============================================================
echo  Run - Week %WEEK%
echo ============================================================

echo.
echo [1/3] prepare
call :do_prepare >nul

if "%FORCE%"=="0" (
    if not exist "%PDIR%\outputs.txt" (
        echo.
        echo [WAITING] outputs.txt not yet in:
        echo   %PDIR%\
        echo.
        echo Place inputs.txt and outputs.txt there, then rerun:
        echo   .\scripts\cap_scr_v010_week.cmd run %WEEK%
        echo.
        echo To skip this check:
        echo   .\scripts\cap_scr_v010_week.cmd run %WEEK% --force
        goto :end
    )
)

echo.
echo [2/3] register
call :do_register >nul

echo.
echo [3/3] check
set "ALL_OK=1"
call :chk_file_run "%PDIR%"             "processed folder"
call :chk_file_run "%PDIR%\inputs.txt"  "processed inputs.txt"
call :chk_file_run "%PDIR%\outputs.txt" "processed outputs.txt"
call :chk_file_run "%SDIR%"             "submissions folder"
call :chk_file_run "%SDIR%\inputs.txt"  "submissions inputs.txt"
call :chk_file_run "%SDIR%\outputs.txt" "submissions outputs.txt"

if "%ALL_OK%"=="0" (
    echo.
    echo [WARN] One or more expected files are missing.
    goto :end
)

echo.
echo ============================================================
echo  Week %WEEK% - all steps complete
echo ============================================================
echo.
type "%SDIR%\outputs.txt"
echo.
goto :end

:do_tag
call :pad_week "%WRAW%" || goto :end
call :check_repo || goto :end

set "TAG=week-%WEEK%"

call :check_changes
if errorlevel 1 goto :end

call :check_clean_tag "%TAG%"
if errorlevel 1 goto :end

echo.
echo Repo: %REPO%
echo Tag : %TAG%
echo.

git -C "%REPO%" add -A
if errorlevel 1 goto :git_fail

git -C "%REPO%" commit -m "week %WEEK%: ingest results and update repository"
if errorlevel 1 goto :git_fail

git -C "%REPO%" tag "%TAG%"
if errorlevel 1 goto :git_fail

git -C "%REPO%" push
if errorlevel 1 goto :git_fail

git -C "%REPO%" push --tags
if errorlevel 1 goto :git_fail

echo.
echo [OK] Tag %TAG% pushed.
goto :end

:git_fail
echo.
echo [ERROR] A git step failed. Review the output above.
goto :end

:check_repo
if not exist "%REPO%\.git\" (
    echo [ERROR] %REPO% is not a Git repository.
    exit /b 1
)
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] git.exe not found on PATH.
    exit /b 1
)
exit /b 0

:check_changes
git -C "%REPO%" status --porcelain >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Could not inspect repo status.
    exit /b 1
)
for /f %%I in ('git -C "%REPO%" status --porcelain ^| find /c /v ""') do set "CHANGES=%%I"
if "%CHANGES%"=="0" (
    echo [ERROR] No changes to commit.
    exit /b 1
)
exit /b 0

:check_clean_tag
git -C "%REPO%" rev-parse -q --verify "refs/tags/%~1" >nul 2>&1
if not errorlevel 1 (
    echo [ERROR] Tag already exists locally: %~1
    exit /b 1
)
exit /b 0

:pad_week
set "WRAW_LOCAL=%~1"
if "%WRAW_LOCAL%"=="" (
    echo [ERROR] Missing week number.
    exit /b 1
)
for /f "delims=0123456789" %%A in ("%WRAW_LOCAL%") do (
    echo [ERROR] Week must be numeric. Got: %WRAW_LOCAL%
    exit /b 1
)
set /a WNUM=%WRAW_LOCAL% 2>nul
if %WNUM% LSS 1 (
    echo [ERROR] Week must be between 1 and 99.
    exit /b 1
)
if %WNUM% GTR 99 (
    echo [ERROR] Week must be between 1 and 99.
    exit /b 1
)
if %WNUM% LSS 10 (
    set "WEEK=0%WNUM%"
) else (
    set "WEEK=%WNUM%"
)
exit /b 0

:chk_file
if exist "%~1\" ( echo   [OK]      %~2 & exit /b 0 )
if exist "%~1"  ( echo   [OK]      %~2 & exit /b 0 )
echo   [MISSING] %~2
exit /b 0

:chk_file_run
if exist "%~1\" ( echo   [OK]      %~2 & exit /b 0 )
if exist "%~1"  ( echo   [OK]      %~2 & exit /b 0 )
echo   [MISSING] %~2
set "ALL_OK=0"
exit /b 0

:timestamp
set "%~1="
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss" 2^>nul') do set "%~1=%%I"
if defined %~1 exit /b 0
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do if not defined %~1 set "%~1=%%I"
if defined %~1 (
    call set "%~1=%%%~1:~0,8%%_%%%~1:~8,6%%"
    exit /b 0
)
exit /b 0

:end
exit /b 0
EOF
cd /mnt/data && zip -q /mnt/data/CapStone_BBO_final_review_fixes.zip CapStone_BBO_final_review_fixes_cap_scr_v010_week_repaired.cmd CapStone_BBO_final_review_fixes_FINAL_CLEANUP_NOTE.txt CapStone_BBO_final_review_fixes_CHANGES_SUMMARY.txt
ls -l /mnt/data/CapStone_BBO_final_review_fixes*"],"timeout":300000}