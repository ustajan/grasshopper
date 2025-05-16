#!/usr/bin/env bash
# run_grasshopper.sh
# Usage: ./run_grasshopper.sh input.gdml output_prefix

set -euo pipefail

# ---------- 1. Check arguments ----------
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <input.gdml> <output-prefix>"
  exit 1
fi

INPUT_GDML="$1"
OUT_PREFIX="$2"

# ---------- 2. Determine how many CPU cores we can use ----------
if CORES=$(getconf _NPROCESSORS_ONLN 2>/dev/null); then
  :             # already set
elif command -v nproc >/dev/null 2>&1; then
  CORES=$(nproc)
else
  echo "Cannot determine CPU core count; defaulting to 1."
  CORES=1
fi

echo "Detected $CORES logical core(s). Launching that many parallel grasshopper jobs..."

# ---------- 3. Launch one grasshopper job per core ----------
declare -a pids=()   # keep track of PIDs so we can wait for them

for (( seed=0; seed<CORES; seed++ )); do
  OUTFILE="${OUT_PREFIX}${seed}.root"
  LOGFILE="${OUT_PREFIX}${seed}.log"

  echo "  Starting seed ${seed} → ${OUTFILE} (log: ${LOGFILE})"

  # Run in background, disassociated from terminal; capture PID
  nohup grasshopper "${INPUT_GDML}" "${OUTFILE}" "${seed}" \
        >  "${LOGFILE}" 2>&1 &

  pids+=("$!")   # $! is PID of the job we just backgrounded
done

# ---------- 4. Wait for all jobs to complete ----------
echo "Waiting for all grasshopper jobs to finish..."

for pid in "${pids[@]}"; do
  if wait "$pid"; then
    :
  else
    echo "Warning: grasshopper job (PID $pid) exited with a non-zero status." >&2
  fi
done

echo "✅  All grasshopper jobs completed."
