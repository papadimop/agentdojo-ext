"""Τεστ εφικτότητας δεύτερου agent: benign utility, σφάλματα, διάρκεια, βήματα ανά ρύθμιση.
Χρήση: PYTHONPATH=. python analyze_moe.py <logdir>  (π.χ. /kaggle/working/runs/MOE)"""
import glob
import json
import os
import sys
from statistics import mean, median

root = sys.argv[1]
REF_8B = {0, 3, 5, 6, 7, 8, 13, 14}  # qwen3:8b benign banking (επαληθευμένο 6/11, CLAUDE.md)
for d in sorted(os.listdir(root)):
    rows = []
    for p in glob.glob(f"{root}/{d}/banking/user_task_*/none/none.json"):
        j = json.load(open(p))
        msgs = j["messages"]
        rows.append({"u": int(j["user_task_id"].rsplit("_", 1)[1]), "util": bool(j["utility"]),
                     "err": j.get("error") is not None, "dur": j.get("duration") or 0,
                     "steps": sum(m["role"] == "assistant" for m in msgs),
                     "calls": sum(m["role"] == "tool" for m in msgs),
                     "blocked": sum(1 for m in msgs if m["role"] == "tool" and str(m.get("error") or "").startswith("Blocked"))})
    if not rows:
        continue
    solved = {r["u"] for r in rows if r["util"]}
    print(f"[{d}] επεισόδια {len(rows)} | utility {len(solved)}/{len(rows)} | σφάλματα {sum(r['err'] for r in rows)} | "
          f"διάρκεια μέση {mean(r['dur'] for r in rows):.0f}s διάμεση {median(r['dur'] for r in rows):.0f}s max {max(r['dur'] for r in rows):.0f}s | "
          f"κλήσεις εργαλείων μέσο {mean(r['calls'] for r in rows):.1f} | επεισόδια με μπλοκάρισμα {sum(r['blocked'] > 0 for r in rows)}")
    print(f"    λύνει: {sorted(solved)}")
    print(f"    σε σχέση με qwen3:8b {sorted(REF_8B)}: επιπλέον {sorted(solved - REF_8B)}, χάνει {sorted(REF_8B - solved)}")
