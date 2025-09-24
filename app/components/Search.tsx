'use client';

import { useState } from 'react';
import { searchCorpus, SearchResult } from '../api';

export default function Search() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        setError(null);

        try {
            const searchResults = await searchCorpus(query);
            setResults(searchResults);
        } catch (err) {
            setError('Failed to perform search. Please try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-4">
            <form onSubmit={handleSearch} className="mb-8">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Enter your search query..."
                        className="flex-1 p-2 border rounded"
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
                    >
                        {loading ? 'Searching...' : 'Search'}
                    </button>
                </div>
            </form>

            {error && (
                <div className="text-red-500 mb-4">
                    {error}
                </div>
            )}

            {results.length > 0 && (
                <div className="space-y-4">
                    {results.map((result, index) => (
                        <div key={index} className="border rounded p-4">
                            <h3 className="text-lg font-semibold mb-2">
                                {result.document}
                            </h3>
                            <p className="text-sm text-gray-600 mb-2">
                                Score: {result.score.toFixed(4)}
                            </p>
                            <p className="text-gray-800">
                                {result.snippet}
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}