import asyncio
from typing import List, Optional
from datetime import datetime
from urllib.parse import quote_plus
import uuid
import re
import subprocess
import json
import sys
import tempfile
import os

from app.models import JobOffer


# Script de scraping à exécuter dans un processus séparé
SCRAPER_SCRIPT = '''
import sys
import json
from playwright.sync_api import sync_playwright
import re

def scrape(url, max_results):
    jobs = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()

            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_selector('a[href*="/jobs/"]', timeout=10000)

                for _ in range(3):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(500)

                links = page.query_selector_all('a[href*="/companies/"][href*="/jobs/"]')

                seen = set()
                for link in links:
                    if len(jobs) >= max_results:
                        break

                    href = link.get_attribute('href') or ""
                    if not href or href in seen or "/companies/" not in href or "/jobs/" not in href:
                        continue

                    seen.add(href)

                    title_match = re.search(r'/jobs/([^/?]+)', href)
                    title = title_match.group(1).replace("-", " ").title() if title_match else "Offre"

                    company_match = re.search(r'/companies/([^/]+)', href)
                    company = company_match.group(1).replace("-", " ").title() if company_match else "Entreprise"

                    full_url = f"https://www.welcometothejungle.com{href}" if href.startswith("/") else href

                    jobs.append({
                        "title": title[:200],
                        "company": company[:100],
                        "url": full_url
                    })

            except Exception:
                pass
            finally:
                browser.close()

    except Exception:
        pass

    return jobs

if __name__ == "__main__":
    url = sys.argv[1]
    max_results = int(sys.argv[2])
    result = scrape(url, max_results)
    print(json.dumps(result))
'''


async def scrape_welcometothejungle(
    keywords: str,
    location: Optional[str] = None,
    contract_type: Optional[str] = None,
    remote: bool = False,
    max_results: int = 50
) -> List[JobOffer]:
    """
    Scrape les offres d'emploi depuis Welcome to the Jungle avec Playwright.

    Args:
        keywords: Mots-clés de recherche
        location: Localisation
        contract_type: Type de contrat
        remote: Uniquement les offres remote
        max_results: Nombre maximum de résultats

    Returns:
        Liste des offres d'emploi
    """
    # Construire l'URL de recherche
    params = [f"query={quote_plus(keywords)}"]
    if location:
        params.append(f"aroundQuery={quote_plus(location)}")
    if remote:
        params.append("remote=true")

    url = f"https://www.welcometothejungle.com/fr/jobs?{'&'.join(params)}"

    jobs = []

    try:
        # Créer un fichier temporaire avec le script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(SCRAPER_SCRIPT)
            script_path = f.name

        try:
            # Exécuter le script dans un processus séparé
            result = subprocess.run(
                [sys.executable, script_path, url, str(max_results)],
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8'
            )

            if result.returncode == 0 and result.stdout.strip():
                raw_jobs = json.loads(result.stdout.strip())

                for raw_job in raw_jobs:
                    job = JobOffer(
                        id=str(uuid.uuid4()),
                        title=raw_job.get("title", "Offre d'emploi"),
                        company=raw_job.get("company", "Entreprise"),
                        location=location or "France",
                        salary=None,
                        contract_type=contract_type,
                        experience_level=None,
                        description=None,
                        url=raw_job.get("url", ""),
                        source="welcometothejungle",
                        posted_at=None,
                        scraped_at=datetime.utcnow().isoformat() + "Z",
                        tags=None
                    )
                    jobs.append(job)

        finally:
            # Supprimer le fichier temporaire
            try:
                os.unlink(script_path)
            except Exception:
                pass

    except subprocess.TimeoutExpired:
        raise Exception("Welcome to the Jungle scraping timeout")
    except json.JSONDecodeError:
        raise Exception("Welcome to the Jungle invalid response")
    except Exception as e:
        raise Exception(f"Welcome to the Jungle scraping error: {str(e)}")

    return jobs
