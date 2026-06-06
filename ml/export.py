"""Step 4 - publish the final, anonymized detections.json (the demo contract).

It writes the SAME document to three places so every consumer stays in sync:
  - backend embed file (baked into the Go binary at build time)
  - web/public/detections.json (offline fallback for the map)
  - data/processed/detections.json (canonical, reproducible artifact)

It also copies the anonymized evidence image for each detection into
web/public/anon/ so the map's evidence panel can show it.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone

import config


def _severity_by_rank(rank_fraction: float) -> str:
    """Relative REVIEW PRIORITY within the batch (human-in-the-loop, responsible AI).

    Grounding DINO is zero-shot (no fine-tuning), so absolute confidence is modest
    and not directly comparable to a trained model. Instead of hard score cutoffs,
    we RANK detections by confidence and verify the least-confident first — these
    are the most likely "candidate problems" (missing/toppled/occluded signs):
      - lowest third  -> urgent  (acil insan doğrulaması — aday)
      - middle third  -> warning (takip)
      - highest third -> info    (yüksek güven — doğrulanmış envanter)
    """
    if rank_fraction < 0.34:
        return "urgent"
    if rank_fraction < 0.67:
        return "warning"
    return "info"


def main() -> int:
    config.ensure_dirs()

    if not config.RAW_DETECTIONS_JSON.exists():
        print("No raw_detections.json. Run detect.py first.")
        return 1

    raw = json.loads(config.RAW_DETECTIONS_JSON.read_text(encoding="utf-8"))
    processed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # One representative pin per pano (the highest-confidence detection per image)
    # so pins never stack on identical coordinates.
    best: dict[str, dict] = {}
    for d in raw:
        if d.get("lat") is None or d.get("lng") is None:
            continue
        key = d["image"]
        if key not in best or float(d["score"]) > float(best[key]["score"]):
            best[key] = d

    items = sorted(best.values(), key=lambda d: float(d["score"]))
    total = len(items)

    out = []
    for rank, d in enumerate(items):
        image_name = d["image"]
        # Copy the anonymized evidence image into the web public folder.
        src = config.ANON_DIR / image_name
        if src.exists():
            shutil.copyfile(src, config.WEB_ANON_DIR / image_name)

        rank_fraction = (rank + 0.5) / total if total else 1.0
        out.append(
            {
                "lat": round(float(d["lat"]), 6),
                "lng": round(float(d["lng"]), 6),
                "label": d.get("label", config.TARGET_LABEL),
                "score": round(float(d["score"]), 4),
                "image_url": f"/anon/{image_name}",
                "address": d.get("address", ""),
                "severity": _severity_by_rank(rank_fraction),
                "captured_at": processed_at,
            }
        )

    payload = json.dumps(out, ensure_ascii=False, indent=2)
    for sink in (config.BACKEND_EMBED_JSON, config.WEB_PUBLIC_JSON, config.PROCESSED_JSON):
        sink.write_text(payload, encoding="utf-8")
        print(f"wrote {len(out)} detection(s) -> {sink}")

    print("\nDONE. To serve the new data:")
    print("  - rebuild the backend (embed),  OR")
    print("  - set DETECTIONS_PATH=data/processed/detections.json and restart it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
