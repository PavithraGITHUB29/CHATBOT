# import time
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# from confluence_fetcher import ConfluenceFetcher
# from database import VectorDatabase
# from config import Config
# import os

# class ChangeHandler(FileSystemEventHandler):
#     def __init__(self, callback):
#         self.callback = callback
        
#     def on_modified(self, event):
#         if not event.is_directory:
#             self.callback()

# class ConfluenceIndexer:
#     def __init__(self):
#         self.config = Config()
#         self.fetcher = ConfluenceFetcher()
#         self.db = VectorDatabase()
#         self.running = False
        
#     def initial_index(self):
#         """Perform initial full index of all pages"""
#         print("Performing initial index...")
#         pages = self.fetcher.fetch_all_pages()
        
#         if pages is None:
#             print("Failed to fetch pages")
#             return False
            
#         index, page_ids, titles, contents = self.db.create_index(pages)
#         self.db.save_index(index, page_ids, titles, contents)
#         self.fetcher.save_current_page_ids(page_ids)
#         print("Initial index completed successfully")
#         return True
        
#     def update_index(self):
#         """Update index with changed pages"""
#         print("Checking for updates...")
        
#         # First check for deleted pages
#         current_page_ids = set(self.fetcher.get_current_page_ids() or [])
#         previous_page_ids = self.fetcher.load_previous_page_ids()
        
#         deleted_page_ids = previous_page_ids - current_page_ids
#         has_deletions = bool(deleted_page_ids)
        
#         print(f"Deleted pages detected: {len(deleted_page_ids)}")
        
#         # Then check for changed/added pages
#         changed_pages = self.fetcher.fetch_changed_pages()
        
#         if changed_pages is None:
#             print("Failed to check for updates")
#             return
            
#         print(f"Changed pages detected: {len(changed_pages)}")
        
#         if not changed_pages and not has_deletions:
#             print("No changes detected")
#             return
            
#         # Load existing index
#         index, page_ids, titles, contents = self.db.load_index()
        
#         if index is None:
#             print("No existing index found, performing initial index")
#             return self.initial_index()
            
#         print(f"Updating index with {len(changed_pages)} changes and {len(deleted_page_ids)} deletions")
        
#         # Update the index
#         index, page_ids, titles, contents = self.db.update_index(
#             changed_pages,
#             deleted_page_ids if has_deletions else None
#         )
        
#         # Save updated data
#         self.db.save_index(index, page_ids, titles, contents)
#         self.fetcher.save_current_page_ids(page_ids)
#         print("Index updated successfully")
#     def run(self):
#         """Run the indexer service"""
#         self.running = True
        
#         # Initial load or create index
#         index, page_ids, titles, contents = self.db.load_index()
#         if index is None:
#             if not self.initial_index():
#                 return
#         else:
#             print("Loaded existing index")
            
#         # Set up file watcher
#         event_handler = ChangeHandler(self.update_index)
#         observer = Observer()
#         observer.schedule(event_handler, path=self.config.DATA_DIR, recursive=True)
#         observer.start()
        
#         print("Confluence indexer service started")
        
#         try:
#             while self.running:
#                 time.sleep(self.config.CHECK_INTERVAL)
#                 self.update_index()
#         except KeyboardInterrupt:
#             observer.stop()
            
#         observer.join()

# if __name__ == "__main__":
#     indexer = ConfluenceIndexer()
#     indexer.run()

import time
from confluence_fetcher import ConfluenceFetcher
from database import VectorDatabase
from config import Config
import os

class ConfluenceIndexer:
    def __init__(self):
        self.config = Config()
        self.fetcher = ConfluenceFetcher()
        self.db = VectorDatabase()
        self.running = False
        
    def initial_index(self):
        """Perform initial full index of all pages"""
        print("Performing initial index...")
        pages = self.fetcher.fetch_all_pages()
        
        if pages is None:
            print("Failed to fetch pages")
            return False
            
        index, page_ids, titles, contents = self.db.create_index(pages)
        self.db.save_index(index, page_ids, titles, contents)
        self.fetcher.save_current_page_ids(page_ids)
        print(f"Initial index completed successfully with {len(page_ids)} pages")
        return True
        
    def update_index(self):
        """Update index with changed pages"""
        print("Checking for updates...")
        
        # First check for deleted pages
        current_page_ids = set(self.fetcher.get_current_page_ids() or [])
        previous_page_ids = self.fetcher.load_previous_page_ids()
        
        deleted_page_ids = previous_page_ids - current_page_ids
        has_deletions = bool(deleted_page_ids)
        
        if has_deletions:
            print(f"Deleted pages detected: {len(deleted_page_ids)}")
        
        # Then check for changed/added pages
        changed_pages = self.fetcher.fetch_changed_pages()
        
        if changed_pages is None:
            print("Failed to check for updates")
            return
            
        if changed_pages:
            print(f"Changed/added pages detected: {len(changed_pages)}")
        
        if not changed_pages and not has_deletions:
            print("No changes detected")
            return
            
        # Load existing index
        index, page_ids, titles, contents = self.db.load_index()
        
        if index is None:
            print("No existing index found, performing initial index")
            return self.initial_index()
            
        print(f"Updating index with {len(changed_pages)} changes and {len(deleted_page_ids)} deletions")
        
        # Update the index
        try:
            index, page_ids, titles, contents = self.db.update_index(
                changed_pages,
                deleted_page_ids if has_deletions else None
            )
            
            # Save updated data
            self.db.save_index(index, page_ids, titles, contents)
            self.fetcher.save_current_page_ids(page_ids)
            print("Index updated successfully")
        except Exception as e:
            print(f"Error updating index: {e}")
            # Fall back to full reindex if update fails
            print("Attempting full reindex...")
            self.initial_index()
        
    def run(self):
        """Run the indexer service"""
        self.running = True
        
        # Initial load or create index
        index, page_ids, titles, contents = self.db.load_index()
        if index is None:
            if not self.initial_index():
                return
        else:
            print(f"Loaded existing index with {len(page_ids)} pages")
            
        print("Confluence indexer service started")
        
        try:
            while self.running:
                self.update_index()
                time.sleep(self.config.CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            self.running = False

if __name__ == "__main__":
    indexer = ConfluenceIndexer()
    indexer.run()