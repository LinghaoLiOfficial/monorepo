#!/usr/bin/env python3
"""Fail if PROJECT_STRUCTURE_WITH_DEFINITIONS.md is stale."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "PROJECT_STRUCTURE_WITH_DEFINITIONS.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not TARGET.exists():
        print("[project-map-check] missing PROJECT_STRUCTURE_WITH_DEFINITIONS.md")
        print("Run: python3 scripts/generate_project_map.py")
        return 1

    before = sha256(TARGET)
    subprocess.run(["python3", "scripts/generate_project_map.py"], cwd=ROOT, check=True)
    after = sha256(TARGET)

    if before != after:
        print("[project-map-check] stale project map detected.")
        print("Run: python3 scripts/generate_project_map.py and commit updated file.")
        return 1

    print("[project-map-check] up-to-date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
