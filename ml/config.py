"""Central configuration for the CityLens CV pipeline.

Everything the pipeline needs is resolved here so the individual steps stay
small and the whole thing can be retargeted to a different urban object by
changing a single value (CITYLENS_TARGET).
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dotenv is optional at runtime
    load_dotenv = None

ROOT = Path(__file__).resolve().parents[1]

if load_dotenv is not None:
    load_dotenv(ROOT / ".env")

# --- Target object -----------------------------------------------------------
# KVKK: this MUST be an inanimate urban object (sign, bin, pothole, ...). Never
# a person, face, plate or anything that identifies an individual.
# `TARGET_OBJECT` is the English prompt fed to the zero-shot detector.
# `TARGET_LABEL` is the human-readable label written into detections.json.
TARGET_OBJECT = os.getenv("CITYLENS_TARGET", "traffic sign")
TARGET_LABEL = os.getenv("CITYLENS_TARGET_LABEL", "trafik levhası")

# --- Models (Hugging Face) ---------------------------------------------------
# Prefer the locally downloaded weights; fall back to the Hub id otherwise.
_LOCAL_GDINO = Path(
    os.getenv(
        "GROUNDING_DINO_DIR",
        r"C:\Users\scadenza\Downloads\citylens-hf-models\01-grounding-dino-tiny-open-vocabulary-detector",
    )
)
GROUNDING_DINO_MODEL = str(_LOCAL_GDINO) if _LOCAL_GDINO.exists() else "IDEA-Research/grounding-dino-tiny"

# Detection thresholds for Grounding DINO.
BOX_THRESHOLD = float(os.getenv("BOX_THRESHOLD", "0.30"))
TEXT_THRESHOLD = float(os.getenv("TEXT_THRESHOLD", "0.25"))

# Anonymization prompt used as a backstop blur pass (faces + plates).
ANON_PROMPT = os.getenv("CITYLENS_ANON_PROMPT", "human face. license plate.")
ANON_BOX_THRESHOLD = float(os.getenv("ANON_BOX_THRESHOLD", "0.25"))

# --- Google Street View Static API ------------------------------------------
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
STREETVIEW_SIZE = os.getenv("STREETVIEW_SIZE", "640x640")
STREETVIEW_FOV = os.getenv("STREETVIEW_FOV", "80")
STREETVIEW_PITCH = os.getenv("STREETVIEW_PITCH", "0")

# --- Directories -------------------------------------------------------------
DATA = ROOT / "data"
RAW_DIR = DATA / "raw"            # KVKK: gitignored; DELETED at the end.
ANON_DIR = DATA / "anon"          # faces + plates irreversibly blurred.
PROCESSED_DIR = DATA / "processed"
MANIFEST_JSON = PROCESSED_DIR / "manifest.json"
RAW_DETECTIONS_JSON = PROCESSED_DIR / "raw_detections.json"

# Output sinks for the final, anonymized detections.json (the demo contract).
WEB_ANON_DIR = ROOT / "web" / "public" / "anon"
BACKEND_EMBED_JSON = ROOT / "backend" / "internal" / "infrastructure" / "detection" / "detections.json"
WEB_PUBLIC_JSON = ROOT / "web" / "public" / "detections.json"
PROCESSED_JSON = PROCESSED_DIR / "detections.json"


def ensure_dirs() -> None:
    """Creates all working directories (idempotent)."""
    for directory in (RAW_DIR, ANON_DIR, PROCESSED_DIR, WEB_ANON_DIR):
        directory.mkdir(parents=True, exist_ok=True)
