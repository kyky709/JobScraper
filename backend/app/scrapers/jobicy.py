import httpx
import asyncio
from typing import List, Optional
from datetime import datetime
import uuid
import re
import html
from bs4 import BeautifulSoup

from app.models import JobOffer

JOBICY_URL = "https://jobicy.com/api/v2/remote-jobs"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


async def scrape_jobicy(
    keywords: str,
    location: Optional[str] = None,
    contract_type: Optional[str] = None,
    remote: bool = False,
    max_results: int = 50
) -> List[JobOffer]:
    """
    Scrape les offres d'emploi depuis Jobicy API.

    Args:
        keywords: Mots-clés de recherche
        location: Localisation
        contract_type: Type de contrat
        remote: Uniquement les offres remote
        max_results: Nombre maximum de résultats

    Returns:
        Liste des offres d'emploi
    """
    jobs = []
    keywords_lower = keywords.lower().split()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Récupérer plus de jobs sans filtre tag pour chercher dans le contenu
            params = {
                "count": 50  # Max allowed by API
            }

            response = await client.get(JOBICY_URL, headers=HEADERS, params=params)
            response.raise_for_status()

            data = response.json()
            job_listings = data.get("jobs", [])

            for job_data in job_listings:
                if len(jobs) >= max_results:
                    break

                # Extraire et décoder les données (HTML entities)
                title = html.unescape(job_data.get("jobTitle", "") or "")
                company = html.unescape(job_data.get("companyName", "Entreprise") or "Entreprise")
                description = html.unescape(job_data.get("jobDescription", "") or "")
                job_location_raw = job_data.get("jobGeo", "Remote")

                # Gérer le cas où job_location est une liste
                if isinstance(job_location_raw, list):
                    job_location = ", ".join(str(loc) for loc in job_location_raw) if job_location_raw else "Remote"
                else:
                    job_location = str(job_location_raw) if job_location_raw else "Remote"

                # Vérifier si les mots-clés correspondent
                search_text = f"{title} {company} {description}".lower()
                if not any(kw in search_text for kw in keywords_lower):
                    continue

                # Filtrer par localisation si spécifié
                if location and location.lower() not in job_location.lower():
                    continue

                # Type de contrat
                job_type_raw = job_data.get("jobType", "")
                if isinstance(job_type_raw, list):
                    job_type = " ".join(str(jt) for jt in job_type_raw).lower()
                else:
                    job_type = str(job_type_raw).lower() if job_type_raw else ""

                job_contract_type = None
                if "full" in job_type:
                    job_contract_type = "CDI"
                elif "part" in job_type:
                    job_contract_type = "Temps partiel"
                elif "contract" in job_type:
                    job_contract_type = "CDD"
                elif "freelance" in job_type:
                    job_contract_type = "Freelance"

                # Expérience
                experience_raw = job_data.get("jobExperience", "")
                if isinstance(experience_raw, list):
                    experience = " ".join(str(e) for e in experience_raw).lower()
                else:
                    experience = str(experience_raw).lower() if experience_raw else ""

                experience_level = None
                if experience:
                    if "junior" in experience or "entry" in experience:
                        experience_level = "Junior"
                    elif "senior" in experience:
                        experience_level = "Senior"
                    elif "mid" in experience:
                        experience_level = "Confirmé"

                # Salaire
                salary_min = job_data.get("annualSalaryMin")
                salary_max = job_data.get("annualSalaryMax")
                salary_currency = job_data.get("salaryCurrency", "USD")
                salary = None
                if salary_min and salary_max:
                    salary = f"{salary_min}-{salary_max} {salary_currency}"
                elif salary_min:
                    salary = f"{salary_min}+ {salary_currency}"

                # Date de publication
                posted_at = job_data.get("pubDate")

                # Nettoyer la description HTML
                if description:
                    soup = BeautifulSoup(description, "html.parser")
                    clean_description = soup.get_text()[:500]
                else:
                    clean_description = None

                # Tags
                tags = []
                job_industry = job_data.get("jobIndustry", [])
                if isinstance(job_industry, list):
                    tags.extend(job_industry[:5])
                elif isinstance(job_industry, str):
                    tags.append(job_industry)

                job = JobOffer(
                    id=str(uuid.uuid4()),
                    title=title or "Unknown Position",
                    company=company,
                    location=job_location or "Remote",
                    salary=salary,
                    contract_type=job_contract_type or contract_type,
                    experience_level=experience_level,
                    description=clean_description,
                    url=job_data.get("url", ""),
                    source="jobicy",
                    posted_at=posted_at,
                    scraped_at=datetime.utcnow().isoformat() + "Z",
                    tags=tags if tags else None
                )

                jobs.append(job)

    except httpx.HTTPStatusError as e:
        raise Exception(f"Jobicy API error: {e.response.status_code}")
    except httpx.RequestError as e:
        raise Exception(f"Jobicy connection error: {str(e)}")
    except Exception as e:
        raise Exception(f"Jobicy scraping error: {str(e)}")

    return jobs
