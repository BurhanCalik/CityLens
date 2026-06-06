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

# --- Target categories -------------------------------------------------------
# KVKK: every category MUST be an inanimate urban object. Never a person, face,
# plate or anything that identifies an individual.
#
# Multi-category open-vocabulary detection: one combined Grounding DINO prompt,
# then each detected box is mapped back to a category by its matched phrase.
# Each category carries its OWN confidence threshold (precision tuning), a draw
# color for the evidence image, a Turkish display label, and matching aliases.
CATEGORIES = [
    {
        "key": "traffic_sign",
        "prompt": "traffic sign",
        "label": "Trafik levhası",
        "threshold": float(os.getenv("TH_TRAFFIC_SIGN", "0.30")),
        "color": "#2dd4bf",
        "aliases": ["traffic sign", "traffic", "road sign", "street sign"],
    },
    {
        "key": "billboard",
        "prompt": "billboard",
        "label": "Reklam panosu",
        "threshold": float(os.getenv("TH_BILLBOARD", "0.40")),
        "color": "#a78bfa",
        "aliases": ["billboard", "bill board", "hoarding", "advertisement"],
    },
    {
        "key": "garbage",
        "prompt": "garbage",
        "label": "Çöp / atık",
        "threshold": float(os.getenv("TH_GARBAGE", "0.34")),
        "color": "#f97316",
        "aliases": ["garbage", "trash", "litter", "rubbish"],
    },
]


def detection_prompt() -> str:
    """Combined Grounding DINO prompt, e.g. 'traffic sign. billboard. garbage.'."""
    return " ".join(c["prompt"].strip().rstrip(".") + "." for c in CATEGORIES)


def category_for_label(text: str):
    """Maps a Grounding DINO matched phrase to a category dict, or None (noise).

    More specific categories are checked before the generic 'sign' family so an
    ambiguous match doesn't get misfiled.
    """
    t = (text or "").lower()
    for key in ("billboard", "garbage", "traffic_sign"):
        cat = next(c for c in CATEGORIES if c["key"] == key)
        if any(alias in t for alias in cat["aliases"]):
            return cat
    return None


# Inference-time floor (lowest per-category threshold); per-category thresholds
# are then applied in detect.py for precision.
BASE_BOX_THRESHOLD = min(c["threshold"] for c in CATEGORIES)

# --- Models (Hugging Face) ---------------------------------------------------
# Prefer the locally downloaded weights; fall back to the Hub id otherwise.
_LOCAL_GDINO = Path(
    os.getenv(
        "GROUNDING_DINO_DIR",
        r"C:\Users\scadenza\Downloads\citylens-hf-models\01-grounding-dino-tiny-open-vocabulary-detector",
    )
)
GROUNDING_DINO_MODEL = str(_LOCAL_GDINO) if _LOCAL_GDINO.exists() else "IDEA-Research/grounding-dino-tiny"

# Grounding DINO text threshold (phrase-match strength). Box thresholds are
# per-category (see CATEGORIES); BASE_BOX_THRESHOLD is the inference-time floor.
TEXT_THRESHOLD = float(os.getenv("TEXT_THRESHOLD", "0.20"))

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
