@echo off
REM SQL Generator Quick Commands
REM Usage: run_commands.bat [command] [query]

echo.
echo ===============================================
echo   SQL Generator - Command Line Interface
echo ===============================================
echo.

if "%1"=="" goto interactive
if "%1"=="help" goto help
if "%1"=="setup" goto setup
if "%1"=="schema" goto schema
if "%1"=="quick" goto quick
if "%1"=="analyze" goto analyze
if "%1"=="query" goto query

:help
echo Available commands:
echo.
echo   run_commands.bat                    - Interactive mode
echo   run_commands.bat setup              - Initialize embeddings (first-time setup)
echo   run_commands.bat quick              - Quick interactive mode
echo   run_commands.bat schema             - Show schema information
echo   run_commands.bat query "your query" - Generate SQL for query
echo   run_commands.bat analyze "query"    - Generate SQL with analysis
echo   run_commands.bat help               - Show this help
echo.
goto end

:quick
echo Starting Quick SQL Generator...
python quick_sql.py
goto end

:schema
echo Showing schema information...
python run_sql_generator.py --schema-info
goto end

:query
if "%2"=="" (
    echo Error: Please provide a query
    echo Example: run_commands.bat query "Show me all customers"
    goto end
)
echo Generating SQL for: %2
python run_sql_generator.py --query %2
goto end

:analyze
if "%2"=="" (
    echo Error: Please provide a query
    echo Example: run_commands.bat analyze "Show me all customers"
    goto end
)
echo Generating SQL with analysis for: %2
python run_sql_generator.py --query %2 --analyze
goto end

:interactive
echo Starting interactive mode...
python run_sql_generator.py --interactive
goto end

:end
echo.
echo Done!
