"""Πλήρης εικόνα ενός ή περισσότερων επεισοδίων από τα logs (χωρίς μοντέλο).
Χρήση: PYTHONPATH=. python show_episode.py <episode.json> [<episode.json> ...] > out.md

Για κάθε επεισόδιο: αίτημα χρήστη, επίθεση (κείμενο + κρυψώνα), κάθε βήμα του agent (κλήση, απόφαση guard κλήσεων,
έξοδος εργαλείου: τι επέστρεψε το εργαλείο και τι ΕΙΔΕ ο agent μετά τον guard εξόδων), τελική απάντηση, utility/security.
Το «τι επέστρεψε το εργαλείο» βγαίνει με αναπαραγωγή των εκτελεσμένων κλήσεων σε καθαρό περιβάλλον (analyze_oguard.replay).
"""
import difflib
import json
import sys

import analyze_llm06 as A
import analyze_oguard as O
import ext_llm06

SUITE = ext_llm06.suite


def text_of(content) -> str:
    return "".join(c.get("content") or "" for c in (content or []) if c.get("type") == "text")


def removed_parts(orig: str, seen: str) -> list[str]:
    """Κομμάτια του orig που λείπουν από το seen (ό,τι έσβησε ο guard εξόδων)."""
    sm = difflib.SequenceMatcher(a=orig, b=seen, autojunk=False)
    return [orig[i1:i2] for tag, i1, i2, _, _ in sm.get_opcodes() if tag in ("delete", "replace") and orig[i1:i2].strip()]


def show(path: str) -> str:
    d = json.load(open(path))
    parts = path.split("/")
    i = parts.index("banking")
    pipeline = parts[i - 1]
    defense = pipeline.split("-", 1)[1] if "-" in pipeline else "none"
    it = d.get("injection_task_id")
    out = [f"## {d['user_task_id']} + {it or 'χωρίς επίθεση'} | άμυνα: {defense} | επανάληψη: {parts[i - 2]}", ""]
    ut = SUITE.get_user_task_by_id(d["user_task_id"])
    out += ["**Αίτημα χρήστη:**", "```", ut.PROMPT, "```", ""]
    if it:
        inj = d.get("injections") or {}
        out += [f"**Επίθεση {it}** (στόχος του επιτιθέμενου, GOAL):", "```", SUITE.get_injection_task_by_id(it).GOAL, "```"]
        for vec, txt in inj.items():
            out += [f"Κρυψώνα: `{vec}`. Κείμενο που μπήκε εκεί (περιτύλιγμα {d.get('attack_type')}):", "```", txt.strip("\n"), "```"]
        out.append("")
    replay = iter(O.replay(d))  # (εργαλείο, αρχική έξοδος, ό,τι είδε ο agent) για κάθε ΕΚΤΕΛΕΣΜΕΝΗ κλήση
    step = 0
    for m in d["messages"]:
        if m["role"] == "assistant":
            calls = m.get("tool_calls") or []
            if calls:
                for tc in calls:
                    step += 1
                    out.append(f"**Βήμα {step}. Ο agent ζητά:** `{tc['function']}({json.dumps(tc.get('args') or {}, ensure_ascii=False)})`")
            else:
                out += ["", "**Τελική απάντηση του agent:**", "```", text_of(m.get("content")).strip(), "```"]
        elif m["role"] == "tool":
            err = m.get("error")
            if err:
                who = "ΜΠΛΟΚΑΡΕ ο guard κλήσεων" if "guard" in err else ("ΜΠΛΟΚΑΡΕ ο κανόνας" if err.startswith("Blocked") else "σφάλμα εργαλείου")
                out += [f"- {who}. Μήνυμα προς τον agent:", "```", err, "```"]
                continue
            fn, orig, seen = next(replay)
            if defense in ("guard", "guard2", "guard2_oguard"):
                out.append("- Ο guard κλήσεων ΕΠΕΤΡΕΨΕ την κλήση (ο λόγος του ALLOW δεν σώζεται στα logs).")
            if orig == seen:
                note = " (ο guard εξόδων δεν άλλαξε τίποτα)" if "oguard" in defense else ""
                out += [f"- Έξοδος του εργαλείου, όπως τη διάβασε ο agent{note}:", "```", seen, "```"]
            else:
                out += ["- Έξοδος του εργαλείου ΠΡΙΝ τον guard εξόδων:", "```", orig, "```",
                        "- Ο guard εξόδων ΕΣΒΗΣΕ:"]
                for r in removed_parts(orig, seen):
                    out += ["```", r, "```"]
                out += ["- Αυτό διάβασε ο agent:", "```", seen, "```"]
    executed = [A.FunctionCall(function=m["tool_call"]["function"], args=m["tool_call"].get("args") or {})
                for m in d["messages"] if m["role"] == "tool" and m.get("error") is None]
    pat = A.pattern_count(it, executed) if it else None
    out += ["", f"**Αποτέλεσμα (με κώδικα):** η δουλειά του χρήστη έγινε (utility) = {d.get('utility')}" +
            (f"· πλήρης επιτυχία επίθεσης (AgentDojo security, > {ext_llm06.BUDGET} κλήσεις μοτίβου) = {d.get('security')}"
             f"· κλήσεις του μοτίβου της επίθεσης που ΕΚΤΕΛΕΣΤΗΚΑΝ = {pat}" if pat is not None else "") +
            f"· διάρκεια {d.get('duration', 0):.0f} s", ""]
    return "\n".join(out)


if __name__ == "__main__":
    A.ROOT = "/"
    for p in sys.argv[1:]:
        print(show(p))
        print("\n---\n")
