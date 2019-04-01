@echo OFF
set LOGFILE=run.log
call :sub > %LOGFILE% 2>&1
exit /b

:sub
sphinx-build -E %~dp0\source %~dp0\build 