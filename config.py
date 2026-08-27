import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
SCENARIOS_FILE = BASE_DIR / "scenarios.json"

PRIMARY_MODEL = os.getenv("GROQ_MODEL")

FALLBACK_MODELS = [
    PRIMARY_MODEL,
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]

MAX_TURNS = int(os.getenv("MAX_TURNS", "40"))

FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

# Temporary authentication for testing
TEST_USER = os.getenv("TEST_USER")
TEST_PASS = os.getenv("TEST_PASS")