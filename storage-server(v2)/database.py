import numpy as np
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
from config import Config

class VectorDatabase:
    def __init__(self):
        self.config = Config()
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.titles = None
        self.contents = None
        self.page_ids = None
        
    def create_index(self, pages):
        """Create FAISS index from pages using title + content embeddings"""
        page_ids = list(pages.keys())
        titles = [pages[pid]['title'] for pid in page_ids]
        contents = [pages[pid]['content'] for pid in page_ids]

        # Combine title and content for hybrid search
        combined_texts = [f"{title}. {content}" for title, content in zip(titles, contents)]
        embeddings = self.model.encode(combined_texts)
        dimension = embeddings.shape[1]
        
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings))
        
        return index, page_ids, titles, contents
        
    def update_index(self, pages, deleted_page_ids=None):
        if self.index is None or self.titles is None or self.contents is None or self.page_ids is None:
            return self.create_index(pages)
            
        # Handle deletions
        if deleted_page_ids:
            self._handle_deletions(deleted_page_ids)
        
        new_page_ids = []
        new_titles = []
        new_contents = []
        updated_indices = []
        
        for pid, page_data in pages.items():
            if pid in self.page_ids:
                idx = self.page_ids.index(pid)
                self.titles[idx] = page_data['title']
                self.contents[idx] = page_data['content']
                updated_indices.append(idx)
            else:
                new_page_ids.append(pid)
                new_titles.append(page_data['title'])
                new_contents.append(page_data['content'])
        
        # Re-embed updated pages
        if updated_indices:
            updated_texts = [f"{self.titles[i]}. {self.contents[i]}" for i in updated_indices]
            updated_embeddings = self.model.encode(updated_texts)

            for i, emb_idx in enumerate(updated_indices):
                self.index.reconstruct(emb_idx, updated_embeddings[i])  # NOTE: only works with some FAISS index types

        # Add new pages
        if new_page_ids:
            new_combined = [f"{title}. {content}" for title, content in zip(new_titles, new_contents)]
            new_embeddings = self.model.encode(new_combined)
            self.index.add(np.array(new_embeddings))

            self.page_ids.extend(new_page_ids)
            self.titles.extend(new_titles)
            self.contents.extend(new_contents)
        
        return self.index, self.page_ids, self.titles, self.contents

    def _handle_deletions(self, deleted_page_ids):
        """Handle removal of deleted pages from the index"""
        keep_mask = [pid not in deleted_page_ids for pid in self.page_ids]
        remove_indices = [i for i, keep in enumerate(keep_mask) if not keep]
        
        if not remove_indices:
            return
            
        remove_ids = faiss.IDSelectorArray(remove_indices)
        self.index.remove_ids(remove_ids)  # May not work with IndexFlatL2 directly

        self.page_ids = [pid for pid, keep in zip(self.page_ids, keep_mask) if keep]
        self.titles = [title for title, keep in zip(self.titles, keep_mask) if keep]
        self.contents = [content for content, keep in zip(self.contents, keep_mask) if keep]

    def save_index(self, index, page_ids, titles, contents):
        """Save index and data to disk"""
        faiss.write_index(index, self.config.INDEX_FILE)
        
        with open(self.config.TITLES_FILE, "wb") as f:
            pickle.dump(titles, f)
            
        with open(self.config.CONTENTS_FILE, "wb") as f:
            pickle.dump(contents, f)
            
        with open(self.config.PAGE_IDS_FILE, "wb") as f:
            pickle.dump(page_ids, f)
            
    def load_index(self):
        """Load index from disk if exists"""
        if not (os.path.exists(self.config.INDEX_FILE) and 
                os.path.exists(self.config.TITLES_FILE) and 
                os.path.exists(self.config.CONTENTS_FILE) and
                os.path.exists(self.config.PAGE_IDS_FILE)):
            return None, None, None, None
            
        index = faiss.read_index(self.config.INDEX_FILE)
        
        with open(self.config.TITLES_FILE, "rb") as f:
            titles = pickle.load(f)
            
        with open(self.config.CONTENTS_FILE, "rb") as f:
            contents = pickle.load(f)
            
        with open(self.config.PAGE_IDS_FILE, "rb") as f:
            page_ids = pickle.load(f)
            
        self.index = index
        self.titles = titles
        self.contents = contents
        self.page_ids = page_ids
            
        return index, page_ids, titles, contents
