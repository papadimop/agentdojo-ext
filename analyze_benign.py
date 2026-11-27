"""Benign (χωρίς επίθεση): ποιες εργασίες λύνει ο agent, ανά επανάληψη. Οποιοδήποτε suite.
Χρήση: PYTHONPATH=. python analyze_benign.py <root>   (root με υποφακέλους επαναλήψεων r1, r2, ...)"""
import glob
import json
import os
import sys
from collections import defaultdict
from statistics import median

root = sys.argv[1]
res = defaultdict(dict)  # (pipeline, suite) -> {(task, rep): (utility, error, duration)}
partial = []
for p in glob.glob(f"{root}/*/*/*/user_task_*/none/none.json"):
    rep, pipe, suite, ut = p[len(root) + 1:].split(os.sep)[:4]
    j = json.load(open(p))
    if "utility" not in j:
        partial.append(p)
        continue
    res[(pipe, suite)][(int(ut.rsplit("_", 1)[1]), rep)] = (bool(j["utility"]), j.get("error") is not None, j.get("duration") or 0)
for (pipe, suite), d in sorted(res.items()):
    reps = sorted({r for _, r in d})
    tasks = sorted({t for t, _ in d})
    print(f"[{suite} / {pipe}] επαναλήψεις {reps}, εργασίες {len(tasks)}, επεισόδια {len(d)}, "
          f"σφάλματα {sum(v[1] for v in d.values())}, διάμεση διάρκεια {median(v[2] for v in d.values()):.0f} s")
    always, some, never = [], [], []
    for t in tasks:
        ok = [d[(t, r)][0] for r in reps if (t, r) in d]
        (always if all(ok) else some if any(ok) else never).append(t)
        print(f"   εργασία {t:2}: η δουλειά έγινε σε {sum(ok)} από τις {len(ok)} φορές")
    print(f"   ΠΑΝΤΑ: {always}\n   ΚΑΠΟΙΕΣ ΦΟΡΕΣ: {some}\n   ΠΟΤΕ: {never}")
    print(f"   σύνολο: η δουλειά έγινε σε {sum(v[0] for v in d.values())} από τα {len(d)} επεισόδια")
if partial:
    print("ΜΙΣΟΤΕΛΕΙΩΜΕΝΑ (δεν μετρούν):", partial)
