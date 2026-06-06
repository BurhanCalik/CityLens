"""Runs the full CityLens CV pipeline in the KVKK-safe order.

    fetch  ->  anonymize  ->  detect  ->  export

Anonymization always runs before detection. If any step fails, the pipeline
stops so a later step can never read un-anonymized data.
"""

from __future__ import annotations

import sys

import anonymize
import detect
import export
import fetch

STEPS = [
    ("fetch", fetch.main),
    ("anonymize", anonymize.main),
    ("detect", detect.main),
    ("export", export.main),
]


def main() -> int:
    print("=" * 64)
    print("CityLens CV pipeline | KVKK order: fetch -> anonymize -> detect -> export")
    print("=" * 64)
    for name, step in STEPS:
        print(f"\n##### STEP: {name} #####")
        code = step()
        if code != 0:
            print(f"\nStep '{name}' failed (exit {code}). Stopping.", file=sys.stderr)
            return code
    print("\nAll steps complete. detections.json published to backend + web + data/processed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
