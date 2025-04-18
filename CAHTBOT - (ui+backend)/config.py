import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Existing configuration
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))  # seconds
    
    # Absolute paths configuration
    DATA_DIR = os.path.abspath(os.getenv("DATA_DIR", "data"))  # Defaults to ./data if not specified
    INDEX_FILE = os.path.join(DATA_DIR, "faiss_index.index")
    TITLES_FILE = os.path.join(DATA_DIR, "titles.pkl")
    CONTENTS_FILE = os.path.join(DATA_DIR, "contents.pkl")
    ETAGS_FILE = os.path.join(DATA_DIR, "etags.pkl")