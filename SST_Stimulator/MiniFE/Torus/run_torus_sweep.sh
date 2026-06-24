#!/usr/bin/env bash
set -e
SCRIPT="$(pwd)/torus_ppn1.py"
OUT_DIR="$(pwd)/results"
# Torus shapes (square, matching the mesh sizes): 4,16,64,256,1024 nodes
SHAPES=("2x2" "4x4" "8x8" "16x16" "32x32")
mkdir -p "$OUT_DIR"
for SHAPE in "${SHAPES[@]}"; do
    echo "=== Running torus $SHAPE (PPN=1) ==="
    export MESH_SHAPE="$SHAPE"
    export STATS_DIR="$OUT_DIR"
    sst "$SCRIPT" 2>&1 | tee "$OUT_DIR/torus_${SHAPE}_ppn1_run.log"
done
echo "All torus runs finished. Results in: $OUT_DIR"
