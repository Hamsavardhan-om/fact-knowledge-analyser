import os
from pathlib import Path
from dotenv import load_dotenv

# Load any .env present in root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DATA_DIR = BASE_DIR / "backend" / "data"
UPLOADS_DIR = DATA_DIR / "raw_uploads"
STORAGE_FILE = DATA_DIR / "storage.json"
CUSTOM_UPLOADS_FILE = DATA_DIR / "custom_uploads.json"
BENCHMARKS_DIR = DATA_DIR / "precomputed"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
BENCHMARKS_DIR.mkdir(parents=True, exist_ok=True)
