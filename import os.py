import os, math, re
from collections import defaultdict, Counter
from difflib import get_close_matches

SPELL_CORRECTION_CUTOFF = 0.75
TOP_K_RESULTS = 10

def tokenize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text.split()

def soundex(word):
    """Optimized Soundex implementation using direct character mapping"""
    if not word: return ""
    
    # Direct character to code mapping for faster lookup
    char_to_code = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6'
    }
    
    word = word.upper()
    result = word[0]  # Keep first letter
    
    # Process remaining letters
    for char in word[1:]:
        code = char_to_code.get(char, '0')
        if code != '0' and (not result or code != result[-1]):
            result += code
            
    # Remove zeros and pad with zeros
    result = result.replace('0', '')
    return (result + '000')[:4]

def precompute_soundex(dictionary):
    sx = defaultdict(list)
    for t in dictionary: sx[soundex(t)].append(t)
    return sx

def correct_token(token, dict_terms):
    if token in dict_terms: return token
    m = get_close_matches(token, dict_terms, n=1, cutoff=SPELL_CORRECTION_CUTOFF)
    return m[0] if m else token

def build_index(corpus_dir):
    """Build inverted index with proper tf-idf weights for lnc.ltc scheme"""
    if not os.path.exists(corpus_dir): 
        return {}, {}, {}, {}, 0
        
    files = [f for f in sorted(os.listdir(corpus_dir)) if os.path.isfile(os.path.join(corpus_dir,f))]
    if not files: 
        return {}, {}, {}, {}, 0
        
    dictionary = {}  # term -> [df, [(docID, tf), ...]]
    doc_lengths = {}  # docID -> normalized length
    docIDs = {}      # filename -> docID
    id_to_doc = {}   # docID -> filename
    
    # First pass: collect raw term frequencies
    raw_tf_data = {}  # term -> [(docID, raw_tf), ...]
    
    for i, fname in enumerate(files, 1):
        docIDs[fname] = i
        id_to_doc[i] = fname
        
        try:
            with open(os.path.join(corpus_dir, fname), "r", encoding="utf-8", errors="ignore") as f:
                tokens = tokenize(f.read())
        except Exception as e:
            print(f"Error reading file {fname}: {e}")
            continue
            
        if not tokens:  # Skip empty documents
            continue
            
        tf_counts = Counter(tokens)
        
        for term, raw_tf in tf_counts.items():
            if term not in raw_tf_data:
                raw_tf_data[term] = []
            raw_tf_data[term].append((i, raw_tf))
    
    # Second pass: compute tf-idf weights and build final dictionary
    for term, doc_tf_pairs in raw_tf_data.items():
        df = len(doc_tf_pairs)  # document frequency
        postings = []
        
        for docID, raw_tf in doc_tf_pairs:
            # For documents: use log tf (no idf) - lnc scheme
            log_tf = 1 + math.log10(raw_tf)
            postings.append((docID, log_tf))
            
        dictionary[term] = [df, postings]
    
    # Third pass: compute document lengths for normalization
    doc_weights_squared = defaultdict(float)
    
    for term, (df, postings) in dictionary.items():
        for docID, weight in postings:
            doc_weights_squared[docID] += weight * weight
    
    # Normalize document vectors (cosine normalization)
    for docID in doc_weights_squared:
        doc_lengths[docID] = math.sqrt(doc_weights_squared[docID])
    
    return dictionary, doc_lengths, docIDs, id_to_doc, len(files)

def build_query_vector(tokens, dictionary, N):
    """Build query vector using ltc scheme (log tf, idf, cosine normalization)"""
    if not tokens:
        return {}
        
    tf_counts = Counter(tokens)
    query_weights = {}
    
    for term, raw_tf in tf_counts.items():
        if term in dictionary:
            df = dictionary[term][0]  # document frequency
            
            # For queries: log tf * idf - ltc scheme
            log_tf = 1 + math.log10(raw_tf)
            idf = math.log10(N / df)
            tf_idf = log_tf * idf
            
            query_weights[term] = tf_idf
    
    # Cosine normalization for query vector
    if query_weights:
        norm = math.sqrt(sum(w * w for w in query_weights.values()))
        if norm > 0:
            query_weights = {term: weight / norm for term, weight in query_weights.items()}
    
    return query_weights

def process_query(query, dictionary, doc_lengths, id_to_doc, N,
                  use_soundex=False, use_spellcorrection=False, sx_map=None):
    try:
        # Tokenize and preprocess query
        tokens = tokenize(query)
        if not tokens:
            return []
            
        # Apply spell correction if enabled
        if use_spellcorrection:
            tokens = [correct_token(t, dictionary.keys()) for t in tokens]
            
        # Apply Soundex matching if enabled
        if use_soundex and sx_map:
            expanded_tokens = set(tokens)  # Use set for efficient lookups
            for token in tokens:
                sx_code = soundex(token)
                expanded_tokens.update(sx_map.get(sx_code, []))
            tokens = list(expanded_tokens)
            
        # Build query vector
        query_vector = build_query_vector(tokens, dictionary, N)
        if not query_vector:  # If no valid terms found
            return []
            
        # Calculate cosine similarity scores
        scores = defaultdict(float)
        
        for term, query_weight in query_vector.items():
            if term in dictionary:
                _, postings = dictionary[term]
                for doc_id, doc_weight in postings:
                    # Cosine similarity: sum of (query_weight * normalized_doc_weight)
                    if doc_id in doc_lengths and doc_lengths[doc_id] > 0:
                        normalized_doc_weight = doc_weight / doc_lengths[doc_id]
                        scores[doc_id] += query_weight * normalized_doc_weight
        
        # Sort by score (descending) then by docID (ascending) for ties
        ranked_docs = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
        
        # Return top K results with document names
        results = []
        for doc_id, score in ranked_docs[:TOP_K_RESULTS]:
            if doc_id in id_to_doc:
                results.append((id_to_doc[doc_id], score))
                
        return results
        
    except KeyboardInterrupt:
        print("\nSearch interrupted by user.")
        return []
    except Exception as e:
        print(f"\nError processing query: {str(e)}")
        return []

def main():
    try:
        # Initialize system
        corpus_dir = r"C:\Users\kousi\OneDrive\Desktop\study\new IR project\Corpus"
        print("Building index...")
        dictionary, doc_lengths, docIDs, id_to_doc, N = build_index(corpus_dir)
        
        if N == 0:
            print("No documents found or indexed.")
            return
            
        print("Precomputing Soundex mappings...")
        sx_map = precompute_soundex(dictionary)
        print(f"\nIndex ready for {N} documents with {len(dictionary)} unique terms.")
        print("Enter your queries. Type 'exit' to quit.\n")
        
        while True:
            try:
                # Get query
                query = input("\nEnter query (or 'exit'): ").strip()
                if query.lower() in ["exit", "quit"]:
                    break
                if not query:
                    print("Empty query. Please try again.")
                    continue
                    
                # Get search options
                use_soundex = input("Enable Soundex? (y/n): ").strip().lower() == "y"
                use_spell = input("Enable Spell Correction? (y/n): ").strip().lower() == "y"
                
                # Process query and time it
                import time
                start_time = time.time()
                
                results = process_query(
                    query, dictionary, doc_lengths, id_to_doc, N,
                    use_soundex=use_soundex, 
                    use_spellcorrection=use_spell,
                    sx_map=sx_map
                )
                
                search_time = time.time() - start_time
                
                # Display results
                if not results:
                    print("\nNo matching documents found.")
                else:
                    print(f"\nFound {len(results)} results in {search_time:.3f} seconds:")
                    print("-" * 70)
                    for i, (doc, score) in enumerate(results, 1):
                        print(f"{i:2d}. {doc:<45} (cosine similarity: {score:.6f})")
                    print("-" * 70)
                
            except KeyboardInterrupt:
                print("\nSearch interrupted. Type 'exit' to quit or try another query.")
                continue
                
            except Exception as e:
                print(f"\nError during search: {str(e)}")
                print("Please try again.")
                continue
                
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
    finally:
        print("\nExiting search system.")

if __name__ == "__main__":
    main()