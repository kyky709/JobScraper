#!/bin/bash

# JobScraper - Script d'installation (Linux/Mac)

set -e

echo "=========================================="
echo "   JobScraper - Installation"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}[1/5] Verification de Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "Python 3 n'est pas installe. Veuillez l'installer."
    exit 1
fi
python3 --version

# Check Node.js
echo -e "${BLUE}[2/5] Verification de Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo "Node.js n'est pas installe. Veuillez l'installer."
    exit 1
fi
node --version

# Setup Backend
echo -e "${BLUE}[3/5] Installation du Backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium

cd ..

# Setup Frontend
echo -e "${BLUE}[4/5] Installation du Frontend...${NC}"
cd frontend
npm install
cd ..

# Create .env if not exists
echo -e "${BLUE}[5/5] Configuration...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Fichier .env cree depuis .env.example"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "   Installation terminee avec succes!"
echo "=========================================="
echo ""
echo "Pour demarrer l'application:"
echo ""
echo "  Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "Ou avec Docker:"
echo "  docker-compose up --build"
echo "==========================================${NC}"
