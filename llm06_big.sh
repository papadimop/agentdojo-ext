#!/bin/bash
# Μεγάλο τρέξιμο LLM06 (σχέδιο: docs/plan_llm06_big.md, γράφτηκε 25/11 ΠΡΙΝ τρέξει).
# Χρήση (από τον φάκελο του repo, PYTHONPATH=.):   bash llm06_big.sh <root> <part>
#   π.χ. bash llm06_big.sh /kaggle/working/runs/big 1
# Κάθε επανάληψη σε δικό της φάκελο: <root>/r1 ... <root>/r4 (ο αναλυτής παίρνει την ετικέτα από εκεί).
# Δύο διεργασίες παράλληλα (OLLAMA_NUM_PARALLEL=2) με διαφορετικά user tasks στο ίδιο logdir.
# Σειρά: επανάληψη -> άμυνα -> benign ΠΡΩΤΑ (το χρειάζεται η μερική σπατάλη) -> 4 επιθέσεις LLM06.
# Αν κοπεί το session, οι πρώτες επαναλήψεις είναι πλήρεις. Επεισόδια που υπάρχουν δεν ξανατρέχουν.
ROOT=$1; PART=$2; mkdir -p "$ROOT"
UT_A="0 1 2 3 4 8 9"          # 13 εργασίες: όλες εκτός 5,6,7 (dev του guard v1/v2 με επιθέσεις)
UT_B="10 11 12 13 14 15"
case $PART in
  1) REPS="r1 r2"; DEFS="none guard2";                    DIRECT="none guard2" ;;
  2) REPS="r3 r4"; DEFS="none guard2";                    DIRECT="none guard2" ;;
  3) REPS="r1 r2"; DEFS="count_limit1 repeat_user_prompt"; DIRECT="" ;;
  4) REPS="r3 r4"; DEFS="count_limit1 repeat_user_prompt"; DIRECT="" ;;
  5) REPS="r1";    DEFS="count_limit";                      DIRECT="" ;;
  6) REPS="r1 r2"; DEFS="none oguard guard2_oguard";       DIRECT="" ;;  # 27/11: guard εξόδων (docs/plan_llm06_oguard.md)
  test) REPS="r1"; DEFS="none guard2 count_limit1"; DIRECT="none guard2"; UT_A="13"; UT_B="2" ;;
  test6) REPS="r1"; DEFS="none oguard guard2_oguard"; DIRECT=""; UT_A="13"; UT_B="2" ;;
  *) echo "part 1-6, test ή test6"; exit 1 ;;
esac

worker () {  # $1 = user tasks, $2 = 1 αν η διεργασία κάνει και τα απευθείας αιτήματα
  for R in $REPS; do
    for D in $DEFS; do
      echo "===== $R $D benign ($1) ====="
      python run_bench.py --logdir "$ROOT/$R" --ut $1 --benign --defense "$D"
      echo "===== $R $D llm06 ($1) ====="
      python run_bench.py --logdir "$ROOT/$R" --ut $1 --it llm06 --defense "$D"
    done
    if [ "$2" = "1" ]; then
      for D in $DIRECT; do
        echo "===== $R $D direct ====="
        python run_bench.py --logdir "$ROOT/$R" --direct --it llm06 --defense "$D"
      done
    fi
  done
  echo "===== ΤΕΛΟΣ διεργασίας ($1) ====="
}

worker "$UT_A" 0 > "$ROOT.P${PART}_A.log" 2>&1 &
worker "$UT_B" 1 > "$ROOT.P${PART}_B.log" 2>&1 &
wait
echo "===== ΤΕΛΟΣ part $PART ====="
