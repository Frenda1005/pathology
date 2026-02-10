#!/usr/bin/env bash
set -euo pipefail

ISYNTAX="$1"
X0="$2"
Y0="$3"
X1="$4"
Y1="$5"
LEVEL="${6:-2}"
TILE="${7:-1024}"   # tileW/tileH in level0 units

python3 /work/PythonTools/patch_extraction.py -b SOFTWARE \
  "$ISYNTAX" \
  -1 False \
  "${X0},${Y0},${X1},${Y1},${TILE},${TILE}" \
  "$LEVEL"
