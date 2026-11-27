#!/bin/bash
# LLM10 βήμα 3 (dev): σχέδιο docs/plan_llm10_dev.md (γράφτηκε 27/11 ΠΡΙΝ τρέξει).
# Χρήση (από τον φάκελο του repo, PYTHONPATH=.):  bash llm10_dev.sh <root> [test]
# Εργασίες dev 1, 6, 8, 15 (δύο διεργασίες: 1 6 / 8 15). Επιθέσεις: LLM10 101-103 + ASI01 slack 1-5. 1 επανάληψη (r1).
# Ρυθμίσεις με σειρά προτεραιότητας: none, oguard, guard2, guard2_oguard, sanitize, repeat_user_prompt.
ROOT=$1; mkdir -p "$ROOT"
UT_A="1 6"; UT_B="8 15"; ITS="llm10msg asi01slack"; DEFS="none oguard guard2 guard2_oguard sanitize repeat_user_prompt"
if [ "$2" = "test" ]; then UT_A="6"; UT_B="8"; ITS="injection_task_101 injection_task_1"; fi
worker () {
  for D in $DEFS; do
    echo "===== $D benign ($1) ====="
    python run_bench.py --suite slack --logdir "$ROOT/r1" --ut $1 --benign --defense "$D"
    echo "===== $D επιθέσεις ($1) ====="
    python run_bench.py --suite slack --logdir "$ROOT/r1" --ut $1 --it $ITS --defense "$D"
  done
  echo "===== ΤΕΛΟΣ διεργασίας ($1) ====="
}
worker "$UT_A" > "$ROOT.A.log" 2>&1 &
worker "$UT_B" > "$ROOT.B.log" 2>&1 &
wait
echo "===== ΤΕΛΟΣ llm10 dev ====="
