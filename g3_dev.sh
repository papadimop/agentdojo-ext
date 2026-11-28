#!/bin/bash
# Dev του guard κλήσεων v3 (σχέδιο: docs/plan_guard3_dev.md, γράφτηκε 28/11 ΠΡΙΝ τρέξει). ΜΟΝΟ εργασίες dev.
# Χρήση (από τον φάκελο του repo, PYTHONPATH=.):  bash g3_dev.sh <root> [test]
# Διεργασία A: slack, εργασίες 1 6 8 15, επιθέσεις LLM10 101-103 + ASI01 slack 1-5, ρυθμίσεις none, guard3, guard3_oguard.
# Διεργασία B: banking, εργασίες 2 4 11, επιθέσεις LLM06 100-103 + ASI01 banking 0-8, ρυθμίσεις none, guard2, guard3.
# 2 επαναλήψεις (r1, r2)· σειρά: επανάληψη -> ρύθμιση -> benign -> επιθέσεις. Επεισόδια που υπάρχουν δεν ξανατρέχουν.
ROOT=$1; mkdir -p "$ROOT"
S_UT="1 6 8 15"; S_ITS="llm10msg asi01slack"; B_UT="2 4 11"; B_ITS="llm06 asi01"; REPS="r1 r2"
if [ "$2" = "test" ]; then S_UT="6"; S_ITS="injection_task_101 injection_task_5"; B_UT="2"; B_ITS="injection_task_100 injection_task_1"; REPS="r1"; fi
slack () {
  for R in $REPS; do for D in none guard3 guard3_oguard; do
    echo "===== slack $R $D ====="
    python run_bench.py --suite slack --logdir "$ROOT/slack/$R" --ut $S_UT --benign --defense "$D"
    python run_bench.py --suite slack --logdir "$ROOT/slack/$R" --ut $S_UT --it $S_ITS --defense "$D"
  done; done
  echo "===== ΤΕΛΟΣ slack ====="
}
banking () {
  for R in $REPS; do for D in none guard2 guard3; do
    echo "===== banking $R $D ====="
    python run_bench.py --suite banking --logdir "$ROOT/banking/$R" --ut $B_UT --benign --defense "$D"
    python run_bench.py --suite banking --logdir "$ROOT/banking/$R" --ut $B_UT --it $B_ITS --defense "$D"
  done; done
  echo "===== ΤΕΛΟΣ banking ====="
}
slack > "$ROOT.slack.log" 2>&1 &
banking > "$ROOT.banking.log" 2>&1 &
wait
echo "===== ΤΕΛΟΣ g3 dev ====="
