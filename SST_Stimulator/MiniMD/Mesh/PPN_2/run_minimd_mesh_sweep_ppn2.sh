#!/usr/bin/env bash
set -e
SCRIPT="$(pwd)/minimd_mesh3d_ppn2.py"
OUT_DIR="$(pwd)/results"
SHAPES=("2x2x2" "2x2x4" "4x4x4" "4x4x8" "8x8x8")
mkdir -p "$OUT_DIR"
for SHAPE in "${SHAPES[@]}"; do
    echo "=== MiniMD 3D mesh $SHAPE (PPN=2) ==="
    export MESH_SHAPE="$SHAPE"
    export STATS_DIR="$OUT_DIR"
    sst "$SCRIPT" 2>&1 | tee "$OUT_DIR/minimd_mesh_${SHAPE}_ppn2_run.log"
done
echo "All PPN=2 MiniMD mesh runs finished. Results in: $OUT_DIR"
