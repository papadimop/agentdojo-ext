"""Ανάλυση των logs του LLM06 (banking). Χρήση: python analyze_llm06.py <runs_root> [out.csv]

Διαβάζει όλα τα JSON κάτω από το <runs_root> (π.χ. runs/rep1, runs/rep2, ...) και τυπώνει,
ανά injection task και ανά σύνολο user tasks:
  ASR (security), stealthy ASR (security και utility), utility υπό επίθεση,
  ΔCalls έναντι benign (ίδιο user task, ίδια επανάληψη), cap hits, επεισόδια με σφάλμα.
Το security υπολογίζεται δύο φορές: από τις κλήσεις που ΖΗΤΗΣΕ το μοντέλο (όπως το AgentDojo)
και από όσες ΕΚΤΕΛΕΣΤΗΚΑΝ (διαφέρουν μόνο όταν μια άμυνα μπλοκάρει κλήσεις).
"""
import csv
import glob
import json
import os
import sys
from statistics import mean

import ext_llm06
from agentdojo.functions_runtime import FunctionCall

SUITE = ext_llm06.suite
ATTACK_IDS = ["injection_task_100", "injection_task_101", "injection_task_102", "injection_task_103"]
CLEAN = {"user_task_2", "user_task_12", "user_task_13"}  # vectors με κενό default


def episode(path: str) -> dict:
    d = json.load(open(path))
    msgs = d["messages"]
    requested = [FunctionCall(function=tc["function"], args=tc.get("args") or {})
                 for m in msgs if m["role"] == "assistant" for tc in (m.get("tool_calls") or [])]
    executed = [FunctionCall(function=m["tool_call"]["function"], args=m["tool_call"].get("args") or {})
                for m in msgs if m["role"] == "tool" and m.get("error") is None]
    last = msgs[-1] if msgs else {}
    cap_hit = last.get("role") == "assistant" and bool(last.get("tool_calls"))
    it_id = d["injection_task_id"]
    sec_exec = None
    if it_id in SUITE.injection_tasks:
        sec_exec = SUITE.injection_tasks[it_id].security_from_traces("", None, None, executed)
    rep = os.path.relpath(path, ROOT).split(os.sep)[0]
    return {
        "rep": rep, "user_task": d["user_task_id"], "injection_task": it_id or "none",
        "attack": d.get("attack_type") or "none", "utility": d.get("utility"),
        "security": d.get("security") if it_id else None,  # χωρίς επίθεση το security δεν έχει νόημα
        "security_executed": sec_exec, "n_requested": len(requested), "n_executed": len(executed),
        "cap_hit": cap_hit, "error": d.get("error") is not None, "duration": d.get("duration") or 0.0,
        "steps": sum(m["role"] == "assistant" for m in msgs),
    }


def pct(xs):
    return f"{100 * mean(xs):5.1f}%" if xs else "   - "


if __name__ == "__main__":
    ROOT = sys.argv[1]
    out_csv = sys.argv[2] if len(sys.argv) > 2 else None
    rows = [episode(p) for p in sorted(glob.glob(f"{ROOT}/**/banking/user_task_*/*/*.json", recursive=True))]
    benign = {(r["rep"], r["user_task"]): r for r in rows if r["attack"] == "none"}
    attacked = [r for r in rows if r["injection_task"] in ATTACK_IDS]
    for r in attacked:
        b = benign.get((r["rep"], r["user_task"]))
        r["delta_calls"] = r["n_requested"] - b["n_requested"] if b else None
        r["benign_utility"] = b["utility"] if b else None

    print(f"Επεισόδια: benign {len(benign)}, υπό επίθεση {len(attacked)}, "
          f"με σφάλμα {sum(r['error'] for r in rows)} (μετρούν utility False / security True)")
    print(f"Benign utility: {pct([r['utility'] for r in benign.values()])}  "
          f"({sum(r['utility'] for r in benign.values())}/{len(benign)})\n")

    subsets = {
        "πλήρες": lambda r: True,
        "καθαρό (2,12,13)": lambda r: r["user_task"] in CLEAN,
        "λύνει benign": lambda r: r["benign_utility"] is True,
    }
    hdr = f"{'injection task':20} {'σύνολο':18} {'N':>4} {'ASR':>7} {'ASR exec':>9} {'stealthy':>9} {'util':>7} {'ΔCalls':>7} {'cap':>4} {'err':>4} {'sec/ep':>7}"
    print(hdr); print("-" * len(hdr))
    for it in ATTACK_IDS:
        for name, f in subsets.items():
            rs = [r for r in attacked if r["injection_task"] == it and f(r)]
            if not rs:
                continue
            dc = [r["delta_calls"] for r in rs if r["delta_calls"] is not None]
            print(f"{it:20} {name:18} {len(rs):4} {pct([r['security'] for r in rs]):>7} "
                  f"{pct([r['security_executed'] for r in rs]):>9} "
                  f"{pct([r['security'] and r['utility'] for r in rs]):>9} {pct([r['utility'] for r in rs]):>7} "
                  f"{(f'{mean(dc):+.1f}' if dc else '-'):>7} {sum(r['cap_hit'] for r in rs):4} "
                  f"{sum(r['error'] for r in rs):4} {mean(r['duration'] for r in rs):7.1f}")
        print()

    if out_csv:
        keys = list(attacked[0].keys()) if attacked else list(rows[0].keys())
        with open(out_csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            w.writerows(attacked + list(benign.values()))
        print("CSV:", out_csv)
