import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
    CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
    CONFLUENCE_API_KEY = os.getenv("CONFLUENCE_API_KEY")
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))  # seconds
    DATA_DIR = "data"
    INDEX_FILE = f"{DATA_DIR}/faiss_index.index"
    TITLES_FILE = f"{DATA_DIR}/titles.pkl"
    CONTENTS_FILE = f"{DATA_DIR}/contents.pkl"
    PAGE_IDS_FILE = f"{DATA_DIR}/page_ids.pkl"  # New file to track page IDs
    LAST_UPDATE_FILE = f"{DATA_DIR}/last_update.txt"  # New file to track last update time