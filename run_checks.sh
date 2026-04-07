#!/usr/bin/env bash
set -u

echo "== Arachnida quick checks =="

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] python3 not found"
  exit 1
fi

echo "[INFO] Python version:"
python3 --version

echo "[INFO] Checking required packages..."
python3 - <<'PY'
import importlib.util
import sys

required = ["requests", "bs4", "PIL"]
missing = [m for m in required if importlib.util.find_spec(m) is None]
if missing:
    print("[ERROR] Missing packages:", ", ".join(missing))
    print("Install with: python3 -m pip install requests beautifulsoup4 pillow")
    sys.exit(1)
print("[OK] All required packages are installed.")
PY
if [ $? -ne 0 ]; then
  exit 1
fi

echo "[INFO] Syntax check..."
if ! PYTHONPYCACHEPREFIX=.pycache python3 -m py_compile spider.py scorpion.py; then
  echo "[ERROR] Syntax check failed."
  exit 1
fi
echo "[OK] Syntax check passed."

OUT_DIR="./data_check"
rm -rf "${OUT_DIR}"
mkdir -p "${OUT_DIR}"
SCORPION_MODE="top3"
CUSTOM_URL=""
if [ $# -ge 1 ]; then
  for arg in "$@"; do
    case "${arg}" in
      --all)
        SCORPION_MODE="all"
        ;;
      *)
        CUSTOM_URL="${arg}"
        ;;
    esac
  done
fi
if [ -n "${CUSTOM_URL}" ]; then
  TEST_CANDIDATES=("${CUSTOM_URL}")
else
  TEST_CANDIDATES=(
    "https://www.python.org"
    "https://www.wikipedia.org"
    "https://www.mozilla.org"
  )
fi

run_spider_for_url() {
  local url="$1"
  echo "[INFO] Running spider (non-recursive) on: ${url}"
  if ! python3 spider.py -p "${OUT_DIR}" "${url}"; then
    echo "[WARN] spider non-recursive failed for: ${url}"
    return 1
  fi
  echo "[OK] spider non-recursive test passed."

  echo "[INFO] Running spider (recursive depth 1) on: ${url}"
  if ! python3 spider.py -r -l 1 -p "${OUT_DIR}" "${url}"; then
    echo "[WARN] spider recursive failed for: ${url}"
    return 1
  fi
  echo "[OK] spider recursive test passed."
  return 0
}

FOUND_IMAGES="$(python3 - <<'PY'
from pathlib import Path
exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
for p in sorted(Path("./data_check").rglob("*")):
    if p.is_file() and p.suffix.lower() in exts:
        print(p)
PY
)"

if [ -z "${FOUND_IMAGES}" ]; then
  for url in "${TEST_CANDIDATES[@]}"; do
    run_spider_for_url "${url}" || continue
    FOUND_IMAGES="$(python3 - <<'PY'
from pathlib import Path
exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
for p in sorted(Path("./data_check").rglob("*")):
    if p.is_file() and p.suffix.lower() in exts:
        print(p)
PY
)"
    if [ -n "${FOUND_IMAGES}" ]; then
      break
    fi
    echo "[WARN] No image found after testing: ${url}"
  done
fi

if [ -z "${FOUND_IMAGES}" ]; then
  echo "[WARN] No downloaded image found in ${OUT_DIR}; skipping scorpion runtime test."
  echo "[DONE] Basic checks completed with warning."
  exit 0
fi

if [ "${SCORPION_MODE}" = "all" ]; then
  echo "[INFO] Running scorpion on all downloaded images."
  if ! python3 scorpion.py ${FOUND_IMAGES}; then
    echo "[ERROR] scorpion all-images test failed."
    exit 1
  fi
  echo "[OK] scorpion all-images test passed."
else
  TOP3_IMAGES="$(printf '%s\n' "${FOUND_IMAGES}" | head -n 3)"
  echo "[INFO] Running scorpion on first 3 images."
  if ! python3 scorpion.py ${TOP3_IMAGES}; then
    echo "[ERROR] scorpion top-3 test failed."
    exit 1
  fi
  echo "[OK] scorpion top-3 test passed."
fi

echo "[DONE] All checks passed."
