'use client';

import { useState } from 'react';
import { searchCorpus, SearchResult } from '../api';

export default function Search() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [useSoundex, setUseSoundex] = useState(false);
    const [useSpellCorrection, setUseSpellCorrection] = useState(false);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        setError(null);

        try {
            const searchResults = await searchCorpus(query, 5, {
                useSoundex,
                useSpellCorrection
            });
            setResults(searchResults);
        } catch (err) {
            setError('Failed to perform search. Please try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <form onSubmit={handleSearch} className="mb-6">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search the corpus..."
                        className="flex-1 h-12 rounded-xl border border-white/15 bg-white/5 px-4 outline-none transition focus:border-blue-500/60 focus:bg-white/10"
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className="h-12 px-5 rounded-xl bg-blue-600 text-white font-medium shadow-sm hover:bg-blue-500 disabled:bg-gray-400/60 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Searching...' : 'Search'}
                    </button>
                </div>
                <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-foreground/80">
                    <label className="inline-flex items-center gap-2 cursor-pointer select-none">
                        <input
                            type="checkbox"
                            checked={useSoundex}
                            onChange={(e) => setUseSoundex(e.target.checked)}
                            className="h-4 w-4 accent-blue-600"
                        />
                        <span>Use Soundex</span>
                    </label>
                    <label className="inline-flex items-center gap-2 cursor-pointer select-none">
                        <input
                            type="checkbox"
                            checked={useSpellCorrection}
                            onChange={(e) => setUseSpellCorrection(e.target.checked)}
                            className="h-4 w-4 accent-blue-600"
                        />
                        <span>Use Spell Correction</span>
                    </label>
                </div>
            </form>

            {error && (
                <div className="text-red-500 mb-4">
                    {error}
                </div>
            )}

            {results.length > 0 && (
                <div className="mt-6 space-y-4">
                    {results.map((result, index) => (
                        <div key={index} className="rounded-xl border border-white/10 bg-white/5 p-4">
                            <div className="flex items-center justify-between">
                                <h3 className="text-base md:text-lg font-semibold">
                                    {result.document}
                                </h3>
                                <span className="text-xs md:text-sm text-foreground/60">{result.score.toFixed(4)}</span>
                            </div>
                            <p className="mt-2 text-sm md:text-base text-foreground/80">
                                {result.snippet}
                            </p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}