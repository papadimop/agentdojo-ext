"""Τρέξιμο banking από Python, χωρίς το CLI. Χρήση (από τον φάκελο του repo, PYTHONPATH=.):

  python run_bench.py --logdir runs/X --ut 3 13 --benign
  python run_bench.py --logdir runs/X --ut 3 13 --it asi01 --attack important_instructions
  python run_bench.py --logdir runs/X --ut 3 13 --it llm06 --defense count_limit
  python run_bench.py --logdir runs/X --direct --it llm06 --defense guard2   (επιθέσεις ως απευθείας αιτήματα)

Διαφορές από το CLI:
- ΔΕΝ τρέχει τις επιθέσεις ως απευθείας αιτήματα (το CLI το κάνει σε κάθε εκκίνηση).
- Δέχεται και την άμυνα count_limit (κανόνας κώδικα) και διορθώνει το tool_filter.
- Δύο διεργασίες μπορούν να τρέχουν παράλληλα στο ίδιο logdir με διαφορετικά user tasks.
Ίδια logs με το CLI: <logdir>/<pipeline>/banking/<user_task>/<attack>/<injection_task>.json
Απευθείας αιτήματα (--direct): <logdir>/<pipeline>/banking/<injection_task>/none/none.json, όπως το CLI·
εκεί το utility είναι το security_from_traces του injection task (ζητηθείσες κλήσεις).
Επεισόδια που υπάρχουν ήδη στο logdir δεν ξανατρέχουν.
"""
import argparse
import time
import traceback
from pathlib import Path

import ext_llm06  # καταχωρεί τα injection tasks 100-103 (και φέρνει πρώτο το load_suites)
from agentdojo.attacks.attack_registry import load_attack
from agentdojo.benchmark import run_task_with_injection_tasks, run_task_without_injection_tasks
from agentdojo.logging import OutputLogger

from defenses import BUILTIN, OWN, build_pipeline

GROUPS = {
    "asi01": [f"injection_task_{i}" for i in range(9)],
    "llm06": ["injection_task_100", "injection_task_101", "injection_task_102", "injection_task_103"],
}

p = argparse.ArgumentParser()
p.add_argument("--logdir", required=True)
p.add_argument("--ut", nargs="+", default=[], help="αριθμοί user tasks, π.χ. 3 13")
p.add_argument("--benign", action="store_true", help="χωρίς επίθεση")
p.add_argument("--it", nargs="+", default=[], help="asi01, llm06 ή injection_task_X")
p.add_argument("--attack", default="important_instructions")
p.add_argument("--direct", action="store_true", help="τα injection tasks του --it ως αιτήματα του χρήστη")
p.add_argument("--defense", default="none", choices=[*OWN, *BUILTIN])
p.add_argument("--agent-model", default=None, help="ρητό μοντέλο Ollama για τον agent (αλλιώς το πρώτο του /v1/models)")
p.add_argument("--guard-model", default=None, help="ρητό μοντέλο Ollama για τους guards (αλλιώς ίδιο με τον agent)")
a = p.parse_args()
if not a.ut and not a.direct:
    p.error("χρειάζεται --ut ή --direct")

suite = ext_llm06.suite
pipeline = build_pipeline(a.defense, agent_model=a.agent_model, guard_model=a.guard_model)
logdir = Path(a.logdir)
its = [x for g in a.it for x in GROUPS.get(g, [g])]
attack = None if (a.benign or a.direct) else load_attack(a.attack, suite, pipeline)
print(f"pipeline={pipeline.name} agent={pipeline.agent_model} user_tasks={a.ut} benign={a.benign} attack={a.attack} its={its}", flush=True)

with OutputLogger(str(logdir)):
    if a.direct:
        for it_id in its:
            t0 = time.time()
            try:
                ok, _ = run_task_without_injection_tasks(suite, pipeline, suite.get_injection_task_by_id(it_id),
                                                         logdir, False, "v1.2.2")
                print(f"{it_id} direct utility={ok} ({time.time() - t0:.0f}s)", flush=True)
            except Exception:
                print(f"{it_id} ΣΦΑΛΜΑ:\n{traceback.format_exc()}", flush=True)
    for u in a.ut:
        ut = suite.get_user_task_by_id(f"user_task_{u}")
        t0 = time.time()
        try:
            if a.benign:
                util, _ = run_task_without_injection_tasks(suite, pipeline, ut, logdir, False, "v1.2.2")
                print(f"{ut.ID} benign utility={util} ({time.time() - t0:.0f}s)", flush=True)
            else:
                util, sec = run_task_with_injection_tasks(suite, pipeline, ut, attack, logdir, False, its, "v1.2.2")
                print(f"{ut.ID} επιτυχίες επίθεσης={sum(sec.values())}/{len(sec)} "
                      f"utility={sum(util.values())}/{len(util)} ({time.time() - t0:.0f}s)", flush=True)
        except Exception:  # ένα χαλασμένο user task δεν σταματά τα υπόλοιπα
            print(f"{ut.ID} ΣΦΑΛΜΑ:\n{traceback.format_exc()}", flush=True)
print("ΤΕΛΟΣ", flush=True)
