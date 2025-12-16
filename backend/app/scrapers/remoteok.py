import httpx
import asyncio
from typing import List, Optional
from datetime import datetime
import uuid

from app.models import JobOffer

REMOTEOK_API_URL = "https://remoteok.com/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


async def scrape_remoteok(
    keywords: str,
    location: Optional[str] = None,
    contract_type: Optional[str] = None,
    max_results: int = 50
) -> List[JobOffer]:
    """
    Scrape les offres d'emploi depuis RemoteOK API.

    Args:
        keywords: Mots-clés de recherche
        location: Localisation (ignoré car RemoteOK = remote only)
        contract_type: Type de contrat
        max_results: Nombre maximum de résultats

    Returns:
        Liste des offres d'emploi
    """
    jobs = []
    keywords_lower = keywords.lower()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(REMOTEOK_API_URL, headers=HEADERS)
            response.raise_for_status()

            data = response.json()

            # Le premier élément est un message légal, on le skip
            if isinstance(data, list) and len(data) > 0:
                job_listings = data[1:] if isinstance(data[0], dict) and "legal" in str(data[0]).lower() else data
            else:
                job_listings = data if isinstance(data, list) else []

            for job_data in job_listings:
                if not isinstance(job_data, dict):
                    continue

                # Filtrer par mots-clés
                title = job_data.get("position", "")
                company = job_data.get("company", "")
                description = job_data.get("description", "")
                tags = job_data.get("tags", [])

                # Vérifier si les mots-clés correspondent
                search_text = f"{title} {company} {description} {' '.join(tags)}".lower()
                if keywords_lower not in search_text:
                    # Vérifier chaque mot-clé individuellement
                    keywords_list = keywords_lower.split()
                    if not any(kw in search_text for kw in keywords_list):
                        continue

                # Extraire le salaire
                salary = None
                salary_min = job_data.get("salary_min")
                salary_max = job_data.get("salary_max")
                if salary_min and salary_max:
                    salary = f"${salary_min:,}-${salary_max:,}"
                elif salary_min:
                    salary = f"${salary_min:,}+"
                elif salary_max:
                    salary = f"Up to ${salary_max:,}"

                # Extraire la date de publication
                posted_at = None
                if job_data.get("date"):
                    posted_at = job_data.get("date")

                # Construire l'URL
                slug = job_data.get("slug", "")
                url = f"https://remoteok.com/remote-jobs/{slug}" if slug else job_data.get("url", "")

                job = JobOffer(
                    id=str(uuid.uuid4()),
                    title=title or "Unknown Position",
                    company=company or "Unknown Company",
                    location="Remote",
                    salary=salary,
                    contract_type=contract_type or "Full-time",
                    experience_level=None,
                    description=description[:500] if description else None,
                    url=url,
                    source="remoteok",
                    posted_at=posted_at,
                    scraped_at=datetime.utcnow().isoformat() + "Z",
                    tags=tags[:10] if tags else None
                )

                jobs.append(job)

                if len(jobs) >= max_results:
                    break

            # Délai anti-ban
            await asyncio.sleep(1)

    except httpx.HTTPStatusError as e:
        raise Exception(f"RemoteOK API error: {e.response.status_code}")
    except httpx.RequestError as e:
        raise Exception(f"RemoteOK connection error: {str(e)}")
    except Exception as e:
        raise Exception(f"RemoteOK scraping error: {str(e)}")

    return jobs
