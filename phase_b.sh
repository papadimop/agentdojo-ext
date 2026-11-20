#!/bin/bash
# Φάση Β: όλες οι άμυνες στα ίδια user tasks. Χρήση (από τον φάκελο του repo):
#   bash phase_b.sh <logdir> <user tasks...>        π.χ. bash phase_b.sh runs/B 3 13
# Για κάθε άμυνα: benign (ψευδείς συναγερμοί, utility) και επιθέσεις.
#   none, 4 έτοιμες: ASI01 (9) + LLM06 (4).   count_limit: μόνο LLM06 (στο ASI01 δεν υπάρχουν επαναλήψεις).
# Σειρά: τα πιο σημαντικά πρώτα, ώστε αν κοπεί το session να έχουν γίνει αυτά.
# Αν μια άμυνα αποτύχει (π.χ. δεν κατεβαίνει μοντέλο), το script συνεχίζει με την επόμενη.
LOG=$1; shift; UT="$@"
for D in none count_limit transformers_pi_detector tool_filter spotlighting_with_delimiting repeat_user_prompt; do
  if [ "$D" = "count_limit" ]; then IT="llm06"; else IT="asi01 llm06"; fi
  echo "===== $D: benign ====="
  python run_bench.py --logdir "$LOG" --ut $UT --benign --defense "$D"
  echo "===== $D: επιθέσεις ($IT) ====="
  python run_bench.py --logdir "$LOG" --ut $UT --it $IT --defense "$D"
done
echo "===== ΤΕΛΟΣ ΦΑΣΗΣ Β ====="
