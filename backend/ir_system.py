import os
import pickle
from typing import Dict, List, Tuple, Set
import search

class IRSystem:
    def __init__(self, corpus_dir: str, index_dir: str = "index"):
        self.corpus_dir = corpus_dir
        self.index_dir = index_dir
        self.dictionary = {}
        self.doc_lengths = {}
        self.docIDs = {}
        self.id_to_doc = {}
        self.N = 0
        self.sx_map = {}
        
        # Create index directory if it doesn't exist
        if not os.path.exists(index_dir):
            os.makedirs(index_dir)
            
    def build_index(self) -> None:
        """Build and save the index to disk"""
        print("Building index...")
        (
            self.dictionary,
            self.doc_lengths,
            self.docIDs,
            self.id_to_doc,
            self.N
        ) = search.build_index(self.corpus_dir)
        
        if self.N > 0:
            print("Precomputing Soundex mappings...")
            self.sx_map = search.precompute_soundex(self.dictionary)
            self._save_index()
            print(f"Index built and saved with {self.N} documents and {len(self.dictionary)} unique terms.")
            
    def _save_index(self) -> None:
        """Save index data to disk"""
        index_data = {
            'dictionary': self.dictionary,
            'doc_lengths': self.doc_lengths,
            'docIDs': self.docIDs,
            'id_to_doc': self.id_to_doc,
            'N': self.N,
            'sx_map': self.sx_map
        }
        
        with open(os.path.join(self.index_dir, 'index.pkl'), 'wb') as f:
            pickle.dump(index_data, f)
            
    def load_index(self) -> bool:
        """Load index data from disk. Returns True if successful, False otherwise."""
        try:
            index_path = os.path.join(self.index_dir, 'index.pkl')
            if not os.path.exists(index_path):
                return False
                
            with open(index_path, 'rb') as f:
                index_data = pickle.load(f)
                
            self.dictionary = index_data['dictionary']
            self.doc_lengths = index_data['doc_lengths']
            self.docIDs = index_data['docIDs']
            self.id_to_doc = index_data['id_to_doc']
            self.N = index_data['N']
            self.sx_map = index_data['sx_map']
            
            return True
            
        except Exception as e:
            print(f"Error loading index: {e}")
            return False
            
    def search(self, query: str, use_soundex: bool = False, use_spellcorrection: bool = False) -> List[Tuple[str, float]]:
        """Search the index with the given query"""
        if not self.dictionary:  # If index is not loaded
            if not self.load_index():  # Try to load it
                self.build_index()  # If loading fails, rebuild it
                
        return search.process_query(
            query,
            self.dictionary,
            self.doc_lengths,
            self.id_to_doc,
            self.N,
            use_soundex=use_soundex,
            use_spellcorrection=use_spellcorrection,
            sx_map=self.sx_map
        )