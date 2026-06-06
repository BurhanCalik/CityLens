"""Step 1 - fetch Google Street View Static images for the points in points.json.

Quota-friendly: we call the FREE metadata endpoint first; if no imagery exists
at a point we skip it without spending a billable image request.

KVKK: raw images land in data/raw/ which is GITIGNORED and DELETED at the end of
the event (documented in docs/KVKK-IMHA.md). They are NEVER committed.
"""

from __future__ import annotations

import json
import sys

import requests

import config

META_URL = "https://maps.googleapis.com/maps/api/streetview/metadata"
IMG_URL = "https://maps.googleapis.com/maps/api/streetview"


def main() -> int:
    config.ensure_dirs()

    if not config.GOOGLE_MAPS_API_KEY:
        print("ERROR: GOOGLE_MAPS_API_KEY is not set in .env — cannot fetch.", file=sys.stderr)
        return 1

    points_path = config.ROOT / "ml" / "points.json"
    points = json.loads(points_path.read_text(encoding="utf-8"))

    manifest = []
    for i, p in enumerate(points, start=1):
        loc = f"{p['lat']},{p['lng']}"

        try:
            # 1) FREE metadata check (saves quota).
            meta = requests.get(
                META_URL,
                params={"location": loc, "key": config.GOOGLE_MAPS_API_KEY},
                timeout=20,
            ).json()
            if meta.get("status") != "OK":
                print(f"[{i:04d}] skip (status={meta.get('status')}) {loc}")
                continue

            # 2) Billable image request.
            params = {
                "size": config.STREETVIEW_SIZE,
                "location": loc,
                "fov": p.get("fov", config.STREETVIEW_FOV),
                "heading": p.get("heading", 0),
                "pitch": p.get("pitch", config.STREETVIEW_PITCH),
                "key": config.GOOGLE_MAPS_API_KEY,
                "return_error_code": "true",
            }
            resp = requests.get(IMG_URL, params=params, timeout=30)
            if resp.status_code != 200:
                print(f"[{i:04d}] image error {resp.status_code} {loc}")
                continue

            raw_path = config.RAW_DIR / f"{i:04d}.jpg"
            raw_path.write_bytes(resp.content)

            # Prefer the pano's true location from metadata over the requested point.
            loc_meta = meta.get("location", {})
            manifest.append(
                {
                    "id": f"{i:04d}",
                    "lat": loc_meta.get("lat", p["lat"]),
                    "lng": loc_meta.get("lng", p["lng"]),
                    "address": p.get("address", ""),
                    "raw": raw_path.name,
                    "captured_at": meta.get("date", ""),
                }
            )
            print(f"[{i:04d}] ok {loc} -> {raw_path.name}")
        except Exception as exc:  # transient network error — skip point, keep going
            print(f"[{i:04d}] error {exc}")
            continue

    config.MANIFEST_JSON.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nFetched {len(manifest)} image(s). Manifest -> {config.MANIFEST_JSON}")
    print(">> NEXT (KVKK): run anonymize.py BEFORE any detection.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
