'use client';

import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '@/lib/auth/auth-context';
import { useRouter } from 'next/navigation';
import WorkerSearchFilters from '@/components/features/search/WorkerSearchFilters';
import WorkerSearchResults from '@/components/features/search/WorkerSearchResults';
import { workersApi } from '@/lib/api';
import { Worker } from '@/lib/types';

// Cache for search results (in a real app, you might use a more sophisticated caching solution)
const searchCache = new Map();

// Cache timeout in milliseconds (15 minutes)
const CACHE_TIMEOUT = 15 * 60 * 1000;

export default function WorkerSearchPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<Record<string, string | string[]>>({});
  const [searchHistory, setSearchHistory] = useState<string[]>([]);

  // Check if user is authenticated
  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }

    if (user.role !== 'employer') {
      router.push('/dashboard');
      return;
    }
  }, [user, router]);

  // Load search history from localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedHistory = localStorage.getItem('searchHistory');
      if (savedHistory) {
        try {
          setSearchHistory(JSON.parse(savedHistory));
        } catch (e) {
          console.error('Error parsing search history', e);
        }
      }
    }
  }, []);

  // Save search history to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
    }
  }, [searchHistory]);

  // Fetch workers based on search parameters
  const fetchWorkers = async (searchFilters: Record<string, string | string[]>) => {
    // Check if results are already cached
    const cacheKey = JSON.stringify(searchFilters);
    if (searchCache.has(cacheKey)) {
      const cachedResult = searchCache.get(cacheKey);
      const now = Date.now();

      // Check if cache is still valid
      if (now - cachedResult.timestamp < CACHE_TIMEOUT) {
        setWorkers(cachedResult.data);
        setLoading(false);
        return;
      } else {
        // Remove expired cache entry
        searchCache.delete(cacheKey);
      }
    }

    setLoading(true);
    setError(null);

    try {
      const results = await workersApi.search(searchFilters);

      // Cache the results
      searchCache.set(cacheKey, {
        data: results,
        timestamp: Date.now()
      });

      setWorkers(results);

      // Add to search history if not already present
      const searchQuery = cacheKey || 'all workers';
      if (!searchHistory.includes(searchQuery)) {
        setSearchHistory(prev => [searchQuery, ...prev.slice(0, 9)]); // Keep only last 10 searches
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while fetching workers');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Apply filters and update search parameters
  const applyFilters = (newFilters: Record<string, string | string[]>) => {
    setFilters(newFilters);
    fetchWorkers(newFilters);
  };

  // Initial fetch without filters
  useEffect(() => {
    if (user && user.role === 'employer') {
      fetchWorkers({});
    }
  }, [user]);

  // Clear cache for a specific query
  const clearCache = (key: string) => {
    searchCache.delete(key);
  };

  // Clear all cache
  const clearAllCache = () => {
    searchCache.clear();
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Search Workers</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <WorkerSearchFilters
            onFilterChange={applyFilters}
            currentFilters={filters}
          />
        </div>

        <div className="lg:col-span-3">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          ) : (
            <WorkerSearchResults
              workers={workers}
              loading={loading}
              searchHistory={searchHistory}
              onSearchHistoryClick={(query) => {
                try {
                  // Parse query string and apply as filters
                  const parsedFilters = JSON.parse(query);
                  applyFilters(parsedFilters);
                } catch (e) {
                  console.error('Error parsing search query', e);
                }
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
}