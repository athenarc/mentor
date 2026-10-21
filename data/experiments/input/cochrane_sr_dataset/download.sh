#!/usr/bin/env bash
# Download only the Cochrane split CSVs required by experiments
# (suite scoring / analyze). Lives under data/experiments/input/.
#
# Source: Mendeley Data DOI 10.17632/7sgmg89zb6.1 (Chan et al., 2025)
# The public archive also contains a second "manual search" dataset; this
# script discards that and keeps only the five split files.
#
# Usage:
#   ./download.sh
#   ./download.sh --force   # re-download even if CSVs already exist

set -euo pipefail

DOWNLOAD_URL="https://data.mendeley.com/public-api/zip/7sgmg89zb6/download/1"
EXPECTED_CHECKSUM="27dc9142917b9b528bfcc4bc57532181fb7d792883e19d02b1a001f0ce6a0eba"
MAIN_ZIP="Title and Abstract Screening Data for Systematic Review.zip"
NESTED_ZIP="20240827_Systematic_Review_Data.zip"

REQUIRED_CSVS=(
  "20240827_dev_set.csv"
  "20240827_val_set.csv"
  "20240827_random_test_set.csv"
  "20240827_heart_test_set.csv"
  "20240827_HIV_test_set.csv"
)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

FORCE=false
for arg in "$@"; do
  case "$arg" in
    --force|-f) FORCE=true ;;
    -h|--help)
      sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 2
      ;;
  esac
done

have_all=true
for csv in "${REQUIRED_CSVS[@]}"; do
  if [[ ! -f "$csv" ]]; then
    have_all=false
    break
  fi
done

if [[ "$have_all" == true && "$FORCE" == false ]]; then
  echo "Required CSVs already present in $SCRIPT_DIR"
  echo "Pass --force to re-download."
  exit 0
fi

tmpdir="$(mktemp -d "${TMPDIR:-/tmp}/cochrane_sr_dataset.XXXXXX")"
cleanup() {
  rm -rf "$tmpdir"
}
trap cleanup EXIT

sha256_file() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    echo "Need shasum or sha256sum" >&2
    exit 1
  fi
}

download() {
  local url="$1" out="$2"
  echo "Downloading archive from Mendeley Data..."
  if command -v curl >/dev/null 2>&1; then
    curl -L --progress-bar -o "$out" "$url"
  elif command -v wget >/dev/null 2>&1; then
    wget --show-progress -O "$out" "$url"
  else
    echo "Need curl or wget" >&2
    exit 1
  fi
}

if ! command -v unzip >/dev/null 2>&1; then
  echo "Need unzip" >&2
  exit 1
fi

main_zip_path="$tmpdir/$MAIN_ZIP"
download "$DOWNLOAD_URL" "$main_zip_path"

actual="$(sha256_file "$main_zip_path")"
if [[ "$actual" != "$EXPECTED_CHECKSUM" ]]; then
  echo "Checksum mismatch for $MAIN_ZIP" >&2
  echo "  expected: $EXPECTED_CHECKSUM" >&2
  echo "  actual:   $actual" >&2
  exit 1
fi
echo "Checksum OK"

echo "Extracting nested split archive..."
# Nested zip may be at top level or one directory down.
if ! unzip -l "$main_zip_path" | grep -q "$NESTED_ZIP"; then
  echo "Nested archive $NESTED_ZIP not found in download" >&2
  exit 1
fi
unzip -j -o "$main_zip_path" "*${NESTED_ZIP}" -d "$tmpdir" >/dev/null
nested_zip_path="$tmpdir/$NESTED_ZIP"
if [[ ! -f "$nested_zip_path" ]]; then
  echo "Failed to extract $NESTED_ZIP" >&2
  exit 1
fi

echo "Extracting required CSVs into $SCRIPT_DIR ..."
for csv in "${REQUIRED_CSVS[@]}"; do
  unzip -j -o "$nested_zip_path" "*${csv}" -d "$SCRIPT_DIR" >/dev/null
  if [[ ! -f "$SCRIPT_DIR/$csv" ]]; then
    echo "Missing required file after extract: $csv" >&2
    exit 1
  fi
  echo "  $csv"
done

echo
echo "Done. Kept only:"
for csv in "${REQUIRED_CSVS[@]}"; do
  ls -lh "$SCRIPT_DIR/$csv" | awk '{print "  " $5 "\t" $9}'
done
echo
echo "Manual-search dataset and archive leftovers were not kept."
