import { useState, useCallback, useEffect } from 'react';
import type { SearchRequest, SearchResponse, AppState, JobOffer } from './types';
import { searchJobs, exportResults, downloadBlob } from './services/api';
import SearchForm from './components/SearchForm';
import JobCard from './components/JobCard';
import Pagination from './components/Pagination';
import SkeletonCard from './components/SkeletonCard';
import JobModal from './components/JobModal';

// Historique des recherches
interface SearchHistory {
  keywords: string;
  timestamp: number;
}

function App() {
  const [appState, setAppState] = useState<AppState>('initial');
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastRequest, setLastRequest] = useState<SearchRequest | null>(null);
  const [exportLoading, setExportLoading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobOffer | null>(null);
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('darkMode') === 'true' ||
        window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  });
  const [searchHistory, setSearchHistory] = useState<SearchHistory[]>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('searchHistory');
      return saved ? JSON.parse(saved) : [];
    }
    return [];
  });

  // Dark mode effect
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('darkMode', String(darkMode));
  }, [darkMode]);

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(null), 3000);
  };

  const addToHistory = (keywords: string) => {
    const newEntry: SearchHistory = { keywords, timestamp: Date.now() };
    const filtered = searchHistory.filter(h => h.keywords.toLowerCase() !== keywords.toLowerCase());
    const updated = [newEntry, ...filtered].slice(0, 10); // Garder les 10 dernieres
    setSearchHistory(updated);
    localStorage.setItem('searchHistory', JSON.stringify(updated));
  };

  const handleSearch = useCallback(async (request: SearchRequest) => {
    setAppState('loading');
    setError(null);
    setLastRequest(request);
    addToHistory(request.keywords);

    try {
      const response = await searchJobs(request);
      setSearchResponse(response);

      if (response.totalResults === 0) {
        setAppState('empty');
      } else {
        setAppState('results');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue');
      setAppState('error');
    }
  }, [searchHistory]);

  const handlePageChange = useCallback((page: number) => {
    if (!lastRequest) return;
    handleSearch({ ...lastRequest, page });
  }, [lastRequest, handleSearch]);

  const handleExport = async (format: 'csv' | 'json') => {
    if (!searchResponse || searchResponse.totalResults === 0) return;

    setExportLoading(true);
    try {
      const blob = await exportResults(format);
      const filename = `job_offers_${new Date().toISOString().split('T')[0]}.${format}`;
      downloadBlob(blob, filename);
      showToast(`Export ${format.toUpperCase()} telecharge !`);
    } catch (err) {
      showToast('Erreur lors de l\'export');
    } finally {
      setExportLoading(false);
    }
  };

  const handleCopyLink = (url: string) => {
    navigator.clipboard.writeText(url);
    showToast('Lien copie dans le presse-papiers !');
  };

  const handleJobClick = (job: JobOffer) => {
    setSelectedJob(job);
  };

  const clearHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem('searchHistory');
    showToast('Historique efface !');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">JobScraper</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-500 dark:text-gray-400 hidden sm:block">
                Trouvez votre prochain emploi
              </span>
              {/* Dark Mode Toggle */}
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                title={darkMode ? 'Mode clair' : 'Mode sombre'}
              >
                {darkMode ? (
                  <svg className="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                  </svg>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Form */}
        <SearchForm onSearch={handleSearch} isLoading={appState === 'loading'} />

        {/* Search History */}
        {searchHistory.length > 0 && appState === 'initial' && (
          <div className="mt-4 bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Recherches recentes</h3>
              <button
                onClick={clearHistory}
                className="text-xs text-gray-500 hover:text-red-500 dark:text-gray-400"
              >
                Effacer
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {searchHistory.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSearch({ keywords: item.keywords, page: 1, limit: 20 })}
                  className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm hover:bg-blue-100 dark:hover:bg-blue-900 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
                >
                  {item.keywords}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Results Section */}
        <div className="mt-8">
          {/* Initial State */}
          {appState === 'initial' && (
            <div className="text-center py-16">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full mb-4">
                <svg className="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Bienvenue sur JobScraper
              </h2>
              <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
                Recherchez des offres d'emploi depuis plusieurs sources en un seul clic.
                Entrez vos mots-cles et lancez la recherche.
              </p>
            </div>
          )}

          {/* Loading State */}
          {appState === 'loading' && (
            <div className="space-y-4">
              <div className="flex items-center justify-center gap-3 py-4">
                <svg className="animate-spin h-6 w-6 text-blue-600" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span className="text-gray-600 dark:text-gray-400 font-medium">Scraping en cours...</span>
              </div>
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <SkeletonCard key={i} />
                ))}
              </div>
            </div>
          )}

          {/* Results State */}
          {appState === 'results' && searchResponse && (
            <>
              {/* Results Header */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {searchResponse.totalResults} resultats trouves
                  </h2>
                  {searchResponse.errors && searchResponse.errors.length > 0 && (
                    <p className="text-sm text-yellow-600 dark:text-yellow-400 mt-1">
                      Attention: {searchResponse.errors.join(', ')}
                    </p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleExport('csv')}
                    disabled={exportLoading}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors text-sm"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Export CSV
                  </button>
                  <button
                    onClick={() => handleExport('json')}
                    disabled={exportLoading}
                    className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-lg transition-colors text-sm"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Export JSON
                  </button>
                </div>
              </div>

              {/* Job Cards */}
              <div className="space-y-4">
                {searchResponse.results.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    onCopyLink={handleCopyLink}
                    onClick={() => handleJobClick(job)}
                  />
                ))}
              </div>

              {/* Pagination */}
              <Pagination
                currentPage={searchResponse.page}
                totalPages={searchResponse.totalPages}
                hasNext={searchResponse.hasNext}
                hasPrevious={searchResponse.hasPrevious}
                onPageChange={handlePageChange}
              />
            </>
          )}

          {/* Empty State */}
          {appState === 'empty' && (
            <div className="text-center py-16">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Aucune offre trouvee
              </h2>
              <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto mb-4">
                Essayez d'elargir vos criteres de recherche ou de changer les sources.
              </p>
              <div className="text-sm text-gray-400">
                Suggestions: "developer", "react", "python", "data"
              </div>
            </div>
          )}

          {/* Error State */}
          {appState === 'error' && (
            <div className="text-center py-16">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 dark:bg-red-900 rounded-full mb-4">
                <svg className="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Une erreur est survenue
              </h2>
              <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto mb-4">
                {error || 'Impossible de recuperer les offres d\'emploi.'}
              </p>
              <button
                onClick={() => lastRequest && handleSearch(lastRequest)}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Reessayer
              </button>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              JobScraper - Projet Portfolio
            </p>
            <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
              <span>Sources: RemoteOK, Jobicy, Welcome to the Jungle</span>
            </div>
          </div>
        </div>
      </footer>

      {/* Toast Notification */}
      {toast && (
        <div className="fixed bottom-4 right-4 px-4 py-3 bg-gray-900 dark:bg-gray-700 text-white rounded-lg shadow-lg animate-pulse z-40">
          {toast}
        </div>
      )}

      {/* Job Modal */}
      {selectedJob && (
        <JobModal
          job={selectedJob}
          onClose={() => setSelectedJob(null)}
          onCopyLink={handleCopyLink}
        />
      )}
    </div>
  );
}

export default App;
