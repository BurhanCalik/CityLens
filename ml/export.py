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


def _severity(score: float) -> str:
    """Confidence-based review priority (human-in-the-loop, responsible AI):
    low-confidence detections are flagged for URGENT manual verification."""
    if score >= 0.60:
        return "info"
    if score >= 0.45:
        return "warning"
    return "urgent"


def main() -> int:
    config.ensure_dirs()

    if not config.RAW_DETECTIONS_JSON.exists():
        print("No raw_detections.json. Run detect.py first.")
        return 1

    raw = json.loads(config.RAW_DETECTIONS_JSON.read_text(encoding="utf-8"))
    processed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    out = []
    used_images = set()
    for d in raw:
        if d.get("lat") is None or d.get("lng") is None:
            print(f"skip {d.get('image')} (no coordinates in manifest)")
            continue

        image_name = d["image"]
        # Copy the anonymized evidence image into the web public folder.
        src = config.ANON_DIR / image_name
        if src.exists() and image_name not in used_images:
            shutil.copyfile(src, config.WEB_ANON_DIR / image_name)
            used_images.add(image_name)

        out.append(
            {
                "lat": round(float(d["lat"]), 6),
                "lng": round(float(d["lng"]), 6),
                "label": d.get("label", config.TARGET_LABEL),
                "score": round(float(d["score"]), 4),
                "image_url": f"/anon/{image_name}",
                "address": d.get("address", ""),
                "severity": _severity(float(d["score"])),
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
