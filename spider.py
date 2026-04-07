#!/usr/bin/env python3
"""Spider: recursively download images from a website."""

from __future__ import annotations

import argparse
import mimetypes
import re
import sys
from collections import deque
from pathlib import Path
from typing import Iterable
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

DEFAULT_DEPTH = 5
DEFAULT_OUTPUT = Path("./data")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
SHORT_OPTIONS = {"r", "l", "p"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spider",
        description="Download images from a URL (optionally recursively).",
        usage="%(prog)s [-r] [-l [N]] [-p [PATH]] URL",
    )
    parser.add_argument(
        "-r",
        action="store_true",
        help="Recursively crawl pages and download images.",
    )
    parser.add_argument(
        "-l",
        metavar="N",
        help=f"Maximum recursive depth (default: {DEFAULT_DEPTH}).",
    )
    parser.add_argument(
        "-p",
        metavar="PATH",
        help=f"Output directory (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument("url", nargs="?", help="Starting URL (http/https).")
    return parser


def expand_compound_short_options(argv: list[str]) -> list[str]:
    expanded: list[str] = []
    for token in argv:
        if not token.startswith("-") or token == "-" or token.startswith("--"):
            expanded.append(token)
            continue

        cluster = token[1:]
        idx = 0
        while idx < len(cluster):
            opt = cluster[idx]
            if opt not in SHORT_OPTIONS:
                expanded.append(f"-{cluster[idx:]}")
                break

            expanded.append(f"-{opt}")
            idx += 1
            if opt in {"l", "p"} and idx < len(cluster):
                remainder = cluster[idx:]
                if set(remainder) <= SHORT_OPTIONS:
                    continue
                expanded.append(remainder)
                break
    return expanded


def looks_like_int(token: str) -> bool:
    return bool(re.fullmatch(r"-?\d+", token))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    tokens = expand_compound_short_options(sys.argv[1:] if argv is None else argv)

    recursive = False
    max_depth = DEFAULT_DEPTH
    output_dir = DEFAULT_OUTPUT
    url: str | None = None
    depth_option_used = False

    idx = 0
    while idx < len(tokens):
        token = tokens[idx]

        if token in {"-h", "--help"}:
            parser.print_help()
            raise SystemExit(0)

        if token == "-r":
            recursive = True
        elif token == "-l":
            depth_option_used = True
            if idx + 1 < len(tokens) - 1:
                candidate = tokens[idx + 1]
                if looks_like_int(candidate):
                    try:
                        max_depth = int(candidate)
                    except ValueError:
                        parser.error(f"argument -l: invalid int value: '{candidate}'")
                    idx += 1
                elif not candidate.startswith("-"):
                    parser.error(f"argument -l: invalid int value: '{candidate}'")
                else:
                    max_depth = DEFAULT_DEPTH
            else:
                max_depth = DEFAULT_DEPTH
        elif token == "-p":
            if idx + 1 < len(tokens) - 1:
                candidate = tokens[idx + 1]
                if not candidate.startswith("-"):
                    output_dir = Path(candidate)
                    idx += 1
                else:
                    output_dir = DEFAULT_OUTPUT
            else:
                output_dir = DEFAULT_OUTPUT
        elif token.startswith("-"):
            parser.error(f"unrecognized arguments: {token}")
        elif url is None:
            url = token
        else:
            parser.error(f"unrecognized arguments: {token}")

        idx += 1

    if url is None:
        parser.error("the following arguments are required: url")
    if depth_option_used and not recursive:
        parser.error("-l requires -r")
    args = argparse.Namespace(url=url, r=recursive, l=max_depth, p=output_dir)
    if args.l < 0:
        parser.error("-l must be >= 0")
    return args


def normalize_url(url: str) -> str:
    clean, _frag = urldefrag(url.strip())
    return clean


def is_http_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def same_hostname(url: str, base_hostname: str) -> bool:
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    return parsed.scheme in {"http", "https"} and hostname == base_hostname.lower()


def extension_from_url(url: str) -> str:
    path = urlparse(url).path
    ext = Path(path).suffix.lower()
    return ext


def looks_like_target_image(url: str) -> bool:
    return extension_from_url(url) in ALLOWED_EXTENSIONS


def safe_filename_from_url(url: str, fallback_stem: str = "image") -> str:
    parsed = urlparse(url)
    raw_name = Path(parsed.path).name
    if not raw_name:
        return f"{fallback_stem}.bin"
    name = re.sub(r"[^A-Za-z0-9._-]", "_", raw_name)
    return name or f"{fallback_stem}.bin"


def unique_path(target_dir: Path, filename: str) -> Path:
    path = target_dir / filename
    if not path.exists():
        return path

    stem = path.stem
    suffix = path.suffix
    idx = 1
    while True:
        candidate = target_dir / f"{stem}_{idx}{suffix}"
        if not candidate.exists():
            return candidate
        idx += 1


def fetch_html(session: requests.Session, url: str) -> str | None:
    try:
        resp = session.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"[WARN] Cannot fetch page: {url} ({exc})")
        return None

    content_type = resp.headers.get("Content-Type", "")
    if "html" not in content_type.lower():
        print(f"[INFO] Skip non-HTML page: {url} ({content_type or 'unknown'})")
        return None
    return resp.text


def iter_page_links(html: str, base_url: str) -> Iterable[str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all("a", href=True):
        href = tag.get("href", "").strip()
        if not href:
            continue
        if href.startswith(("mailto:", "javascript:", "tel:", "#")):
            continue
        absolute = normalize_url(urljoin(base_url, href))
        if is_http_url(absolute):
            yield absolute


def iter_image_links(html: str, base_url: str) -> Iterable[str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all("img", src=True):
        src = tag.get("src", "").strip()
        if not src or src.startswith("data:"):
            continue
        absolute = normalize_url(urljoin(base_url, src))
        if is_http_url(absolute) and looks_like_target_image(absolute):
            yield absolute


def inferred_extension(url: str, content_type: str) -> str:
    ext = extension_from_url(url)
    if ext in ALLOWED_EXTENSIONS:
        return ext
    guessed = mimetypes.guess_extension(content_type.split(";")[0].strip().lower() or "")
    if guessed and guessed.lower() in ALLOWED_EXTENSIONS:
        return guessed.lower()
    return ".bin"


def download_image(session: requests.Session, image_url: str, output_dir: Path) -> None:
    try:
        with session.get(image_url, timeout=15, stream=True) as resp:
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "")
            ext = inferred_extension(image_url, content_type)

            original = safe_filename_from_url(image_url, fallback_stem="image")
            filename = original
            if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
                filename = f"{Path(filename).stem}{ext}"

            destination = unique_path(output_dir, filename)
            with destination.open("wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"[OK] {image_url} -> {destination}")
    except requests.RequestException as exc:
        print(f"[WARN] Cannot download image: {image_url} ({exc})")
    except OSError as exc:
        print(f"[WARN] Cannot write image: {image_url} ({exc})")


def crawl_and_download(start_url: str, recursive: bool, max_depth: int, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    base_hostname = (urlparse(start_url).hostname or "").lower()

    with requests.Session() as session:
        session.headers.update({"User-Agent": "arachnide-spider/1.0"})
        visited_pages: set[str] = set()
        downloaded_images: set[str] = set()

        queue: deque[tuple[str, int]] = deque()
        queue.append((normalize_url(start_url), 0))

        while queue:
            page_url, depth = queue.popleft()
            if page_url in visited_pages:
                continue
            visited_pages.add(page_url)

            html = fetch_html(session, page_url)
            if html is None:
                continue

            for image_url in iter_image_links(html, page_url):
                if not same_hostname(image_url, base_hostname):
                    continue
                if image_url in downloaded_images:
                    continue
                downloaded_images.add(image_url)
                download_image(session, image_url, output_dir)

            if not recursive:
                continue
            if depth >= max_depth:
                continue

            for next_page in iter_page_links(html, page_url):
                if same_hostname(next_page, base_hostname) and next_page not in visited_pages:
                    queue.append((next_page, depth + 1))


def main() -> int:
    args = parse_args()
    start_url = normalize_url(args.url)
    if not is_http_url(start_url):
        print("[ERROR] URL must start with http:// or https:// and include a hostname.")
        return 1

    crawl_and_download(
        start_url=start_url,
        recursive=args.r,
        max_depth=args.l,
        output_dir=args.p,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
