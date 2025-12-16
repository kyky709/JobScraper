import type { SearchRequest, SearchResponse } from '../types';

const API_BASE = '/api';

export async function searchJobs(request: SearchRequest): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Erreur API: ${response.status}`);
  }

  return response.json();
}

export async function exportResults(format: 'csv' | 'json'): Promise<Blob> {
  const response = await fetch(`${API_BASE}/export?format=${format}`);

  if (!response.ok) {
    throw new Error(`Erreur export: ${response.status}`);
  }

  return response.blob();
}

export async function healthCheck(): Promise<{ status: string; timestamp: string }> {
  const response = await fetch(`${API_BASE}/health`);

  if (!response.ok) {
    throw new Error('API non disponible');
  }

  return response.json();
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
