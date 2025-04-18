import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
from config import Config

config = Config()
model = SentenceTransformer("all-MiniLM-L6-v2")

def store_pages_in_faiss(pages: dict):
    titles, contents = list(pages.keys()), list(pages.values())
    embeddings = model.encode(contents)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    
    # Ensure directory exists
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    # Save with absolute paths
    faiss.write_index(index, config.INDEX_FILE)
    
    with open(config.TITLES_FILE, "wb") as f:
        pickle.dump(titles, f)
        
    with open(config.CONTENTS_FILE, "wb") as f:
        pickle.dump(contents, f)
    
    return index, titles, contents

def load_index_from_disk():
    """Load index from disk using absolute paths"""
    if not (os.path.exists(config.INDEX_FILE) and 
            os.path.exists(config.TITLES_FILE) and 
            os.path.exists(config.CONTENTS_FILE)):
        return None, None, None
        
    index = faiss.read_index(config.INDEX_FILE)
    
    with open(config.TITLES_FILE, "rb") as f:
        titles = pickle.load(f)
        
    with open(config.CONTENTS_FILE, "rb") as f:
        contents = pickle.load(f)
        
    return index, titles, contents

def search_relevant_page(query, index, titles, contents):
    if index is None or not titles or not contents:
        return None, None
        
    query_embedding = model.encode([query])
    D, I = index.search(np.array(query_embedding), 3)
    if I[0][0] >= len(titles):
        return None, None
    return titles[I[0][0]], contents[I[0][0]]