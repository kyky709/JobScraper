from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from datetime import datetime
from typing import Optional, List, Callable, Any
import asyncio
import re
import math

from app.models import SearchRequest, SearchResponse, HealthResponse, JobOffer
from app.scrapers.remoteok import scrape_remoteok
from app.scrapers.welcometothejungle import scrape_welcometothejungle
from app.scrapers.jobicy import scrape_jobicy
from app.services.export_service import export_to_csv, export_to_json

# Stockage temporaire des derniers résultats pour l'export
last_results: List[JobOffer] = []

# Configuration du retry
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # secondes


async def retry_scraper(
    scraper_func: Callable,
    source_name: str,
    max_retries: int = MAX_RETRIES,
    **kwargs
) -> List[JobOffer]:
    """
    Exécute un scraper avec mécanisme de retry et backoff exponentiel.
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            return await scraper_func(**kwargs)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = RETRY_DELAY * (2 ** attempt)
                await asyncio.sleep(delay)
    raise last_error


def parse_salary(salary_str: Optional[str]) -> Optional[int]:
    """
    Parse une chaîne de salaire pour extraire une valeur numérique moyenne.
    Retourne None si le parsing échoue.
    """
    if not salary_str:
        return None

    # Nettoyer la chaîne
    salary_clean = salary_str.replace(",", "").replace(" ", "").upper()

    # Chercher les nombres (supporter K pour milliers)
    numbers = re.findall(r"(\d+(?:\.\d+)?)\s*K?", salary_clean)
    if not numbers:
        return None

    values = []
    for num in numbers:
        val = float(num)
        if "K" in salary_clean:
            val *= 1000
        values.append(val)

    # Retourner la moyenne si range, sinon la valeur unique
    if len(values) >= 2:
        return int((values[0] + values[1]) / 2)
    elif len(values) == 1:
        return int(values[0])
    return None


def filter_jobs(
    jobs: List[JobOffer],
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    experience_level: Optional[str] = None
) -> List[JobOffer]:
    """
    Filtre les offres selon les critères avancés.
    """
    filtered = []

    for job in jobs:
        # Filtre par salaire
        if salary_min or salary_max:
            job_salary = parse_salary(job.salary)
            if job_salary is not None:
                if salary_min and job_salary < salary_min:
                    continue
                if salary_max and job_salary > salary_max:
                    continue
            elif salary_min or salary_max:
                # Si pas de salaire et filtre actif, on garde quand même (optionnel)
                pass

        # Filtre par niveau d'expérience
        if experience_level:
            if job.experience_level:
                if experience_level.lower() not in job.experience_level.lower():
                    continue
            else:
                # Si pas d'info experience, on garde
                pass

        filtered.append(job)

    return filtered


def sort_jobs(jobs: List[JobOffer], sort_by: str = "date") -> List[JobOffer]:
    """
    Trie les offres selon le critère spécifié.
    """
    if sort_by == "date":
        # Trier par date de publication (récentes en premier)
        return sorted(
            jobs,
            key=lambda x: x.posted_at or x.scraped_at or "",
            reverse=True
        )
    elif sort_by == "salary":
        # Trier par salaire (plus élevé en premier)
        def salary_key(job):
            salary = parse_salary(job.salary)
            return salary if salary is not None else 0
        return sorted(jobs, key=salary_key, reverse=True)
    elif sort_by == "relevance":
        # Pour la pertinence, on garde l'ordre original (déjà filtré par keywords)
        return jobs
    else:
        return jobs


def paginate_jobs(
    jobs: List[JobOffer],
    page: int = 1,
    limit: int = 20
) -> tuple[List[JobOffer], int, bool, bool]:
    """
    Pagine les résultats.
    Retourne (jobs_page, total_pages, has_next, has_previous)
    """
    total = len(jobs)
    total_pages = math.ceil(total / limit) if total > 0 else 1

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit

    paginated = jobs[start_idx:end_idx]
    has_next = page < total_pages
    has_previous = page > 1

    return paginated, total_pages, has_next, has_previous

app = FastAPI(
    title="JobScraper API",
    description="API de scraping d'offres d'emploi depuis plusieurs sources",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS pour le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Vérifie l'état de l'API.

    Returns:
        Status de l'API et timestamp
    """
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.post("/api/search", response_model=SearchResponse, tags=["Search"])
async def search_jobs(request: SearchRequest):
    """
    Lance une recherche d'offres d'emploi.

    Scrape les sources sélectionnées et retourne les résultats agrégés.

    **Paramètres de recherche:**
    - `keywords`: Mots-clés de recherche (requis)
    - `location`: Localisation souhaitée
    - `sources`: Sources à interroger (remoteok, jobicy, arbeitnow, welcometothejungle)
    - `contractType`: Type de contrat (CDI, CDD, Stage, etc.)
    - `remote`: Uniquement les offres remote
    - `salaryMin`: Salaire minimum annuel
    - `salaryMax`: Salaire maximum annuel
    - `experienceLevel`: Niveau d'expérience (Junior, Confirmé, Senior)
    - `sortBy`: Tri des résultats (date, salary, relevance)
    - `page`: Numéro de page (défaut: 1)
    - `limit`: Résultats par page (défaut: 20, max: 100)

    Returns:
        Résultats paginés avec métadonnées
    """
    global last_results

    all_jobs: List[JobOffer] = []
    errors: List[str] = []

    # Déterminer les sources à scraper
    sources = request.sources or ["remoteok", "jobicy"]

    # Créer les tâches de scraping avec retry
    scraper_tasks = []

    if "remoteok" in sources:
        scraper_tasks.append(("remoteok", retry_scraper(
            scrape_remoteok,
            "remoteok",
            keywords=request.keywords,
            location=request.location,
            contract_type=request.contract_type
        )))

    if "welcometothejungle" in sources:
        scraper_tasks.append(("welcometothejungle", retry_scraper(
            scrape_welcometothejungle,
            "welcometothejungle",
            keywords=request.keywords,
            location=request.location,
            contract_type=request.contract_type,
            remote=request.remote or False
        )))

    if "jobicy" in sources:
        scraper_tasks.append(("jobicy", retry_scraper(
            scrape_jobicy,
            "jobicy",
            keywords=request.keywords,
            location=request.location,
            contract_type=request.contract_type,
            remote=request.remote or False
        )))

    # Exécuter les scrapers en parallèle avec gestion des erreurs
    for source_name, task in scraper_tasks:
        try:
            jobs = await task
            all_jobs.extend(jobs)
        except Exception as e:
            error_msg = f"{source_name}: {str(e)}"
            errors.append(error_msg)

    # Appliquer les filtres avancés
    filtered_jobs = filter_jobs(
        all_jobs,
        salary_min=request.salary_min,
        salary_max=request.salary_max,
        experience_level=request.experience_level
    )

    # Trier les résultats
    sorted_jobs = sort_jobs(filtered_jobs, sort_by=request.sort_by or "date")

    # Sauvegarder tous les résultats pour l'export (avant pagination)
    last_results = sorted_jobs

    # Appliquer la pagination
    page = request.page or 1
    limit = request.limit or 20
    paginated_jobs, total_pages, has_next, has_previous = paginate_jobs(
        sorted_jobs, page=page, limit=limit
    )

    scraped_at = datetime.utcnow().isoformat() + "Z"

    return SearchResponse(
        success=len(all_jobs) > 0 or len(errors) == 0,
        total_results=len(sorted_jobs),
        results=paginated_jobs,
        scraped_at=scraped_at,
        errors=errors if errors else None,
        page=page,
        limit=limit,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous
    )


@app.get("/api/export", tags=["Export"])
async def export_results(
    format: str = Query("csv", description="Format d'export: 'csv' ou 'json'")
):
    """
    Exporte les derniers résultats de recherche.

    Args:
        format: Format d'export souhaité ('csv' ou 'json')

    Returns:
        Fichier téléchargeable au format demandé
    """
    global last_results

    if not last_results:
        raise HTTPException(
            status_code=404,
            detail="Aucun résultat à exporter. Effectuez d'abord une recherche."
        )

    if format.lower() == "csv":
        content = export_to_csv(last_results)
        return Response(
            content=content,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=job_offers.csv"
            }
        )
    elif format.lower() == "json":
        content = export_to_json(last_results)
        return Response(
            content=content,
            media_type="application/json",
            headers={
                "Content-Disposition": "attachment; filename=job_offers.json"
            }
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Format non supporté. Utilisez 'csv' ou 'json'."
        )


@app.get("/", tags=["Root"])
async def root():
    """
    Page d'accueil de l'API.
    """
    return {
        "message": "Bienvenue sur JobScraper API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/api/health"
    }


# Gestion globale des erreurs
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire global des exceptions non gérées"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Une erreur interne s'est produite",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
