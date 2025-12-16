# Cahier des Charges — JobScraper

## Scraper d'Offres d'Emploi avec Interface Web

**Version :** 1.0  
**Date :** Décembre 2024  
**Projet Portfolio Freelance**

---

## 1. Présentation du Projet

### 1.1 Contexte

Dans le cadre d'un portfolio freelance orienté développement web et automatisation, ce projet vise à démontrer des compétences en :

- Web scraping avec Python
- Développement d'API REST
- Création d'interface utilisateur moderne
- Intégration fullstack

### 1.2 Objectif

Développer une application web permettant de :

1. Scraper des offres d'emploi depuis plusieurs sources
2. Centraliser et filtrer les résultats
3. Visualiser les données via une interface intuitive
4. Exporter les résultats (CSV, JSON)

### 1.3 Cible Démonstration

- Recruteurs freelance
- Équipes RH de PME
- Candidats en recherche active
- Agences de recrutement

---

## 2. Périmètre Fonctionnel

### 2.1 Fonctionnalités Principales

#### F1 — Recherche d'offres

| ID | Fonctionnalité | Priorité |
|----|----------------|----------|
| F1.1 | Saisie de mots-clés (poste, compétences) | Haute |
| F1.2 | Sélection de la localisation (ville, région, remote) | Haute |
| F1.3 | Choix des sources à scraper | Moyenne |
| F1.4 | Filtres avancés (salaire, type contrat, expérience) | Moyenne |

#### F2 — Scraping

| ID | Fonctionnalité | Priorité |
|----|----------------|----------|
| F2.1 | Scraping de Welcome to the Jungle | Haute |
| F2.2 | Scraping de RemoteOK (jobs remote) | Haute |
| F2.3 | Scraping de Indeed France | Basse (anti-bot strict) |
| F2.4 | Gestion des erreurs et retry | Haute |
| F2.5 | Indicateur de progression en temps réel | Moyenne |

#### F3 — Affichage des Résultats

| ID | Fonctionnalité | Priorité |
|----|----------------|----------|
| F3.1 | Liste des offres avec pagination | Haute |
| F3.2 | Carte de chaque offre (titre, entreprise, lieu, salaire) | Haute |
| F3.3 | Tri par date, salaire, pertinence | Moyenne |
| F3.4 | Filtrage dynamique côté client | Moyenne |
| F3.5 | Vue détaillée d'une offre | Haute |

#### F4 — Export des Données

| ID | Fonctionnalité | Priorité |
|----|----------------|----------|
| F4.1 | Export CSV | Haute |
| F4.2 | Export JSON | Moyenne |
| F4.3 | Copier le lien de l'offre | Haute |

#### F5 — Interface Utilisateur

| ID | Fonctionnalité | Priorité |
|----|----------------|----------|
| F5.1 | Design moderne et responsive | Haute |
| F5.2 | Dark mode | Basse |
| F5.3 | Historique des recherches (localStorage) | Basse |
| F5.4 | État de chargement avec skeleton/spinner | Haute |

---

## 3. Spécifications Techniques

### 3.1 Architecture Générale

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│                   React + TypeScript                        │
│                      Tailwind CSS                           │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                              │
│                  FastAPI (Python)                           │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  API REST   │  │  Scraper    │  │  Export     │         │
│  │  Endpoints  │  │  Engine     │  │  Service    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Stack Technique

#### Backend

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| Framework API | FastAPI | Performance, async natif, documentation auto |
| Scraping | BeautifulSoup4 + httpx | Léger, suffisant pour les cibles |
| Async HTTP | httpx | Requêtes asynchrones performantes |
| Validation | Pydantic | Intégré à FastAPI, typage fort |

#### Frontend

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| Framework | React 18 | Maîtrisé, écosystème riche |
| Langage | TypeScript | Typage, maintenabilité |
| Styling | Tailwind CSS | Rapidité, cohérence |
| HTTP Client | Axios ou fetch | Requêtes API |
| State | useState/useReducer | Suffisant pour ce scope |

#### Outils

| Outil | Usage |
|-------|-------|
| Git/GitHub | Versioning |
| Vercel | Déploiement frontend |
| Railway / Render | Déploiement backend |
| VS Code | IDE |

### 3.3 Structure des Données

#### Offre d'Emploi (JobOffer)

```typescript
interface JobOffer {
  id: string;                    // UUID généré
  title: string;                 // Titre du poste
  company: string;               // Nom de l'entreprise
  location: string;              // Lieu (ville ou "Remote")
  salary?: string;               // Fourchette salariale si dispo
  contractType?: string;         // CDI, CDD, Freelance, Stage
  experienceLevel?: string;      // Junior, Mid, Senior
  description?: string;          // Description courte
  url: string;                   // Lien vers l'offre originale
  source: string;                // "welcometothejungle" | "remoteok"
  postedAt?: string;             // Date de publication
  scrapedAt: string;             // Date du scraping (ISO)
  tags?: string[];               // Compétences/tags
}
```

#### Requête de Recherche (SearchRequest)

```typescript
interface SearchRequest {
  keywords: string;              // Mots-clés recherchés
  location?: string;             // Localisation souhaitée
  sources?: string[];            // Sources à scraper
  contractType?: string;         // Filtre type de contrat
  remote?: boolean;              // Filtre remote only
}
```

#### Réponse de Recherche (SearchResponse)

```typescript
interface SearchResponse {
  success: boolean;
  totalResults: number;
  results: JobOffer[];
  scrapedAt: string;
  errors?: string[];             // Erreurs par source si applicable
}
```

---

## 4. Spécifications API

### 4.1 Endpoints

#### POST /api/search

Lance une recherche et scrape les sources.

**Request Body :**
```json
{
  "keywords": "développeur react",
  "location": "Paris",
  "sources": ["welcometothejungle", "remoteok"],
  "remote": false
}
```

**Response 200 :**
```json
{
  "success": true,
  "totalResults": 47,
  "results": [
    {
      "id": "abc123",
      "title": "Développeur React Senior",
      "company": "TechCorp",
      "location": "Paris",
      "salary": "55-65K€",
      "contractType": "CDI",
      "url": "https://...",
      "source": "welcometothejungle",
      "postedAt": "2024-12-10",
      "scrapedAt": "2024-12-15T14:30:00Z",
      "tags": ["React", "TypeScript", "Node.js"]
    }
  ],
  "scrapedAt": "2024-12-15T14:30:00Z"
}
```

#### GET /api/export

Exporte les derniers résultats.

**Query Parameters :**
- `format` : "csv" | "json"

**Response :** Fichier téléchargeable

#### GET /api/health

Health check de l'API.

**Response 200 :**
```json
{
  "status": "ok",
  "timestamp": "2024-12-15T14:30:00Z"
}
```

---

## 5. Maquettes & Interface

### 5.1 Page Principale

```
┌────────────────────────────────────────────────────────────────┐
│  🔍 JobScraper                                    [Dark Mode]  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  🔍  Rechercher un poste (ex: développeur react)        │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                │
│   ┌──────────────────┐  ┌──────────────────┐                   │
│   │ 📍 Localisation  │  │ 📋 Type contrat  │  [🚀 Rechercher] │
│   └──────────────────┘  └──────────────────┘                   │
│                                                                │
│   Sources:  [x] Welcome to the Jungle  [x] RemoteOK            │
│             [ ] Remote only                                    │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   47 résultats trouvés                    [Exporter CSV ⬇]    │
│                                                                │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │  Développeur React Senior              TechCorp          │ │
│   │  📍 Paris  💰 55-65K€  🏷️ CDI                            │ │
│   │  [React] [TypeScript] [Node.js]                          │ │
│   │                                        [Voir l'offre →]  │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │  Frontend Developer                    StartupXYZ        │ │
│   │  📍 Remote  💰 45-55K€  🏷️ CDI                           │ │
│   │  [Vue.js] [JavaScript]                                   │ │
│   │                                        [Voir l'offre →]  │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                │
│   [1] [2] [3] ... [10]  →                                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 5.2 États de l'Interface

| État | Affichage |
|------|-----------|
| Initial | Formulaire de recherche vide, message d'accueil |
| Loading | Skeleton cards + spinner + "Scraping en cours..." |
| Résultats | Liste des offres avec compteur |
| Aucun résultat | Message "Aucune offre trouvée" + suggestions |
| Erreur | Message d'erreur + bouton retry |

---

## 6. Stratégie de Scraping

### 6.1 Welcome to the Jungle

- **URL cible :** `https://www.welcometothejungle.com/fr/jobs`
- **Méthode :** Parsing HTML avec BeautifulSoup
- **Données extractibles :** Titre, entreprise, lieu, tags, lien
- **Pagination :** Query params `?page=X`
- **Rate limiting :** 1 requête/seconde recommandé

### 6.2 RemoteOK

- **URL cible :** `https://remoteok.com/api`
- **Méthode :** API JSON publique (plus simple)
- **Données extractibles :** Complètes (titre, salaire, tags, date)
- **Avantage :** Pas besoin de parsing HTML

### 6.3 Bonnes Pratiques Anti-Ban

```python
# Headers à utiliser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

# Délai entre requêtes
import asyncio
await asyncio.sleep(1)  # 1 seconde minimum
```

---

## 7. Plan de Développement

### Phase 1 — Backend (6-8h)

| Tâche | Temps estimé |
|-------|--------------|
| Setup FastAPI + structure projet | 1h |
| Scraper Welcome to the Jungle | 2h |
| Scraper RemoteOK | 1h |
| Endpoints API + validation | 2h |
| Export CSV/JSON | 1h |
| Tests manuels | 1h |

### Phase 2 — Frontend (5-7h)

| Tâche | Temps estimé |
|-------|--------------|
| Setup React + Tailwind | 30min |
| Composant SearchForm | 1h30 |
| Composant JobCard | 1h |
| Composant JobList + pagination | 1h30 |
| Intégration API + états loading/error | 1h30 |
| Export + finitions UI | 1h |

### Phase 3 — Déploiement (1-2h)

| Tâche | Temps estimé |
|-------|--------------|
| Déploiement backend (Railway/Render) | 30min |
| Déploiement frontend (Vercel) | 30min |
| Tests E2E | 30min |
| README GitHub | 30min |

**Total estimé : 12-17h**

---

## 8. Livrables Attendus

### 8.1 Code Source

- [ ] Repository GitHub public
- [ ] README complet (installation, usage, screenshots)
- [ ] Code commenté et structuré
- [ ] `.env.example` pour les variables d'environnement

### 8.2 Déploiement

- [ ] Backend live sur Railway ou Render
- [ ] Frontend live sur Vercel
- [ ] URLs fonctionnelles pour démonstration

### 8.3 Documentation

- [ ] Ce cahier des charges
- [ ] Documentation API (auto-générée par FastAPI : `/docs`)
- [ ] Screenshots/GIF de démonstration

---

## 9. Critères de Validation

| Critère | Validation |
|---------|------------|
| Recherche fonctionnelle | ✓ Retourne des offres pertinentes |
| Scraping multi-sources | ✓ Au moins 2 sources fonctionnelles |
| Interface responsive | ✓ Mobile + Desktop |
| Export données | ✓ CSV téléchargeable |
| Performance | ✓ Résultats en < 15 secondes |
| Gestion erreurs | ✓ Messages clairs, pas de crash |
| Code quality | ✓ Lisible, typé, structuré |

---

## 10. Évolutions Futures (Hors Scope v1)

Ces fonctionnalités ne sont pas incluses dans la v1 mais peuvent être ajoutées ultérieurement :

- Sauvegarde des offres en favoris
- Alertes email pour nouvelles offres
- Plus de sources (LinkedIn, Indeed, Glassdoor)
- Analyse des tendances (salaires moyens, compétences demandées)
- Authentification utilisateur
- Base de données persistante

---

## Annexes

### A. Ressources Utiles

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [httpx (async HTTP)](https://www.python-httpx.org/)

### B. Inspirations UI

- [RemoteOK](https://remoteok.com/) — Interface simple et efficace
- [Indeed](https://fr.indeed.com/) — Structure de résultats
- [Welcome to the Jungle](https://www.welcometothejungle.com/) — Design moderne

---

*Document généré le 15 décembre 2024*
