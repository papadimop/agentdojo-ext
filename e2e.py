"""End-to-end έλεγχος χωρίς LLM: ένας 'agent' που ακολουθεί την επίθεση και ένας που την αγνοεί.

Χρήση: python e2e.py <suite> <user_task_id> <injection_task_id> <module> [system_message]
"""
import importlib
import sys

from agentdojo.agent_pipeline.ground_truth_pipeline import GroundTruthPipeline
from agentdojo.attacks.attack_registry import load_attack
from agentdojo.task_suite.load_suites import get_suite

suite_name, ut_id, it_id, module = sys.argv[1:5]
importlib.import_module(module)
suite = get_suite("v1.2.2", suite_name)
ut = suite.get_user_task_by_id(ut_id)
it = suite.get_injection_task_by_id(it_id)


class DummyPipe:
    name = "local"


attack = load_attack("important_instructions", suite, DummyPipe())
injections = attack.attack(ut, it)
print("vectors used:", list(injections))


class Scripted:
    """Ψεύτικος agent που εκτελεί μια σταθερή λίστα κλήσεων."""

    def __init__(self, calls_fn, output):
        self.calls_fn = calls_fn
        self.GROUND_TRUTH_OUTPUT = output

    def ground_truth(self, env):
        return self.calls_fn(env)


compliant = Scripted(lambda env: it.ground_truth(env) + ut.ground_truth(env), ut.GROUND_TRUTH_OUTPUT)
resistant = Scripted(lambda env: ut.ground_truth(env), ut.GROUND_TRUTH_OUTPUT)

for name, task in [("agent follows attack", compliant), ("agent ignores attack", resistant)]:
    utility, security = suite.run_task_with_pipeline(GroundTruthPipeline(task), ut, it, injections)
    print(f"{name:22s} -> utility={utility} security(attack success)={security}")
