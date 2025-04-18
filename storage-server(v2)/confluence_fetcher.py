import requests
import pickle
import os
from datetime import datetime, timedelta
from config import Config

class ConfluenceFetcher:
    def __init__(self):
        self.config = Config()
        os.makedirs(self.config.DATA_DIR, exist_ok=True)

    def _make_request(self, url, params=None):
        """Helper method to make authenticated requests"""
        auth = (self.config.CONFLUENCE_USERNAME, self.config.CONFLUENCE_API_KEY)
        try:
            response = requests.get(
                url,
                auth=auth,
                headers={"Accept": "application/json"},
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error making request: {e}")
            return None

    def fetch_all_pages(self):
        """Fetch all pages from Confluence (initial load)"""
        url = f"{self.config.CONFLUENCE_BASE_URL}/rest/api/content"
        params = {
            'type': 'page',
            'expand': 'body.storage,version',
            'limit': 200  # Max allowed by Confluence
        }
        
        all_pages = {}
        start = 0
        
        while True:
            params['start'] = start
            data = self._make_request(url, params)
            if not data:
                return None, None
            
            for page in data.get('results', []):
                all_pages[page['id']] = {
                    'title': page['title'],
                    'content': page['body']['storage']['value'],
                    'version': page['version']['number'],
                    'last_modified': page['version']['when']
                }
            
            if 'next' not in data.get('_links', {}):
                break
                
            start += data.get('size', len(data.get('results', [])))
        
        # Save last update time
        with open(self.config.LAST_UPDATE_FILE, 'w') as f:
            f.write(datetime.now().isoformat())
        
        return all_pages

    def fetch_changed_pages(self):
        """Fetch only pages changed since last update"""
        try:
            with open(self.config.LAST_UPDATE_FILE, 'r') as f:
                last_update = datetime.fromisoformat(f.read().strip())
        except (FileNotFoundError, ValueError):
            # If no last update time, do a full fetch
            return self.fetch_all_pages()
        
        # Format date according to Confluence API requirements
        since_date = (last_update - timedelta(seconds=5)).strftime('%Y-%m-%d %H:%M')
        
        
        url = f"{self.config.CONFLUENCE_BASE_URL}/rest/api/content/search"
        params = {
            'cql': f'type=page and lastModified>="{since_date}"',
            'expand': 'body.storage,version',
            'limit': 200
        }
        
        changed_pages = {}
        
        while True:
            data = self._make_request(url, params)
            if not data:
                return None
            
            for page in data.get('results', []):
                # Skip pages without required fields
                if not all(key in page for key in ['id', 'title', 'body', 'version']):
                    continue
                    
                if 'storage' not in page['body']:
                    continue
                    
                changed_pages[page['id']] = {
                    'title': page['title'],
                    'content': page['body']['storage']['value'],
                    'version': page['version']['number'],
                    'last_modified': page['version']['when']
                }
            
            if 'next' not in data.get('_links', {}):
                break
                
            params['start'] = data.get('start', 0) + data.get('size', len(data.get('results', [])))
        
        if changed_pages:
            with open(self.config.LAST_UPDATE_FILE, 'w') as f:
                f.write(datetime.now().isoformat())
        
        return changed_pages

    def get_current_page_ids(self):
        """Get the current list of all page IDs from Confluence"""
        url = f"{self.config.CONFLUENCE_BASE_URL}/rest/api/content"
        params = {
            'type': 'page',
            'fields': 'id',
            'limit': 200
        }
        
        page_ids = []
        start = 0
        
        while True:
            params['start'] = start
            data = self._make_request(url, params)
            if not data:
                return None
            
            page_ids.extend([page['id'] for page in data.get('results', [])])
            
            if 'next' not in data.get('_links', {}):
                break
                
            start += data.get('size', len(data.get('results', [])))
        
        return page_ids

    def load_previous_page_ids(self):
        """Load the previous list of page IDs from disk"""
        if not os.path.exists(self.config.PAGE_IDS_FILE):
            return set()
        with open(self.config.PAGE_IDS_FILE, 'rb') as f:
            return set(pickle.load(f))

    def save_current_page_ids(self, page_ids):
        """Save the current list of page IDs to disk"""
        with open(self.config.PAGE_IDS_FILE, 'wb') as f:
            pickle.dump(list(page_ids), f)