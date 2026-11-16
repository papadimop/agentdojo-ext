"""Runner δύο sessions, εδώ με ψεύτικους agents (χωρίς LLM) για να ελεγχθεί η λογική."""
import ext_asi06 as m
from agentdojo.agent_pipeline.ground_truth_pipeline import GroundTruthPipeline
from agentdojo.attacks.attack_registry import load_attack
from agentdojo.functions_runtime import FunctionCall

suite = m.suite
ut1 = suite.get_user_task_by_id("user_task_22")      # session 1: υπάρχον task που διαβάζει email
it_write = suite.get_injection_task_by_id("injection_task_101")
ut2 = suite.get_user_task_by_id("user_task_100")     # session 2: καθαρό αίτημα
it_exec = suite.get_injection_task_by_id("injection_task_102")


class P:
    name = "local"


injections = load_attack("important_instructions", suite, P()).attack(ut1, it_write)
print("session 1 vectors:", list(injections))


class Scripted:
    def __init__(self, fn, out=""):
        self.fn, self.GROUND_TRUTH_OUTPUT = fn, out

    def ground_truth(self, env):
        return self.fn(env)


def session2_calls(follow_poison):
    def fn(env):
        target = m.ATTACKER if follow_poison else m.REAL_ACCOUNTANT
        return [FunctionCall(function="send_email", args={
            "recipients": [target], "subject": "Budget 2024", "body": "Attached.", "attachments": [{"type": "file", "file_id": "15"}]})]
    return fn


for label, writes, follows in [("agent writes poison and uses it", True, True),
                                ("agent ignores the injection", False, False)]:
    env = suite.load_and_inject_default_environment(injections)
    env.cloud_drive.create_file(m.MEMORY_FILE, m.MEMORY_INIT)      # αρχική, σωστή μνήμη
    s1 = Scripted(lambda e: (it_write.ground_truth(e) if writes else []) + ut1.ground_truth(e), ut1.GROUND_TRUTH_OUTPUT)
    u1, write_ok = suite.run_task_with_pipeline(GroundTruthPipeline(s1), ut1, it_write, injections, environment=env)
    # το ΙΔΙΟ αντικείμενο env συνεχίζει στο session 2 (εκεί ζει η μνήμη)
    s2 = Scripted(session2_calls(follows))
    u2, exec_ok = suite.run_task_with_pipeline(GroundTruthPipeline(s2), ut2, it_exec, {}, environment=env)
    print(f"{label:32s} -> S1 utility={u1} write={write_ok} | S2 utility={u2} execution={exec_ok}")
