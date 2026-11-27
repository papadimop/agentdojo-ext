#!/bin/bash
# Benign slack (χωρίς επίθεση, χωρίς άμυνα): ποιες εργασίες λύνει ο agent. Σχέδιο: docs/plan_llm10.md (27/11, πριν τρέξει).
# Χρήση (από τον φάκελο του repo, PYTHONPATH=.):  bash slack_benign.sh <root> [test]
# 21 εργασίες x 2 επαναλήψεις (r1, r2), δύο διεργασίες (0-10 / 11-20).
ROOT=$1; mkdir -p "$ROOT"
UT_A="0 1 2 3 4 5 6 7 8 9 10"; UT_B="11 12 13 14 15 16 17 18 19 20"
if [ "$2" = "test" ]; then UT_A="4 6"; UT_B="8 16"; fi
worker () {
  for R in r1 r2; do
    echo "===== $R benign slack ($1) ====="
    python run_bench.py --suite slack --logdir "$ROOT/$R" --ut $1 --benign --defense none
  done
  echo "===== ΤΕΛΟΣ διεργασίας ($1) ====="
}
worker "$UT_A" > "$ROOT.A.log" 2>&1 &
worker "$UT_B" > "$ROOT.B.log" 2>&1 &
wait
echo "===== ΤΕΛΟΣ benign slack ====="
