#!/usr/bin/env python3
"""Scorpion: display image metadata (basic + EXIF when available)."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import ExifTags, Image

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="scorpion",
        description="Display metadata from one or more image files.",
    )
    parser.add_argument("files", nargs="+", help="Image file paths to inspect.")
    return parser.parse_args()


def format_timestamp(ts: float) -> str:
    return datetime.fromtimestamp(ts).isoformat(sep=" ", timespec="seconds")


def normalize_exif_value(value: Any) -> Any:
    if isinstance(value, bytes):
        preview = value[:16].hex()
        return f"<bytes: len={len(value)}, hex_preview={preview}>"
    if isinstance(value, tuple):
        return tuple(normalize_exif_value(v) for v in value)
    if isinstance(value, list):
        return [normalize_exif_value(v) for v in value]
    if isinstance(value, dict):
        return {k: normalize_exif_value(v) for k, v in value.items()}
    if isinstance(value, str):
        if len(value) > 240:
            return value[:240] + "...<truncated>"
        return value
    return value


def print_basic_info(path: Path) -> None:
    stat = path.stat()
    if hasattr(stat, "st_birthtime"):
        created_at = stat.st_birthtime
        created_at_source = "filesystem_birthtime"
    else:
        created_at = stat.st_mtime
        created_at_source = "filesystem_mtime_fallback"
    print("Basic:")
    print(f"  - file_name: {path.name}")
    print(f"  - file_path: {path.resolve()}")
    print(f"  - extension: {path.suffix.lower()}")
    print(f"  - size_bytes: {stat.st_size}")
    print(f"  - created_at: {format_timestamp(created_at)}")
    print(f"  - created_at_source: {created_at_source}")
    print(f"  - status_changed_at: {format_timestamp(stat.st_ctime)}")
    print(f"  - modified_at: {format_timestamp(stat.st_mtime)}")


def print_exif_info(img: Image.Image) -> None:
    exif_raw = img.getexif()
    if not exif_raw:
        print("EXIF:")
        print("  - no_exif_data: true")
        return

    exif_entries = {}
    for tag_id, value in exif_raw.items():
        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
        exif_entries[tag_name] = normalize_exif_value(value)

    print("EXIF:")
    for key in sorted(exif_entries):
        print(f"  - {key}: {exif_entries[key]}")


def print_other_metadata(img: Image.Image) -> None:
    # PNG often stores textual metadata in info dict.
    # For other formats this section may be empty.
    if not img.info:
        print("Other metadata:")
        print("  - none: true")
        return

    print("Other metadata:")
    for key in sorted(img.info):
        print(f"  - {key}: {normalize_exif_value(img.info[key])}")


def inspect_file(path_str: str) -> bool:
    path = Path(path_str)
    print("=" * 70)
    print(f"File: {path}")

    if not path.exists():
        print(f"[ERROR] File not found: {path}")
        return False
    if not path.is_file():
        print(f"[ERROR] Not a file: {path}")
        return False

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        print(
            f"[ERROR] Unsupported extension: {path.suffix} "
            f"(allowed: {', '.join(sorted(SUPPORTED_EXTENSIONS))})"
        )
        return False

    try:
        print_basic_info(path)
        with Image.open(path) as img:
            print(f"Image:")
            print(f"  - format: {img.format}")
            print(f"  - mode: {img.mode}")
            print(f"  - size: {img.width}x{img.height}")
            print_exif_info(img)
            print_other_metadata(img)
        return True
    except Exception as exc:
        print(f"[ERROR] Failed to parse metadata: {path} ({exc})")
        return False


def main() -> int:
    args = parse_args()
    success_count = 0
    for file_path in args.files:
        if inspect_file(file_path):
            success_count += 1
    print("=" * 70)
    print(f"Processed {len(args.files)} file(s), successful: {success_count}")
    return 0 if success_count == len(args.files) else 1


if __name__ == "__main__":
    raise SystemExit(main())
