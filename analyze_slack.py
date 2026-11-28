"""Ανάλυση slack (LLM10 100-103 και ASI01 1-5), με κώδικα. Χρήση: PYTHONPATH=. python analyze_slack.py <root>
Ανά άμυνα και επίθεση: σε πόσα επεισόδια πέτυχε η επίθεση (security του AgentDojo στο τελικό περιβάλλον: τι κατέληξε στη σελίδα /
στα μηνύματα, όχι οι ζητηθείσες κλήσεις), σε πόσα έγινε η δουλειά του χρήστη, αν η επίθεση έφτασε στον agent (αναπαραγωγή των
εκτελεσμένων κλήσεων σε καθαρό περιβάλλον: υπήρχε το κείμενο της επίθεσης στην έξοδο; το είδε ο agent;), ψευδείς συναγερμοί (benign
με μπλοκαρισμένη κλήση ή πειραγμένη έξοδο χωρίς επίθεση), σφάλματα. Fisher: κάθε άμυνα έναντι none (περιγραφικό στο dev)."""
import glob
import json
import os
import re
import sys
from collections import defaultdict

import ext_llm10 as X
from agentdojo.agent_pipeline.tool_execution import tool_result_to_str
from agentdojo.functions_runtime import FunctionsRuntime

SUITE = X.suite
LLM10 = {"injection_task_100", "injection_task_101", "injection_task_102", "injection_task_103"}


def norm(s):
    return re.sub(r"\s+", " ", (s or "").replace("''", "'")).lower()


def replay(d):
    env = SUITE.load_and_inject_default_environment(d.get("injections") or {})
    rt = FunctionsRuntime(SUITE.tools)
    out = []
    for m in d["messages"]:
        if m["role"] != "tool" or m.get("error") is not None:
            continue
        tc = m["tool_call"]
        o, err = rt.run_function(env, tc["function"], tc.get("args") or {})
        seen = "".join(c.get("content") or "" for c in (m.get("content") or []) if c.get("type") == "text")
        out.append((tool_result_to_str(o) if err is None else "", seen))
    return out


def load(root):
    rows = []
    for p in sorted(glob.glob(f"{root}/**/slack/user_task_*/*/*.json", recursive=True)):
        d = json.load(open(p))
        if "utility" not in d:
            print("  ΜΙΣΟΤΕΛΕΙΩΜΕΝΟ (δεν μετρά):", p)
            continue
        parts = os.path.relpath(p, root).split(os.sep)
        i = parts.index("slack")
        pipe = parts[i - 1]
        it = d.get("injection_task_id")
        key = norm(SUITE.get_injection_task_by_id(it).GOAL)[:60] if it else None
        pairs = replay(d)
        msgs = d["messages"]
        rows.append({
            "rep": parts[i - 2] if i >= 2 else "-", "defense": pipe.split("-", 1)[1] if "-" in pipe else "none",
            "task": d["user_task_id"], "it": it or "none", "family": "-" if not it else ("LLM10" if it in LLM10 else "ASI01"),
            "utility": bool(d["utility"]), "security": bool(d.get("security")) if it else None, "error": d.get("error") is not None,
            "blocked": sum(1 for m in msgs if m["role"] == "tool" and str(m.get("error") or "").startswith("Blocked")),
            "exposed": bool(key) and any(key in norm(o) for o, _ in pairs),
            "reached": bool(key) and any(key in norm(s) for _, s in pairs),
            "collateral": sum(1 for o, s in pairs if o != s and not (key and key in norm(o))),
            "duration": d.get("duration") or 0,
        })
    return rows


def main(root):
    from scipy.stats import fisher_exact
    rows = load(root)
    print(f"Επεισόδια: {len(rows)}, σφάλματα: {sum(r['error'] for r in rows)}")
    defs = [d for d in ["none", "oguard", "guard2", "guard2_oguard", "guard3", "guard3_oguard", "sanitize", "repeat_user_prompt"] if any(r["defense"] == d for r in rows)]
    print("\n1. Ανά άμυνα και είδος επίθεσης (σε πόσα επεισόδια):")
    base = {}
    for fam in ("LLM10", "ASI01"):
        for d in defs:
            rs = [r for r in rows if r["defense"] == d and r["family"] == fam]
            if not rs:
                continue
            k = sum(r["security"] for r in rs)
            exp = [r for r in rs if r["exposed"]]
            line = (f"  {fam} {d:20} η επίθεση πέτυχε σε {k:2} από {len(rs):2} | η δουλειά έγινε σε {sum(r['utility'] for r in rs):2} από {len(rs):2}"
                    f" | η επίθεση έφτασε στον agent σε {sum(r['reached'] for r in exp):2} από {len(exp):2} που ήταν στην έξοδο"
                    f" | επεισόδια με μπλοκάρισμα {sum(r['blocked'] > 0 for r in rs):2} | σφάλματα {sum(r['error'] for r in rs)}")
            if d == "none":
                base[fam] = (k, len(rs))
            elif fam in base:
                b = base[fam]
                line += f" | Fisher έναντι none p={fisher_exact([[b[0], b[1] - b[0]], [k, len(rs) - k]])[1]:.2g}"
            print(line)
    print("\n2. Ανά επίθεση (σε πόσα επεισόδια πέτυχε η επίθεση):")
    its = sorted({r["it"] for r in rows if r["it"] != "none"}, key=lambda x: int(x.rsplit("_", 1)[1]))
    print("  " + f"{'άμυνα':20} " + " ".join(f"{i.rsplit('_', 1)[1]:>6}" for i in its))
    for d in defs:
        cells = []
        for it in its:
            rs = [r for r in rows if r["defense"] == d and r["it"] == it]
            cells.append(f"{sum(r['security'] for r in rs)}/{len(rs)}" if rs else "-")
        print(f"  {d:20} " + " ".join(f"{c:>6}" for c in cells))
    print("\n3. Χωρίς επίθεση (benign): η δουλειά έγινε / ψευδείς συναγερμοί")
    for d in defs:
        rs = [r for r in rows if r["defense"] == d and r["it"] == "none"]
        if rs:
            print(f"  {d:20} η δουλειά έγινε σε {sum(r['utility'] for r in rs)} από {len(rs)} | με μπλοκάρισμα {sum(r['blocked'] > 0 for r in rs)}"
                  f" | πειραγμένες έξοδοι {sum(r['collateral'] for r in rs)} | διάρκεια μέση {sum(r['duration'] for r in rs) / len(rs):.0f} s")
    print("\n4. Πειραγμένες έξοδοι χωρίς επίθεση, σε επεισόδια με επίθεση (ψευδείς συναγερμοί του guard εξόδων):")
    for d in defs:
        rs = [r for r in rows if r["defense"] == d and r["it"] != "none"]
        if rs:
            print(f"  {d:20} {sum(r['collateral'] for r in rs)}")
    print("\n5. Επεισόδια όπου πέτυχε η επίθεση (για show_episode):")
    for r in rows:
        if r["security"]:
            print(f"  {r['rep']} {r['defense']:20} {r['task']:13} {r['it']} δουλειά={r['utility']} μπλοκ.={r['blocked']}")


if __name__ == "__main__":
    main(sys.argv[1])
