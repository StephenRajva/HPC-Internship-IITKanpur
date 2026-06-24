#!/usr/bin/env bash
# =============================================================================
#  run_mesh_sweep.sh  -  run the PPN=1 mesh scaling study for every size
# =============================================================================
#  What it does:
#    * keeps PPN fixed at 1 (handled inside mesh_ppn1.py)
#    * runs SST once per mesh shape
#    * writes one CSV + one text log per shape into the results folder
#
#  Edit the two paths below if your machine is different.
# =============================================================================

set -e  # stop if any command fails

# ---- EDIT THESE TWO PATHS IF NEEDED -----------------------------------------
SCRIPT="/Users/stephenrajva/Downloads/SST_Stimulator/MiniFE/Mesh/mesh_ppn1.py"
OUT_DIR="/Users/stephenrajva/Downloads/SST_Stimulator/MiniFE/Mesh/results"
# -----------------------------------------------------------------------------

# Mesh shapes to test (router grid). NxN means N*N nodes because local_ports=1.
#   2x2 ->4 nodes | 4x4 ->16 | 8x8 ->64 | 16x16 ->256 | 32x32 ->1024
SHAPES=("2x2" "4x4" "8x8" "16x16" "32x32")

mkdir -p "$OUT_DIR"
echo "Results will be saved in: $OUT_DIR"
echo

for SHAPE in "${SHAPES[@]}"; do
    echo "=============================================="
    echo " Running mesh $SHAPE  (PPN = 1)"
    echo "=============================================="

    export MESH_SHAPE="$SHAPE"
    export STATS_DIR="$OUT_DIR"

    # run SST and save everything printed to the screen into a log file too
    sst "$SCRIPT" 2>&1 | tee "$OUT_DIR/mesh_${SHAPE}_ppn1_run.log"

    echo "  -> done: $SHAPE"
    echo
done

echo "All runs finished. CSVs and logs are in: $OUT_DIR"
