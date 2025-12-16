export interface JobOffer {
  id: string;
  title: string;
  company: string;
  location: string;
  salary?: string;
  contractType?: string;
  experienceLevel?: string;
  description?: string;
  url: string;
  source: string;
  postedAt?: string;
  scrapedAt: string;
  tags?: string[];
}

export interface SearchRequest {
  keywords: string;
  location?: string;
  sources?: string[];
  contractType?: string;
  remote?: boolean;
  salaryMin?: number;
  salaryMax?: number;
  experienceLevel?: string;
  sortBy?: 'date' | 'salary' | 'relevance';
  page?: number;
  limit?: number;
}

export interface SearchResponse {
  success: boolean;
  totalResults: number;
  results: JobOffer[];
  scrapedAt: string;
  errors?: string[];
  page: number;
  limit: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

export type AppState = 'initial' | 'loading' | 'results' | 'empty' | 'error';
