#!/usr/bin/env bash
set -e
SCRIPT="$(pwd)/minimd_torus3d_ppn1.py"
OUT_DIR="$(pwd)/results"
# 3D torus shapes (match the MiniMD 3D mesh sizes): 8,16,64,128,512 nodes
SHAPES=("2x2x2" "2x2x4" "4x4x4" "4x4x8" "8x8x8")
mkdir -p "$OUT_DIR"
for SHAPE in "${SHAPES[@]}"; do
    echo "=== Running MiniMD 3D torus $SHAPE (PPN=1) ==="
    export MESH_SHAPE="$SHAPE"
    export STATS_DIR="$OUT_DIR"
    sst "$SCRIPT" 2>&1 | tee "$OUT_DIR/minimd_torus_${SHAPE}_ppn1_run.log"
done
echo "All MiniMD torus runs finished. Results in: $OUT_DIR"
