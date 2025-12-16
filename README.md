# JobScraper

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Application web de scraping d'offres d'emploi depuis plusieurs sources, avec interface moderne et export des donnees.

![JobScraper Preview](docs/preview.png)

## Fonctionnalites

- **Recherche multi-sources** : RemoteOK, Jobicy, Arbeitnow, Welcome to the Jungle
- **Filtres avances** : mots-cles, localisation, type de contrat, remote only
- **Tri des resultats** : par date, salaire, pertinence
- **Export des donnees** : CSV et JSON
- **Interface responsive** : design moderne avec Tailwind CSS
- **Pagination** : navigation facile dans les resultats

## Stack Technique

| Composant | Technologies |
|-----------|-------------|
| **Backend** | FastAPI, httpx, BeautifulSoup4, Playwright, Pydantic |
| **Frontend** | React 18, TypeScript, Tailwind CSS, Vite |
| **Infrastructure** | Docker, Docker Compose, Nginx |

## Installation Rapide

### Option 1 : Scripts automatises

**Windows :**
```bash
scripts\setup.bat
```

**Linux/Mac :**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Option 2 : Docker (Recommande pour la production)

```bash
# Lancer toute l'application
docker-compose up -d

# Acceder a l'application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# Documentation: http://localhost:8000/docs
```

### Option 3 : Installation manuelle

#### Backend

```bash
cd backend

# Creer l'environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate

# Activer l'environnement (Linux/Mac)
source venv/bin/activate

# Installer les dependances
pip install -r requirements.txt

# Installer Playwright (pour Welcome to the Jungle)
playwright install chromium

# Lancer le serveur
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Installer les dependances
npm install

# Lancer le serveur de developpement
npm run dev
```

## Configuration

Copiez `.env.example` vers `.env` et ajustez les valeurs :

```env
# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Frontend Configuration
VITE_API_URL=http://localhost:8000

# Scraping Configuration
SCRAPER_DELAY=1.0
MAX_RETRIES=3
```

## Utilisation

1. Ouvrir le frontend sur `http://localhost:5173` (dev) ou `http://localhost` (Docker)
2. Entrer des mots-cles de recherche (ex: "developer", "react", "python")
3. Optionnel: ajouter une localisation, un type de contrat
4. Selectionner les sources a scraper
5. Cliquer sur "Rechercher"
6. Parcourir les resultats et exporter en CSV/JSON si necessaire

## API Endpoints

### POST /api/search

Lance une recherche d'offres d'emploi.

```json
{
  "keywords": "developer react",
  "location": "Paris",
  "sources": ["remoteok", "jobicy", "arbeitnow", "welcometothejungle"],
  "remote": false,
  "contractType": "CDI"
}
```

### GET /api/export?format=csv|json

Exporte les derniers resultats de recherche.

### GET /api/health

Verification de l'etat de l'API.

## Documentation API

La documentation interactive est disponible sur:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Structure du Projet

```
JobScraper/
├── backend/
│   ├── app/
│   │   ├── api/              # Routes API (future)
│   │   ├── core/             # Configuration
│   │   │   └── config.py
│   │   ├── scrapers/         # Modules de scraping
│   │   │   ├── remoteok.py
│   │   │   ├── jobicy.py
│   │   │   ├── arbeitnow.py
│   │   │   └── welcometothejungle.py
│   │   ├── services/
│   │   │   └── export_service.py
│   │   ├── main.py           # Point d'entree FastAPI
│   │   └── models.py         # Modeles Pydantic
│   ├── tests/                # Tests unitaires
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # Composants React
│   │   ├── services/         # Appels API
│   │   ├── types/            # Types TypeScript
│   │   ├── hooks/            # Custom hooks
│   │   ├── utils/            # Utilitaires
│   │   └── App.tsx
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   └── CAHIER_DES_CHARGES.md
├── scripts/
│   ├── setup.sh              # Script d'installation Linux/Mac
│   └── setup.bat             # Script d'installation Windows
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## Sources de Donnees

| Source | Type | Methode | Status |
|--------|------|---------|--------|
| RemoteOK | API JSON | httpx | Active |
| Jobicy | API JSON | httpx | Active |
| Arbeitnow | API JSON | httpx | Active |
| Welcome to the Jungle | Web | Playwright | Active |

## Deploiement

### Docker Compose (Production)

```bash
# Build et lancement
docker-compose up -d --build

# Voir les logs
docker-compose logs -f

# Arreter
docker-compose down
```

### Backend (Railway/Render)

1. Connecter le repository GitHub
2. Configurer les variables d'environnement
3. Deployer le dossier `backend/`

### Frontend (Vercel)

1. Connecter le repository GitHub
2. Configurer `VITE_API_URL` vers l'URL du backend
3. Deployer le dossier `frontend/`

## Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Contribution

1. Fork le projet
2. Creer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## License

Distribue sous licence MIT. Voir [LICENSE](LICENSE) pour plus d'informations.

---

**JobScraper** - Projet Portfolio
