'use client';

import { useState } from 'react';

export default function SemanticSearch({ onSearch }: { onSearch: (query: string, target?: string, mutation?: string) => void }) {
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setSearching(true);
    setError(null);
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || data.details || 'Search failed');
      }

      // Common mutations to detect
      const COMMON_MUTATIONS = [
        'NRAS', 'KRAS', 'BRAF', 'TP53', 'PIK3CA', 'PTEN', 'EGFR', 
        'APC', 'SMAD4', 'CDKN2A', 'RB1', 'NF1', 'ARID1A', 'CTNNB1',
        'IDH1', 'IDH2', 'FLT3', 'NPM1', 'DNMT3A', 'TET2', 'ASXL1'
      ];
      
      // Extract mutation name from query
      const mutationMatch = query.match(new RegExp(`\\b(${COMMON_MUTATIONS.join('|')})\\b`, 'i'));
      const mutation = mutationMatch ? mutationMatch[1].toUpperCase() : null;
      
      // Extract target name from query if it's a dependency question
      const targetMatch = query.match(/(STK17A|STK17B|MYLK4|TBK1|CLK4)/i);
      const target = targetMatch ? targetMatch[1].toUpperCase() : null;
      
      // Check if query is asking about dependency
      const isDependencyQuery = /dependent|dependency|depend|high|low/i.test(query);
      
      if (mutation && target && isDependencyQuery) {
        // Complex query: mutation + target dependency (e.g., "NRAS mutations and high TBK1 dependency")
        onSearch('', target, mutation);
      } else if (mutation && isDependencyQuery) {
        // Mutation + dependency query without specific target
        onSearch('', null, mutation);
      } else if (target && isDependencyQuery) {
        // Target dependency query
        onSearch('', target);
      } else if (mutation) {
        // Just mutation query
        onSearch('', null, mutation);
      } else if (target) {
        // Just target query
        onSearch(target);
      } else {
        // Other queries, just use the query text
        onSearch(query);
      }
    } catch (err: any) {
      const errorMessage = err?.message || 'Failed to process your question. Please try rephrasing.';
      setError(errorMessage);
      console.error('Search error:', err);
    } finally {
      setSearching(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSearch} className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setError(null);
          }}
          placeholder="Ask a natural language question... (e.g., 'Show me cancers with NRAS mutations and high TBK1 dependency')"
          className="w-full px-4 py-3 pl-12 pr-24 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm text-gray-900 font-medium placeholder:text-gray-600"
        />
        <svg className="absolute left-4 top-3.5 h-5 w-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <button
          type="submit"
          disabled={searching || !query.trim()}
          className="absolute right-2 top-2 px-4 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm font-semibold"
        >
          {searching ? 'Searching...' : 'Search'}
        </button>
      </form>
      {error && (
        <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm font-medium text-red-800">{error}</p>
        </div>
      )}
    </div>
  );
}

