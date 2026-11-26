#!/bin/bash
# Τεστ εφικτότητας δεύτερου agent (MoE). Σχέδιο: docs/plan_moe_test.md (γράφτηκε 27/11 ΠΡΙΝ τρέξει).
# Χρήση (από τον φάκελο του repo, PYTHONPATH=.):  bash moe_test.sh <logdir> <agent model> <guard model> [test]
# Benign μόνο (χωρίς επίθεση), 16 εργασίες banking, 2 ρυθμίσεις: none και guard2_oguard (agent MoE + guards με το μικρό μοντέλο).
# Δύο διεργασίες παράλληλα (εργασίες 0-7 / 8-15). Το guard2_oguard κόβεται στα 45 λεπτά (όριο GPU αν τα 2 μοντέλα δεν χωράνε).
# Μετά από κάθε ρύθμιση: ollama ps + nvidia-smi (μνήμη).
LOG=$1; AGENT=$2; GUARD=$3; mkdir -p "$LOG"
UT_A="0 1 2 3 4 5 6 7"; UT_B="8 9 10 11 12 13 14 15"
if [ "$4" = "test" ]; then UT_A="13"; UT_B="2"; fi
for D in none guard2_oguard; do
  echo "===== $D ====="
  T=""; [ "$D" != "none" ] && T="timeout 45m"
  $T python run_bench.py --logdir "$LOG" --ut $UT_A --benign --defense "$D" --agent-model "$AGENT" --guard-model "$GUARD" > "$LOG.$D.A.log" 2>&1 &
  $T python run_bench.py --logdir "$LOG" --ut $UT_B --benign --defense "$D" --agent-model "$AGENT" --guard-model "$GUARD" > "$LOG.$D.B.log" 2>&1 &
  wait
  (ollama ps; nvidia-smi --query-gpu=memory.used,memory.total --format=csv) > "$LOG.$D.mem.txt" 2>&1 || true
done
echo "===== ΤΕΛΟΣ moe test ====="
