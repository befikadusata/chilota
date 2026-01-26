'use client';

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/lib/auth/auth-context';

interface SearchSuggestion {
  id: string;
  text: string;
  type: 'location' | 'skill' | 'language' | 'other';
}

interface SearchSuggestionsProps {
  query: string;
  onSelect: (suggestion: string) => void;
  className?: string;
}

export default function SearchSuggestions({ query, onSelect, className = '' }: SearchSuggestionsProps) {
  const { user } = useAuth();
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Fetch suggestions based on query
  useEffect(() => {
    if (!query.trim() || !user) return;

    const fetchSuggestions = async () => {
      setLoading(true);
      
      try {
        // In a real implementation, we would call an API endpoint for suggestions
        // For now, we'll simulate with mock data based on the query
        const mockSuggestions: SearchSuggestion[] = [];
        
        // Add location suggestions if query looks like a location
        if (query.length > 1) {
          const locations = ['Addis Ababa', 'Dire Dawa', 'Mekelle', 'Bahir Dar', 'Hawassa', 'Adama', 'Jimma'];
          const locationMatches = locations.filter(loc => 
            loc.toLowerCase().includes(query.toLowerCase())
          );
          
          locationMatches.forEach(loc => {
            mockSuggestions.push({
              id: `loc-${loc}`,
              text: loc,
              type: 'location'
            });
          });
        }
        
        // Add skill suggestions if query looks like a skill
        if (query.length > 1) {
          const skills = ['Cooking', 'Cleaning', 'Childcare', 'Elderly Care', 'Gardening', 'Driving', 'Laundry', 'Ironing'];
          const skillMatches = skills.filter(skill => 
            skill.toLowerCase().includes(query.toLowerCase())
          );
          
          skillMatches.forEach(skill => {
            mockSuggestions.push({
              id: `skill-${skill}`,
              text: skill,
              type: 'skill'
            });
          });
        }
        
        // Add language suggestions if query looks like a language
        if (query.length > 1) {
          const languages = ['Amharic', 'Oromo', 'Tigrinya', 'Afar', 'Somali', 'Gedeo', 'English'];
          const langMatches = languages.filter(lang => 
            lang.toLowerCase().includes(query.toLowerCase())
          );
          
          langMatches.forEach(lang => {
            mockSuggestions.push({
              id: `lang-${lang}`,
              text: lang,
              type: 'language'
            });
          });
        }
        
        setSuggestions(mockSuggestions.slice(0, 5)); // Limit to 5 suggestions
        setShowSuggestions(true);
      } catch (error) {
        console.error('Error fetching suggestions:', error);
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    };

    // Use a debounce to avoid too many requests
    const timeoutId = setTimeout(fetchSuggestions, 300);
    
    return () => clearTimeout(timeoutId);
  }, [query, user]);

  // Handle clicks outside the suggestions container
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle suggestion selection
  const handleSelect = (suggestion: string) => {
    onSelect(suggestion);
    setShowSuggestions(false);
  };

  if (!showSuggestions || suggestions.length === 0) {
    return null;
  }

  return (
    <div 
      ref={containerRef}
      className={`absolute z-10 mt-1 w-full bg-popover shadow-lg rounded-md py-1 max-h-60 overflow-auto ${className}`}
    >
      {loading ? (
        <div className="px-4 py-2 text-muted-foreground">Loading suggestions...</div>
      ) : (
        suggestions.map((suggestion) => (
          <div
            key={suggestion.id}
            className="px-4 py-2 hover:bg-muted cursor-pointer flex items-center"
            onClick={() => handleSelect(suggestion.text)}
          >
            <span className="mr-2">
              {suggestion.type === 'location' && '📍'}
              {suggestion.type === 'skill' && '🔧'}
              {suggestion.type === 'language' && '🗣️'}
              {suggestion.type === 'other' && '💡'}
            </span>
            <span>{suggestion.text}</span>
          </div>
        ))
      )}
    </div>
  );
}