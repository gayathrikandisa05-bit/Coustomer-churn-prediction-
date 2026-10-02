"""Centralized project paths and reproducibility settings."""
from pathlib import Path

RANDOM_STATE = 42
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DATA_PATH = PROCESSED_DIR / "cleaned_telco_churn.csv"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


def ensure_directories() -> None:
    """Create directories used by reproducible pipeline outputs."""
    for directory in (INTERIM_DIR, PROCESSED_DIR, MODELS_DIR, REPORTS_DIR, FIGURES_DIR):
        directory.mkdir(parents=True, exist_ok=True)
