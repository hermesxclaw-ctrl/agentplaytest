#!/usr/bin/env bash
# Sequential captured runs for the demo: friendly then hostile, Gemma 3 4B.
# 20-step budget per run (disclosed in the reports): on this shared 2-core
# box each step costs minutes of CPU time, and every behavior the demo
# demonstrates (real play, fixation, flailing) resolves well within 20.
cd "$(dirname "$0")"
export PYTHONUNBUFFERED=1
echo "=== friendly (gemma-3-4b-it) ==="
# Labels are run-specific on purpose: the bare "friendly"/"hostile" labels
# belong to the original captured artifacts in runs/. Every reproduction
# gets its own label so re-running the demo can never silently overwrite
# another run's evidence.
python3 playtest.py --target friendly --backend llamacpp --model gemma-3-4b-it --max-steps 20 --label friendly-4b
echo "=== hostile (gemma-3-4b-it) ==="
python3 playtest.py --target hostile --backend llamacpp --model gemma-3-4b-it --max-steps 20 --label hostile-4b
echo "ALL RUNS DONE"
