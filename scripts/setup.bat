@echo off
REM JobScraper - Script d'installation (Windows)

echo ==========================================
echo    JobScraper - Installation
echo ==========================================
echo.

REM Check Python
echo [1/5] Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas installe. Veuillez l'installer.
    exit /b 1
)
python --version

REM Check Node.js
echo [2/5] Verification de Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js n'est pas installe. Veuillez l'installer.
    exit /b 1
)
node --version

REM Setup Backend
echo [3/5] Installation du Backend...
cd backend

if not exist "venv" (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium

cd ..

REM Setup Frontend
echo [4/5] Installation du Frontend...
cd frontend
call npm install
cd ..

REM Create .env if not exists
echo [5/5] Configuration...
if not exist ".env" (
    copy .env.example .env
    echo Fichier .env cree depuis .env.example
)

echo.
echo ==========================================
echo    Installation terminee avec succes!
echo ==========================================
echo.
echo Pour demarrer l'application:
echo.
echo   Backend:  cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo   Frontend: cd frontend ^&^& npm run dev
echo.
echo Ou avec Docker:
echo   docker-compose up --build
echo ==========================================

pause
