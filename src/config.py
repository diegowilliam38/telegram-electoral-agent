import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import re

# API Keys (Regex to obliterate ALL spaces, tabs, newlines, and carriage returns from copy-paste)
_raw_openai = os.getenv("OPENAI_API_KEY", "").replace("\\n", "").replace("\\r", "").replace('"', '').replace("'", "")
OPENAI_API_KEY = re.sub(r'\s+', '', _raw_openai)

_raw_tg = os.getenv("TELEGRAM_BOT_TOKEN", "").replace("\\n", "").replace("\\r", "").replace('"', '').replace("'", "")
TELEGRAM_BOT_TOKEN = re.sub(r'\s+', '', _raw_tg)

# Paths (Relative to avoid C++ Unicode FileIO errors on Windows)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join("docs", "references")
DB_DIR = os.path.join("data", "faiss_index")
TOPICS_FILE = os.path.join("data", "topics.json")

# Model Settings
MODEL_NAME = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# Vector DB Settings
COLLECTION_NAME = "manual_eleitoral"

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env")
