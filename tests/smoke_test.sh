#!/usr/bin/env bash
# Smoke test for grasshopper: a short electron run on examples/beta/beta_lite.gdml.
#
# usage: smoke_test.sh [grasshopper-binary] [root-dir]
#   grasshopper-binary  defaults to `grasshopper` on PATH
#   root-dir            directory containing schema/ and examples/
#                       (the source tree, or <prefix>/share/grasshopper)
#
# Needs the Geant4 datasets in the environment (G4LEDATA etc.), as any Geant4
# run does. Runs in a temporary directory and leaves nothing behind.
# Exit status is 0 on success. Used by ctest, GitHub Actions and the
# conda-forge recipe test. The long regression test remains exec/unit_test/.
set -euo pipefail

BIN=${1:-grasshopper}
ROOT=${2:-"$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"}
SRC="$ROOT/examples/beta/beta_lite.gdml"
SCHEMA="$ROOT/schema/gdml.xsd"

[ -f "$SRC" ]    || { echo "smoke_test: missing $SRC" >&2; exit 1; }
[ -f "$SCHEMA" ] || { echo "smoke_test: missing $SCHEMA" >&2; exit 1; }

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
cd "$WORK"

# 500 events, no VRML file, schema resolved by absolute path.
sed -e 's|name="EventsToRun" value="[0-9]*"|name="EventsToRun" value="500"|' \
    -e 's|name="VRMLvisualizationOn" value="1"|name="VRMLvisualizationOn" value="0"|' \
    -e "s|xsi:noNamespaceSchemaLocation=\"[^\"]*\"|xsi:noNamespaceSchemaLocation=\"$SCHEMA\"|" \
    "$SRC" > smoke.gdml

echo "smoke_test: $("$BIN" --version)"

if ! "$BIN" smoke.gdml smoke_out 12345 > smoke.log 2>&1; then
  echo "smoke_test: grasshopper exited with an error; last lines of log:" >&2
  tail -40 smoke.log >&2
  exit 1
fi

if grep -q "VALIDATION ERROR" smoke.log; then
  echo "smoke_test: GDML validation errors reported:" >&2
  grep "VALIDATION ERROR" smoke.log | head >&2
  exit 1
fi

if [ ! -s smoke_out.dat ] || [ "$(wc -l < smoke_out.dat)" -le 1 ]; then
  echo "smoke_test: smoke_out.dat is missing or has no data rows" >&2
  tail -40 smoke.log >&2
  exit 1
fi

if command -v md5sum >/dev/null 2>&1; then
  sum=$(md5sum smoke_out.dat | cut -d' ' -f1)
else
  sum=$(md5 -q smoke_out.dat)
fi
echo "smoke_test: $(( $(wc -l < smoke_out.dat) - 1 )) rows, md5 $sum"
echo "smoke_test: OK"
