#!/bin/bash
# Dev του guard εξόδων (σχέδιο: docs/plan_oguard_dev.md, γράφτηκε 26/11 ΠΡΙΝ τρέξει).
# Χρήση (από τον φάκελο του repo, PYTHONPATH=.):   bash oguard_dev.sh <logdir> [test]
# Μόνο εργασίες dev: επιθέσεις στις 5, 6, 7 (ASI01 0-8 + LLM06 100-103), benign στις 2, 4, 5, 6, 7, 11.
# Δύο διεργασίες παράλληλα, μία ανά περιτύλιγμα (important_instructions / injecagent), στο ίδιο logdir.
# Σειρά: άμυνα -> benign -> επιθέσεις. Επεισόδια που υπάρχουν δεν ξανατρέχουν.
LOG=$1; mkdir -p "$LOG"
UT_ATT="5 6 7"; BEN_A="2 4 5"; BEN_B="6 7 11"; ITS="asi01 llm06"
if [ "$2" = "test" ]; then UT_ATT="5"; BEN_A="2"; BEN_B="11"; ITS="injection_task_1 injection_task_100"; fi
worker () {  # $1 = περιτύλιγμα, $2 = benign εργασίες
  for D in none oguard; do
    echo "===== $D benign ($2) ====="
    python run_bench.py --logdir "$LOG" --ut $2 --benign --defense "$D"
    echo "===== $D $1 ====="
    python run_bench.py --logdir "$LOG" --ut $UT_ATT --it $ITS --attack "$1" --defense "$D"
  done
  echo "===== ΤΕΛΟΣ διεργασίας ($1) ====="
}
worker important_instructions "$BEN_A" > "$LOG.A.log" 2>&1 &
worker injecagent "$BEN_B" > "$LOG.B.log" 2>&1 &
wait
echo "===== ΤΕΛΟΣ oguard dev ====="
