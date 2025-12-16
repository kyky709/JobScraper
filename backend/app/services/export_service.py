import csv
import json
import io
from typing import List
from app.models import JobOffer


def export_to_csv(jobs: List[JobOffer]) -> str:
    """
    Exporte les offres d'emploi au format CSV.

    Args:
        jobs: Liste des offres d'emploi

    Returns:
        Contenu CSV en string
    """
    output = io.StringIO()

    fieldnames = [
        "id", "title", "company", "location", "salary",
        "contract_type", "experience_level", "description",
        "url", "source", "posted_at", "scraped_at", "tags"
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()

    for job in jobs:
        job_dict = job.model_dump(by_alias=False)
        # Convertir les tags en string
        if job_dict.get("tags"):
            job_dict["tags"] = ", ".join(job_dict["tags"])
        writer.writerow(job_dict)

    return output.getvalue()


def export_to_json(jobs: List[JobOffer]) -> str:
    """
    Exporte les offres d'emploi au format JSON.

    Args:
        jobs: Liste des offres d'emploi

    Returns:
        Contenu JSON en string
    """
    jobs_data = [job.model_dump(by_alias=True) for job in jobs]
    return json.dumps(jobs_data, indent=2, ensure_ascii=False)
