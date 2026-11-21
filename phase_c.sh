#!/bin/bash
# Φάση Γ: ο guard κλήσεων. Χρήση (από τον φάκελο του repo):
#   bash phase_c.sh <logdir> <user tasks...>
# Τρέχει none και guard στα ίδια user tasks: benign + ASI01 (9) + LLM06 (4).
# Το none χρειάζεται για σύγκριση στο ίδιο logdir (π.χ. στα dev user tasks 5,6,7).
# Οι αποφάσεις του guard τυπώνονται στο stderr ως γραμμές "GUARD ALLOW|BLOCK|UNPARSED->ALLOW ...".
LOG=$1; shift; UT="$@"
for D in none guard; do
  echo "===== $D: benign ====="
  python run_bench.py --logdir "$LOG" --ut $UT --benign --defense "$D"
  echo "===== $D: επιθέσεις (asi01 llm06) ====="
  python run_bench.py --logdir "$LOG" --ut $UT --it asi01 llm06 --defense "$D"
done
echo "===== ΤΕΛΟΣ ΦΑΣΗΣ Γ ====="
