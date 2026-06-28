#!/usr/bin/env bash
# Runs the MiniFE mesh PPN=2 sweep over all shapes (same sizes as PPN=1).
set -e
SCRIPT="$(pwd)/mesh_ppn2.py"
OUT_DIR="$(pwd)/results"
SHAPES=("2x2" "4x4" "8x8" "16x16" "32x32")   # 4,16,64,256,1024 routers/nodes-grid
mkdir -p "$OUT_DIR"
for SHAPE in "${SHAPES[@]}"; do
    echo "=== MiniFE mesh $SHAPE  (PPN=2) ==="
    export MESH_SHAPE="$SHAPE"
    export STATS_DIR="$OUT_DIR"
    sst "$SCRIPT" 2>&1 | tee "$OUT_DIR/mesh_${SHAPE}_ppn2_run.log"
done
echo "All PPN=2 mesh runs finished. Results in: $OUT_DIR"
