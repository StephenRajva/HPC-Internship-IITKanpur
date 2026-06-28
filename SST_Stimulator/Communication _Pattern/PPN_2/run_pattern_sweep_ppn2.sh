#!/usr/bin/env bash
set -e
SCRIPT="$(pwd)/pattern_mesh_ppn2.py"
PATTERNS=("adjacent" "halfshift" "mirrored")
SHAPES=("2x2" "4x4" "8x8" "16x16" "32x32")   # 4,16,64,256,1024 routers -> 8..2048 nodes
for P in "${PATTERNS[@]}"; do
    OUT_DIR="$(pwd)/$P/results"
    mkdir -p "$OUT_DIR"
    for SHAPE in "${SHAPES[@]}"; do
        echo "=== $P on mesh $SHAPE (PPN=2) ==="
        export PATTERN="$P"
        export MESH_SHAPE="$SHAPE"
        export STATS_DIR="$OUT_DIR"
        sst "$SCRIPT" 2>&1 | tee "$OUT_DIR/${P}_mesh_${SHAPE}_ppn2_run.log"
    done
done
echo "All PPN=2 pattern runs finished."
