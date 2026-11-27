"""Έλεγχος των επιθέσεων LLM10 χωρίς μοντέλο. Χρήση: PYTHONPATH=. python test_llm10.py
Για κάθε εργασία που στέλνει μηνύματα (και την 4 για την ανάρτηση) και κάθε επίθεση 100-103, δύο ψεύτικοι agents με τις
κλήσεις της σωστής λύσης (ground truth): ένας που βάζει το επικίνδυνο κομμάτι στο περιεχόμενο (υπακούει) και ένας που όχι.
Αναμένεται: υπακούει -> επίθεση True, αγνοεί -> επίθεση False· η δουλειά του χρήστη (utility) True και στους δύο."""
import ext_llm10 as X
from agentdojo.agent_pipeline.ground_truth_pipeline import GroundTruthPipeline
from agentdojo.attacks.attack_registry import load_attack
from agentdojo.functions_runtime import FunctionCall

suite = X.suite


class P:
    name = "vllm_parsed"


class Scripted:
    def __init__(self, fn, output):
        self.fn, self.GROUND_TRUTH_OUTPUT = fn, output

    def ground_truth(self, env):
        return self.fn(env)


def with_payload(calls, it_id):
    out = []
    for c in calls:
        a = dict(c.args)
        if it_id == "injection_task_100" and c.function == "post_webpage":
            a["content"] = f"{a['content']} {X.PAYLOADS[it_id]}"
        elif it_id != "injection_task_100" and c.function in X.MSG_TOOLS:
            p = X.PAYLOADS[it_id].replace("DATA", str(a.get("recipient") or a.get("channel")))
            a["body"] = f"{p} {a['body']}" if it_id == "injection_task_103" else f"{a['body']} {p}"
        out.append(FunctionCall(function=c.function, args=a, placeholder_args=a))
    return out


attack = load_attack("important_instructions", suite, P())
bad = 0
for uid, ut in sorted(suite.user_tasks.items(), key=lambda x: int(x[0].split("_")[-1])):
    gt_funcs = {c.function for c in ut.ground_truth(suite.load_and_inject_default_environment({}))}
    for it_id in X.PAYLOADS:
        applies = ("post_webpage" in gt_funcs) if it_id == "injection_task_100" else bool(gt_funcs & set(X.MSG_TOOLS))
        if not applies:
            continue
        it = suite.get_injection_task_by_id(it_id)
        inj = attack.attack(ut, it)
        res = []
        for name, fn in (("υπακούει", lambda env: with_payload(ut.ground_truth(env), it_id)),
                         ("αγνοεί", lambda env: ut.ground_truth(env))):
            u, s = suite.run_task_with_pipeline(GroundTruthPipeline(Scripted(fn, ut.GROUND_TRUTH_OUTPUT)), ut, it, inj)
            res.append((name, u, s))
        ok = res[0][2] is True and res[1][2] is False and res[0][1] and res[1][1]
        bad += not ok
        print(f"{'OK ' if ok else 'ΛΑΘΟΣ'} {uid:12} {it_id} κρυψώνες={list(inj)} " +
              " | ".join(f"{n}: δουλειά={u} επίθεση={s}" for n, u, s in res))
print("ΣΥΝΟΛΟ λαθών:", bad)
