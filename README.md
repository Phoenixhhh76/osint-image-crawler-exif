# OSINT Image Crawler and EXIF Analyzer

A small Python project that demonstrates practical OSINT fundamentals through two tasks:

- crawling public websites for image assets
- extracting and analyzing image metadata and EXIF information

This repository is designed as a portfolio-friendly version of the `arachnide` exercise, showing both implementation ability and security awareness.

## Why This Is OSINT

OSINT is not only about collecting public data, but also about structuring and interpreting it. This project demonstrates that workflow by:

- collecting images from publicly accessible web pages
- inspecting metadata that may reveal useful investigative clues
- identifying privacy-sensitive fields such as timestamps, device details, and embedded metadata
- applying basic constraints around scope, recursion, and error handling

## Tools

### `spider`

Downloads image files from a target website.

Features:

- supports `http://` and `https://`
- optional recursive crawling with `-r`
- configurable maximum depth with `-l`
- configurable output directory with `-p`
- restricted to the same hostname as the starting URL
- supports `.jpg`, `.jpeg`, `.png`, `.gif`, and `.bmp`

### `scorpion`

Reads one or more image files and prints available metadata.

Features:

- shows basic file information
- shows image format, mode, and dimensions
- extracts EXIF data when available
- prints other metadata such as PNG textual fields
- handles missing files, unsupported extensions, and parsing errors

## Tech Stack

- Python 3
- `requests` for HTTP requests
- `BeautifulSoup` for HTML parsing
- `Pillow` for image metadata and EXIF extraction

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chmod +x spider scorpion run_checks.sh
```

### Run `spider`

```bash
./spider "https://example.com"
./spider -r "https://example.com"
./spider -r -l 2 -p ./data_test "https://example.com"
```

### Run `scorpion`

```bash
./scorpion ./data/sample.jpg
./scorpion ./data/sample.jpg ./data/sample.png
```

### Run Checks

```bash
bash ./run_checks.sh
bash ./run_checks.sh "https://www.python.org"
bash ./run_checks.sh --all
```

## Project Structure

```text
osint-image-crawler-exif/
├── .gitignore
├── README.md
├── README_zh-TW.md
├── requirements.txt
├── run_checks.sh
├── spider
├── spider.py
├── scorpion
├── scorpion.py
└── docs/
    ├── implementation_review_zh-TW.md
    ├── osint_prerequisites_zh-TW.md
    └── project_requirements_zh-TW.md
```

## Documentation

- `README_zh-TW.md`: Traditional Chinese project overview
- `docs/project_requirements_zh-TW.md`: translated exercise requirements
- `docs/osint_prerequisites_zh-TW.md`: background notes on HTTP, URLs, EXIF, and security basics
- `docs/implementation_review_zh-TW.md`: implementation checklist and risk review

## Security and Ethics

This project is intended for legal, authorized, educational, and research use only.

When using tools like these, you should:

- respect website terms of service and `robots.txt`
- avoid sending abusive or excessive requests
- treat metadata as potentially sensitive information
- never use OSINT tooling for unauthorized collection or surveillance

## Portfolio Value

This project helps demonstrate that you can:

- build a basic crawler in Python
- extract and interpret image metadata
- explain the privacy implications of EXIF data
- implement input handling, recursion limits, and error handling with a security mindset

## Possible Next Improvements

- support image URLs without a file extension by validating `Content-Type`
- export metadata as JSON for downstream analysis
- improve URL normalization and deduplication
- add a GUI or metadata editing/removal features
