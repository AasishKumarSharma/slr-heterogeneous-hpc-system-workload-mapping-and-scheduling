#!/bin/bash
# ==============================================================
# Full SLR Reproducibility Pipeline
# ==============================================================
# This script runs the complete extraction, analysis, and
# verification pipeline for the SLR paper.
#
# Prerequisites:
#   pip install -r ../requirements.txt
#
# Steps:
#   1. Extract data from PDFs (requires PDFs in SLR_PaperCollection/)
#   2. Generate analysis figures
#   3. Verify all paper claims against the dataset
# ==============================================================

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================="
echo "SLR Reproducibility Pipeline"
echo "=============================================="

# Step 1: PDF Extraction (optional - requires paper PDFs)
if [ "$1" == "--extract" ]; then
    echo ""
    echo "[Step 1/3] Running PDF extraction pipeline..."
    echo "  This requires paper PDFs in SLR_PaperCollection/"
    python3 extract_all_papers.py
else
    echo ""
    echo "[Step 1/3] Skipping PDF extraction (use --extract to run)"
    echo "  Using pre-extracted data from ../data/"
fi

# Step 2: Generate figures
echo ""
echo "[Step 2/3] Generating analysis figures..."
python3 analysis_and_figures.py

# Step 3: Verify paper claims
echo ""
echo "[Step 3/3] Verifying paper claims..."
python3 verify_paper_claims.py

echo ""
echo "=============================================="
echo "Pipeline complete. Check output above."
echo "=============================================="
