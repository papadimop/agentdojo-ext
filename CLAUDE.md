# Διπλωματική: επέκταση AgentDojo + ενδιάμεσος agent (οδηγίες για Claude)

## Ποιος είμαι και πώς θέλω καθοδήγηση
- Σταύρος, φοιτητής ΗΜΜΥ ΑΠΘ. Ελληνικά, τεχνικοί όροι στα αγγλικά.
- Κάθε έννοια την πρώτη φορά: πρώτα απλά λόγια ή αναλογία, μετά τεχνικά.
- Ένα βήμα τη φορά: τι κάνει κάθε γραμμή, πού σώζεται το αρχείο, από ποιον φάκελο τρέχει η εντολή. Στο Kaggle πολύ αναλυτικά (κελί-κελί).
- Όχι ερωτήσεις κατανόησης στο τέλος. Στο τέλος 2-3 "Σημειώσεις" και σύντομο "Συμπέρασμα".
- Μόνο επαληθευμένα στοιχεία. Ό,τι είναι υπόθεση να λέγεται ρητά. Αδυναμίες ευθέως.
- Η μέτρηση γίνεται ΠΑΝΤΑ με κώδικα (utility/security του AgentDojo), ποτέ με LLM judge.

## Το θέμα (εγκρίθηκε από τον επιβλέποντα 16/11/2026)
Συνδυασμός:
1. Επέκταση AgentDojo με 3 κατηγορίες OWASP που λείπουν: LLM06:2026/ASI02 (loop amplification, banking), LLM10:2026 Improper Output Handling (slack), ASI06 Memory Poisoning σε δύο sessions (workspace). Οι επιθέσεις αυτές είναι το test set.
2. Ενδιάμεσος agent (guard) με τοπικό LLM + RAG που ελέγχει (α) τις εξόδους των εργαλείων (ιδέα PromptArmor) και (β) κάθε κλήση εργαλείου πριν εκτελεστεί, με βάση το αίτημα του χρήστη (ιδέα LlamaFirewall AlignmentCheck).
3. Μέτρηση σε παλιές (ASI01) και νέες επιθέσεις: καμία άμυνα -> 4 έτοιμες άμυνες -> απλός κανόνας κώδικα -> ενδιάμεσος agent χωρίς RAG -> με RAG.
- RAG: πραγματικά κείμενα επιθέσεων. Μέρος των ειδών επίθεσης του AgentDojo στο RAG, εξέταση στα υπόλοιπα (όχι τα ίδια κείμενα σε RAG και εξέταση). Εξωτερικά datasets (BIPIA, deepset/prompt-injections) για σύγκριση. MITRE ATLAS/OWASP μόνο για ετικέτες.

## Περιβάλλον
- agentdojo==0.1.35 (benchmark v1.2.2). Python 3.13.
- Laptop: Windows, VS Code, PowerShell, venv redteam-env, 6 GB RAM (χωρίς μεγάλα μοντέλα, μόνο κώδικας και check_suites).
- Kaggle: T4 x2, Ollama, μοντέλα έως 14B (qwen3:8b επαληθευμένο). Κάθε session ξεκινά άδειο. Χωρίς API keys.

## Επαληθευμένα στοιχεία (μην τα ξαναψάχνεις)
- Τρέξιμο με Ollama: `LOCAL_LLM_PORT=11434`, `--model VLLM_PARSED` (κεφαλαία). qwen3:8b benign banking 8/16 (περνούν 0,3,5,6,7,8,13,14), ~1 λεπτό/task.
- Νέα tasks: εγγραφή σε `get_suite("v1.2.2", "<suite>")`, το import `from agentdojo.task_suite.load_suites import get_suite` ΠΡΩΤΟ (αλλιώς circular import). Φόρτωση με `-ml <module>`, `PYTHONPATH=.`.
- ID από όνομα κλάσης: InjectionTask100 -> injection_task_100.
- Έλεγχος χωρίς μοντέλο: `python -m agentdojo.scripts.check_suites -v v1.2.2 -s <suite> -ml <module> --no-check-injectable`.
- Η επίθεση ΑΝΤΙΚΑΘΙΣΤΑ το default κείμενο του injection vector. Χρησιμοποιούμε vectors με κενό default: banking injection_address_change (user_task_13), injection_landloard_notice (2/12), slack prompt_injection_eve_blog (user_task_4).
- GOAL χωρίς διπλά εισαγωγικά (σπάει το YAML).
- send_email attachments: `[{"type": "file", "file_id": "15"}]`.
- post_webpage αντικαθιστά το περιεχόμενο (μετρά η τελευταία ανάρτηση).
- Workspace: πολλά read-only user tasks ελέγχουν pre_environment == post_environment, άρα εγγραφή μνήμης στο S1 τα κάνει utility False.
- `run_task_with_pipeline(..., environment=env)` δέχεται έτοιμο env και το αλλάζει in place (βάση του runner δύο sessions).
- Άμυνες: `DEFENSES` = tool_filter, transformers_pi_detector, spotlighting_with_delimiting, repeat_user_prompt. Το CLI `--defense` δέχεται μόνο αυτά. Δικές μας άμυνες τρέχουν από Python (`benchmark_suite_with_injections`), το pipeline.name πρέπει να περιέχει γνωστό key.
- Σημείο για guard στις εξόδους: υποκλάση `PromptInjectionDetector` (agent_pipeline/pi_detector.py) με `detect(tool_output)`. Σημείο πριν την κλήση: δεν υπάρχει hook, υποκλάση του `ToolsExecutor` (agent_pipeline/tool_execution.py) με έλεγχο πριν το `runtime.run_function`.
- ΠΑΓΙΔΑ: το `security_from_traces` διαβάζει τις κλήσεις που ΖΗΤΗΣΕ το LLM, όχι όσες εκτελέστηκαν. Με άμυνα που μπλοκάρει, για το LLM06 μετράμε εκτελεσμένες κλήσεις.
- ΠΑΓΙΔΑ: σφάλμα API/context στο benchmark γράφεται utility False, security True. Μετράμε και αναφέρουμε πόσα επεισόδια απέτυχαν από σφάλμα.
- `VLLM_PARSED` παίρνει το ΠΡΩΤΟ μοντέλο του `/v1/models` (`_get_local_model_id`) και αγνοεί το `--model-id`. Στο Ollama να υπάρχει ένα μοντέλο όταν τρέχει το CLI. Agent + guard με δύο μοντέλα: μόνο από Python με ρητό όνομα μοντέλου.
- Θερμοκρασία: `openai_llm.py` στέλνει `temperature or NOT_GIVEN`, άρα το 0.0 ΔΕΝ στέλνεται και ισχύει το default του Ollama/μοντέλου (μη ντετερμινιστικό).
- qwen3:8b (Ollama, Q4_K_M) defaults: temperature 0.6, top_p 0.95, top_k 20, thinking ενεργό. ~10 GB στη GPU με context 32768.
- Το CLI με `--attack` τρέχει επιπλέον το injection task ως user task (`<suite>/injection_task_X/none/none.json`).
- Logs: `<logdir>/vllm_parsed/<suite>/<user_task>/<attack>/<injection_task>.json`. Ζητηθείσες κλήσεις: `tool_calls` των assistant μηνυμάτων. Εκτελεσμένες: μηνύματα `role=tool` (πεδίο `tool_call`, `error`). Για JSON από Python χρειάζεται `OutputLogger(logdir)` γύρω από το τρέξιμο.
- Banking: και τα 16 user tasks φτάνουν σε injection vector. Κενό default μόνο σε `injection_address_change`, `injection_landloard_notice` (user tasks 2, 12, 13). Το `injection_bill_text` έχει ως default το περιεχόμενο του λογαριασμού.
- Upstream: workspace injection_task_6-13 αποτυγχάνουν στο δικό τους check_suites.

## Αρχεία
- ext_llm06.py, ext_llm10.py, ext_asi06.py: οι επιθέσεις (ελεγμένες χωρίς μοντέλο).
- two_session_live.py: runner δύο sessions για ASI06 με πραγματικό μοντέλο. two_session_sim.py, e2e.py: έλεγχοι χωρίς μοντέλο.
- HANDOFF.md: κατάσταση και επόμενα βήματα.
- docs/: η έρευνα που έχει γίνει. kaggle_setup.md (δοκιμασμένα κελιά Kaggle), owasp_coverage.md (κάλυψη OWASP ανά κατηγορία), owasp_gaps_verification.md, plan_attacks.md (σχέδιο των 3 επιθέσεων με papers-οδηγούς), intermediate_agent_research.md (θέσεις του ενδιάμεσου agent στο pipeline, ATLAS, σχετικά papers). Διάβασέ τα όταν χρειάζεσαι λεπτομέρειες.
