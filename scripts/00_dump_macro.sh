#!/usr/bin/env bash
set -euo pipefail

ISYNTAX="$1"
OUT="$2"

echo "Input slide: $ISYNTAX"
echo "Output macro: $OUT"

# This uses the Philips PixelEngine helper
python3 /work/PythonTools/dump_macro_label.py "$ISYNTAX"

# The script usually writes:
#   <SLIDE>_MACROIMAGE.jpg
# in the same folder as the slide

MACRO_AUTO="$(dirname "$ISYNTAX")/$(basename "$ISYNTAX" .isyntax)_MACROIMAGE.jpg"

if [ ! -f "$MACRO_AUTO" ]; then
  echo "ERROR: Macro not produced."
  exit 1
fi

cp "$MACRO_AUTO" "$OUT"

echo "Saved macro -> $OUT"
