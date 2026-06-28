#!/usr/bin/env bash
set -e
SCRIPT="$(pwd)/dfly_ppn2.py"
OUT_DIR="$(pwd)/results"
# Dragonfly sizes (same group grids as PPN=1), hosts_per_router=2 -> PPN=2
SIZES=("4" "16" "64")
mkdir -p "$OUT_DIR"
for S in "${SIZES[@]}"; do
    echo "=== Running dragonfly size $S (PPN=2) ==="
    export DFLY_SIZE="$S"
    export STATS_DIR="$OUT_DIR"
    sst "$SCRIPT" 2>&1 | tee "$OUT_DIR/dragonfly_${S}_ppn2_run.log"
done
echo "All PPN=2 dragonfly runs finished. Results in: $OUT_DIR"
