@echo off
REM Financial Data Update Scheduler
REM Run this script daily to update company financial data
REM To schedule: Open Task Scheduler, create a new task, and set this script to run daily

echo Starting financial data update...
echo Date: %date%
echo Time: %time%

REM Change to the bizip directory
cd /d "%~dp0"

REM Run the Python update script
python update_financial_data.py

REM Check if the update was successful
if %errorlevel% equ 0 (
    echo Financial data update completed successfully!
) else (
    echo Financial data update failed with error code %errorlevel%
)

REM Pause to see the results (remove this line if running as a scheduled task)
pause 