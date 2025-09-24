const API_BASE_URL = 'http://localhost:8000/api';

export async function getCorpusFiles() {
    const response = await fetch(`${API_BASE_URL}/corpus`);
    if (!response.ok) {
        throw new Error('Failed to fetch corpus files');
    }
    const data = await response.json();
    return data.files;
}

export async function getCorpusContent(fileName: string) {
    const response = await fetch(`${API_BASE_URL}/corpus/${fileName}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch content for ${fileName}`);
    }
    const data = await response.json();
    return data.content;
}

export interface SearchResult {
    document: string;
    score: number;
    snippet: string;
}

export async function searchCorpus(query: string, topK: number = 5): Promise<SearchResult[]> {
    const params = new URLSearchParams({
        query: query,
        top_k: topK.toString()
    });
    
    const response = await fetch(`${API_BASE_URL}/search?${params.toString()}`, {
        method: 'POST'
    });
    
    if (!response.ok) {
        throw new Error('Failed to perform search');
    }
    
    const data = await response.json();
    return data.results;
}