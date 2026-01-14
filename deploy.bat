@echo off
REM Account Management System - Docker Build & Deploy Script (Windows)

echo ========================================
echo   Account Management System - Deploy
echo ========================================

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Docker is not installed
    exit /b 1
)

REM Create data directory
if not exist data mkdir data

REM Create .env file if not exists
if not exist .env (
    echo Creating .env file from .env.example...
    if exist .env.example (
        copy .env.example .env
        echo Please edit .env file to set a secure SECRET_KEY
    ) else (
        echo Error: .env.example not found
        exit /b 1
    )
)

REM Parse command line arguments
set ACTION=%1
if "%ACTION%"=="" set ACTION=up

if "%ACTION%"=="build" (
    echo Building Docker images...
    docker-compose build --no-cache
    echo Build completed!
    goto :end
)

if "%ACTION%"=="up" (
    echo Starting services...
    docker-compose up -d --build
    echo.
    echo Services started!
    echo Access the application at: http://localhost:8080
    goto :end
)

if "%ACTION%"=="down" (
    echo Stopping services...
    docker-compose down
    echo Services stopped!
    goto :end
)

if "%ACTION%"=="restart" (
    echo Restarting services...
    docker-compose restart
    echo Services restarted!
    goto :end
)

if "%ACTION%"=="logs" (
    docker-compose logs -f
    goto :end
)

if "%ACTION%"=="clean" (
    echo Cleaning up...
    docker-compose down -v --rmi local
    echo Cleanup completed!
    goto :end
)

echo Usage: deploy.bat {build^|up^|down^|restart^|logs^|clean}
echo.
echo Commands:
echo   build   - Build Docker images without cache
echo   up      - Build and start services (default)
echo   down    - Stop and remove containers
echo   restart - Restart services
echo   logs    - View logs
echo   clean   - Remove containers, volumes, and images
exit /b 1

:end
