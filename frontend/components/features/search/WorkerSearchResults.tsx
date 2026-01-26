'use client';

import { useState } from 'react';
import { Worker } from '@/lib/types';
import { Button } from '@/components/ui/Button';
import Image from 'next/image';

interface WorkerSearchResultsProps {
  workers: Worker[];
  loading: boolean;
  searchHistory?: string[];
  onSearchHistoryClick?: (query: string) => void;
}

interface SortOption {
  value: string;
  label: string;
}

export default function WorkerSearchResults({ workers, loading, searchHistory = [], onSearchHistoryClick }: WorkerSearchResultsProps) {
  const [sortOption, setSortOption] = useState('relevance');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10); // This would typically come from the API response

  // Sort options
  const sortOptions: SortOption[] = [
    { value: 'relevance', label: 'Relevance' },
    { value: 'experience', label: 'Experience' },
    { value: 'rating', label: 'Rating' },
    { value: 'date_registered', label: 'Newest First' },
    { value: 'age', label: 'Age' },
    { value: 'name', label: 'Name' },
  ];

  // Handle sort change
  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSortOption(e.target.value);
    // In a real implementation, this would trigger a new API call
  };

  // Calculate pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = workers.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(workers.length / itemsPerPage);

  // Handle page change
  const handlePageChange = (pageNumber: number) => {
    setCurrentPage(pageNumber);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <div className="text-muted-foreground">
          Showing <span className="font-semibold">{currentItems.length}</span> of <span className="font-semibold">{workers.length}</span> workers
        </div>
        <div className="flex items-center space-x-2">
          <span>Sort by:</span>
          <select
            value={sortOption}
            onChange={handleSortChange}
            className="p-2 border border-border rounded"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {currentItems.length === 0 ? (
        <div className="space-y-8">
          <div className="text-center py-12">
            <h3 className="text-xl font-medium text-foreground mb-2">No workers found</h3>
            <p className="text-muted-foreground">Try adjusting your search filters</p>
          </div>

          {/* Show search history if available */}
          {searchHistory.length > 0 && (
            <div className="bg-card p-4 rounded-lg shadow">
              <h3 className="font-medium mb-3">Recent Searches</h3>
              <div className="flex flex-wrap gap-2">
                {searchHistory.map((query, index) => (
                  <button
                    key={index}
                    onClick={() => onSearchHistoryClick?.(query)}
                    className="bg-muted hover:bg-muted-foreground/10 text-primary text-sm px-3 py-1 rounded-full"
                  >
                    {query || 'All workers'}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div>
          {/* Show search history if available */}
          {searchHistory.length > 0 && (
            <div className="bg-card p-4 rounded-lg shadow mb-6">
              <h3 className="font-medium mb-3">Recent Searches</h3>
              <div className="flex flex-wrap gap-2">
                {searchHistory.map((query, index) => (
                  <button
                    key={index}
                    onClick={() => onSearchHistoryClick?.(query)}
                    className="bg-muted hover:bg-muted-foreground/10 text-primary text-sm px-3 py-1 rounded-full"
                  >
                    {query || 'All workers'}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {currentItems.map((worker) => (
              <div key={worker.id} className="bg-card rounded-lg shadow-md overflow-hidden border border-border">
                <div className="p-4">
                  <div className="flex items-center mb-4">
                    {worker.profile_photo_url ? (
                      <Image
                        src={worker.profile_photo_url}
                        alt={worker.full_name}
                        width={64}
                        height={64}
                        className="w-16 h-16 rounded-full object-cover mr-4"
                        priority={false}
                      />
                    ) : (
                      <div className="bg-muted border-2 border-dashed rounded-xl w-16 h-16 mr-4" />
                    )}
                    <div>
                      <h3 className="text-lg font-semibold">{worker.full_name}</h3>
                      <div className="flex items-center">
                        <span className="text-warning mr-1">★</span>
                        <span>{worker.rating.toFixed(1)}</span>
                        <span className="mx-2">•</span>
                        <span>{worker.years_experience} years exp</span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-sm text-muted-foreground">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {worker.current_location}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      <span className="font-medium">Region:</span> {worker.region_of_origin}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      <span className="font-medium">Age:</span> {worker.age}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      <span className="font-medium">Education:</span> {worker.education_level}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      <span className="font-medium">Religion:</span> {worker.religion.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </div>
                  </div>

                  <div className="mb-4">
                    <h4 className="font-medium mb-1">Skills:</h4>
                    <div className="flex flex-wrap gap-1">
                      {worker.skills.slice(0, 3).map((skill, index) => (
                        <span key={index} className="bg-info/10 text-info text-xs px-2 py-1 rounded">
                          {skill}
                        </span>
                      ))}
                      {worker.skills.length > 3 && (
                        <span className="bg-muted text-muted-foreground text-xs px-2 py-1 rounded">
                          +{worker.skills.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="mb-4">
                    <h4 className="font-medium mb-1">Languages:</h4>
                    <div className="flex flex-wrap gap-1">
                      {worker.languages.slice(0, 3).map((language, index) => (
                        <span key={index} className="bg-success/10 text-success text-xs px-2 py-1 rounded">
                          {typeof language === 'string' ? language : language.language}
                        </span>
                      ))}
                      {worker.languages.length > 3 && (
                        <span className="bg-muted text-muted-foreground text-xs px-2 py-1 rounded">
                          +{worker.languages.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <Button className="flex-1">View Profile</Button>
                    <Button variant="outline" className="flex-1">Contact</Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-8 flex justify-center">
          <nav className="inline-flex rounded-md shadow">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className={`px-3 py-2 rounded-l-md border ${
                currentPage === 1
                  ? 'bg-muted text-muted-foreground cursor-not-allowed'
                  : 'bg-background text-muted-foreground hover:bg-muted'
              }`}
            >
              Previous
            </button>

            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => handlePageChange(page)}
                className={`px-3 py-2 border-t border-b ${
                  currentPage === page
                    ? 'bg-primary/10 text-primary'
                    : 'bg-background text-muted-foreground hover:bg-muted'
                }`}
              >
                {page}
              </button>
            ))}

            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className={`px-3 py-2 rounded-r-md border ${
                currentPage === totalPages
                  ? 'bg-muted text-muted-foreground cursor-not-allowed'
                  : 'bg-background text-muted-foreground hover:bg-muted'
              }`}
            >
              Next
            </button>
          </nav>
        </div>
      )}
    </div>
  );
}