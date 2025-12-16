from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid


class JobOffer(BaseModel):
    """Modèle représentant une offre d'emploi"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    company: str
    location: str
    salary: Optional[str] = None
    contract_type: Optional[str] = Field(None, alias="contractType")
    experience_level: Optional[str] = Field(None, alias="experienceLevel")
    description: Optional[str] = None
    url: str
    source: str
    posted_at: Optional[str] = Field(None, alias="postedAt")
    scraped_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z", alias="scrapedAt")
    tags: Optional[List[str]] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


class SearchRequest(BaseModel):
    """Modèle pour une requête de recherche"""
    keywords: str
    location: Optional[str] = None
    sources: Optional[List[str]] = Field(default=["remoteok", "jobicy"])
    contract_type: Optional[str] = Field(None, alias="contractType")
    remote: Optional[bool] = False
    salary_min: Optional[int] = Field(None, alias="salaryMin")
    salary_max: Optional[int] = Field(None, alias="salaryMax")
    experience_level: Optional[str] = Field(None, alias="experienceLevel")
    sort_by: Optional[str] = Field(default="date", alias="sortBy")
    page: Optional[int] = Field(default=1, ge=1)
    limit: Optional[int] = Field(default=20, ge=1, le=1000)


class SearchResponse(BaseModel):
    """Modèle pour la réponse de recherche"""
    success: bool
    total_results: int = Field(alias="totalResults")
    results: List[JobOffer]
    scraped_at: str = Field(alias="scrapedAt")
    errors: Optional[List[str]] = None
    page: int = 1
    limit: int = 20
    total_pages: int = Field(default=1, alias="totalPages")
    has_next: bool = Field(default=False, alias="hasNext")
    has_previous: bool = Field(default=False, alias="hasPrevious")

    class Config:
        populate_by_name = True


class HealthResponse(BaseModel):
    """Modèle pour le health check"""
    status: str
    timestamp: str
