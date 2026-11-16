"""Runner δύο sessions για το ASI06 με ΠΡΑΓΜΑΤΙΚΟ μοντέλο (Kaggle, Ollama, LOCAL_LLM_PORT=11434).

Χρήση: python two_session_live.py <session1_user_task_id> [defense]
Γράφει τα αποτελέσματα σε asi06_results.jsonl
"""
import json
import sys

import ext_asi06 as m
from agentdojo.agent_pipeline.agent_pipeline import AgentPipeline, PipelineConfig
from agentdojo.attacks.attack_registry import load_attack

ut1_id = sys.argv[1]
defense = sys.argv[2] if len(sys.argv) > 2 else None
suite = m.suite

pipeline = AgentPipeline.from_config(PipelineConfig(
    llm="vllm_parsed", model_id=None, defense=defense,
    system_message_name=None, system_message=m.MEMORY_SYSTEM_MESSAGE))

ut1 = suite.get_user_task_by_id(ut1_id)
it_write = suite.get_injection_task_by_id("injection_task_101")
ut2 = suite.get_user_task_by_id("user_task_100")
it_exec = suite.get_injection_task_by_id("injection_task_102")

injections = load_attack("important_instructions", suite, pipeline).attack(ut1, it_write)

env = suite.load_and_inject_default_environment(injections)
env.cloud_drive.create_file(m.MEMORY_FILE, m.MEMORY_INIT)   # αρχική, σωστή μνήμη

u1, write_ok = suite.run_task_with_pipeline(pipeline, ut1, it_write, injections, environment=env)
u2, exec_ok = suite.run_task_with_pipeline(pipeline, ut2, it_exec, {}, environment=env)  # ΙΔΙΟ env

row = {"session1_task": ut1_id, "defense": defense, "s1_utility": u1, "write": write_ok,
       "s2_utility": u2, "execution": exec_ok, "memory_after": m.memory_file(env).content}
print(row)
with open("asi06_results.jsonl", "a") as f:
    f.write(json.dumps(row) + "\n")
