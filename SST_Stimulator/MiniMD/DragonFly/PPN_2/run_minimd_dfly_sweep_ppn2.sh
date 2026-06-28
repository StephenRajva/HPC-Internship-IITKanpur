#!/usr/bin/env bash
set -e
SCRIPT="$(pwd)/minimd_dfly_ppn2.py"
OUT_DIR="$(pwd)/results"
SIZES=("4" "16" "64")
mkdir -p "$OUT_DIR"
for S in "${SIZES[@]}"; do
    echo "=== MiniMD dragonfly size $S (PPN=2) ==="
    export DFLY_SIZE="$S"
    export STATS_DIR="$OUT_DIR"
    sst "$SCRIPT" 2>&1 | tee "$OUT_DIR/minimd_dragonfly_${S}_ppn2_run.log"
done
echo "All PPN=2 MiniMD dragonfly runs finished. Results in: $OUT_DIR"
