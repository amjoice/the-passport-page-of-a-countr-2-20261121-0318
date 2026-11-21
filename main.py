#!/usr/bin/env python3
"""Talvera Passport Spread — deliver the pre-rendered image.

The artwork lives in this repo as entry.png. This script only copies
that file into the grading output folder, using nothing beyond the
standard library, so it runs on a bare python:3.13-slim image that has
no Pillow installed. No generation, no fonts, no network.
"""

import shutil
import sys
from pathlib import Path

SOURCE_NAME = "entry.png"
TARGET_NAME = "entry.png"


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / SOURCE_NAME
    if not source.is_file():
        print(f"missing {SOURCE_NAME} next to main.py", file=sys.stderr)
        return 1
    for candidate in (Path("/output") / TARGET_NAME, Path("output") / TARGET_NAME):
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, candidate)
        except OSError:
            continue
        size = candidate.stat().st_size
        print(f"copied {SOURCE_NAME} -> {candidate} ({size} bytes)")
        return 0
    print("could not write entry.png to any output folder", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
