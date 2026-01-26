'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/Button';
import SearchSuggestions from '@/components/features/search/SearchSuggestions';

interface WorkerSearchFiltersProps {
  onFilterChange: (filters: Record<string, string | string[]>) => void;
  currentFilters: Record<string, string | string[]>;
}

interface FilterOptions {
  regions: string[];
  skills: string[];
  languages: string[];
  education_levels: string[];
  religions: string[];
  working_times: string[];
  experience_range: { min: number; max: number };
  age_range: { min: number; max: number };
  rating_range: { min: number; max: number };
}

export default function WorkerSearchFilters({ onFilterChange, currentFilters }: WorkerSearchFiltersProps) {
  const [filters, setFilters] = useState<Record<string, string | string[]>>({});
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeInput, setActiveInput] = useState<string | null>(null);
  const [suggestionQuery, setSuggestionQuery] = useState('');

  // Fetch available filter options
  useEffect(() => {
    const fetchFilterOptions = async () => {
      try {
        const response = await fetch('/api/workers/filters/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch filter options');
        }

        const data = await response.json();
        setFilterOptions(data);
      } catch (err) {
        setError('Failed to load filter options');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchFilterOptions();
  }, []);

  // Initialize filters with current filters
  useEffect(() => {
    setFilters(currentFilters);
  }, [currentFilters]);

  // Handle filter changes
  const handleFilterChange = (name: string, value: string | string[]) => {
    const newFilters = { ...filters, [name]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  // Handle multi-select changes
  const handleMultiSelectChange = (name: string, value: string, checked: boolean) => {
    const currentValues = Array.isArray(filters[name]) ? filters[name] as string[] : [];
    let newValues: string[];

    if (checked) {
      newValues = [...currentValues, value];
    } else {
      newValues = currentValues.filter(v => v !== value);
    }

    handleFilterChange(name, newValues);
  };

  // Handle input focus for suggestions
  const handleInputFocus = (inputName: string) => {
    setActiveInput(inputName);
  };

  // Handle input blur to hide suggestions
  const handleInputBlur = () => {
    setTimeout(() => setActiveInput(null), 200); // Delay to allow click on suggestions
  };

  // Handle input change for suggestions
  const handleInputChange = (name: string, value: string) => {
    handleFilterChange(name, value);
    if (activeInput === name) {
      setSuggestionQuery(value);
    }
  };

  // Handle suggestion selection
  const handleSuggestionSelect = (suggestion: string) => {
    if (activeInput) {
      handleFilterChange(activeInput, suggestion);
      setSuggestionQuery('');
    }
  };

  // Reset all filters
  const resetFilters = () => {
    setFilters({});
    onFilterChange({});
  };

  if (loading) {
    return <div className="p-4">Loading filters...</div>;
  }

  if (error) {
    return <div className="p-4 text-error">{error}</div>;
  }

  if (!filterOptions) {
    return <div className="p-4">No filter options available</div>;
  }

  return (
    <div className="bg-card p-4 rounded-lg shadow">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-card-foreground">Filters</h2>
        <Button variant="outline" onClick={resetFilters}>
          Reset
        </Button>
      </div>

      <div className="space-y-6">
        {/* Location Filters */}
        <div className="relative">
          <h3 className="font-medium mb-2 text-foreground">Location</h3>
          <div className="space-y-2">
            <div className="relative">
              <input
                type="text"
                placeholder="Region of Origin"
                value={filters.region_of_origin || ''}
                onChange={(e) => handleInputChange('region_of_origin', e.target.value)}
                onFocus={() => handleInputFocus('region_of_origin')}
                onBlur={handleInputBlur}
                className="w-full p-2 border border-input rounded"
              />
              {activeInput === 'region_of_origin' && (
                <SearchSuggestions
                  query={suggestionQuery}
                  onSelect={handleSuggestionSelect}
                  className="mt-0"
                />
              )}
            </div>

            <div className="relative">
              <input
                type="text"
                placeholder="Current Location"
                value={filters.current_location || ''}
                onChange={(e) => handleInputChange('current_location', e.target.value)}
                onFocus={() => handleInputFocus('current_location')}
                onBlur={handleInputBlur}
                className="w-full p-2 border border-input rounded"
              />
              {activeInput === 'current_location' && (
                <SearchSuggestions
                  query={suggestionQuery}
                  onSelect={handleSuggestionSelect}
                  className="mt-0"
                />
              )}
            </div>
          </div>
        </div>

        {/* Skills Filter */}
        <div>
          <h3 className="font-medium mb-2 text-foreground">Skills</h3>
          <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto">
            {filterOptions.skills.map((skill) => (
              <label key={skill} className="flex items-center">
                <input
                  type="checkbox"
                  checked={Array.isArray(filters.skills) && filters.skills.includes(skill)}
                  onChange={(e) => handleMultiSelectChange('skills', skill, e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm">{skill}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Languages Filter */}
        <div>
          <h3 className="font-medium mb-2 text-foreground">Languages</h3>
          <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto">
            {filterOptions.languages.map((language) => (
              <label key={language} className="flex items-center">
                <input
                  type="checkbox"
                  checked={Array.isArray(filters.languages) && filters.languages.includes(language)}
                  onChange={(e) => handleMultiSelectChange('languages', language, e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm">{language}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Education Level */}
        <div>
          <h3 className="font-medium mb-2 text-foreground">Education Level</h3>
          <select
            value={filters.education_level || ''}
            onChange={(e) => handleFilterChange('education_level', e.target.value)}
            className="w-full p-2 border border-input rounded"
          >
            <option value="">All Levels</option>
            {filterOptions.education_levels.map((level) => (
              <option key={level} value={level}>
                {level.charAt(0).toUpperCase() + level.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Religion */}
        <div>
          <h3 className="font-medium mb-2 text-foreground">Religion</h3>
          <select
            value={filters.religion || ''}
            onChange={(e) => handleFilterChange('religion', e.target.value)}
            className="w-full p-2 border border-input rounded"
          >
            <option value="">All Religions</option>
            {filterOptions.religions.map((religion) => (
              <option key={religion} value={religion}>
                {religion.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </option>
            ))}
          </select>
        </div>

        {/* Working Time */}
        <div>
          <h3 className="font-medium mb-2 text-foreground">Working Time</h3>
          <select
            value={filters.working_time || ''}
            onChange={(e) => handleFilterChange('working_time', e.target.value)}
            className="w-full p-2 border border-input rounded"
          >
            <option value="">Any</option>
            {filterOptions.working_times.map((time) => (
              <option key={time} value={time}>
                {time.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </option>
            ))}
          </select>
        </div>

        {/* Experience Range */}
        <div>
          <h3 className="font-medium mb-2 text-foreground">Years of Experience</h3>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="number"
              placeholder="Min"
              min={filterOptions.experience_range.min}
              max={filterOptions.experience_range.max}
              value={filters.experience_min || ''}
              onChange={(e) => handleFilterChange('experience_min', e.target.value)}
              className="p-2 border border-input rounded"
            />
            <input
              type="number"
              placeholder="Max"
              min={filterOptions.experience_range.min}
              max={filterOptions.experience_range.max}
              value={filters.experience_max || ''}
              onChange={(e) => handleFilterChange('experience_max', e.target.value)}
              className="p-2 border border-input rounded"
            />
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            Range: {filterOptions.experience_range.min} - {filterOptions.experience_range.max} years
          </div>
        </div>

        {/* Age Range */}
        <div>
          <h3 className="font-medium mb-2 text-foreground">Age</h3>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="number"
              placeholder="Min"
              min={filterOptions.age_range.min}
              max={filterOptions.age_range.max}
              value={filters.age_min || ''}
              onChange={(e) => handleFilterChange('age_min', e.target.value)}
              className="p-2 border border-input rounded"
            />
            <input
              type="number"
              placeholder="Max"
              min={filterOptions.age_range.min}
              max={filterOptions.age_range.max}
              value={filters.age_max || ''}
              onChange={(e) => handleFilterChange('age_max', e.target.value)}
              className="p-2 border border-input rounded"
            />
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            Range: {filterOptions.age_range.min} - {filterOptions.age_range.max} years
          </div>
        </div>

        {/* Rating */}
        <div>
          <h3 className="font-medium mb-2 text-foreground">Minimum Rating</h3>
          <input
            type="number"
            min={filterOptions.rating_range.min}
            max={filterOptions.rating_range.max}
            step="0.1"
            placeholder={`Min: ${filterOptions.rating_range.min}`}
            value={filters.min_rating || ''}
            onChange={(e) => handleFilterChange('min_rating', e.target.value)}
            className="w-full p-2 border border-input rounded"
          />
          <div className="text-xs text-muted-foreground mt-1">
            Range: {filterOptions.rating_range.min} - {filterOptions.rating_range.max}
          </div>
        </div>

        {/* Verification Status */}
        <div>
          <h3 className="font-medium mb-2 text-foreground">Verification</h3>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={filters.is_verified === 'true'}
              onChange={(e) => handleFilterChange('is_verified', e.target.checked ? 'true' : '')}
              className="mr-2"
            />
            <span>Verified Only</span>
          </label>
        </div>
      </div>
    </div>
  );
}