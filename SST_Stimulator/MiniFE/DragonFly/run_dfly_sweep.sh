#!/usr/bin/env bash
set -e
SCRIPT="$(pwd)/dfly_ppn1.py"
OUT_DIR="$(pwd)/results"
# Dragonfly sizes (nodes), all with hosts_per_router=1 -> PPN=1
SIZES=("4" "16" "64")
mkdir -p "$OUT_DIR"
for S in "${SIZES[@]}"; do
    echo "=== Running dragonfly size $S (PPN=1) ==="
    export DFLY_SIZE="$S"
    export STATS_DIR="$OUT_DIR"
    sst "$SCRIPT" 2>&1 | tee "$OUT_DIR/dragonfly_${S}_ppn1_run.log"
done
echo "All dragonfly runs finished. Results in: $OUT_DIR"
