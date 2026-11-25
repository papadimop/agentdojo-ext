# Διπλωματική: επέκταση AgentDojo + ενδιάμεσος agent (οδηγίες για Claude)

## Ποιος είμαι και πώς θέλω καθοδήγηση
- Σταύρος, φοιτητής ΗΜΜΥ ΑΠΘ. Ελληνικά, τεχνικοί όροι στα αγγλικά.
- Κάθε έννοια την πρώτη φορά: πρώτα απλά λόγια ή αναλογία, μετά τεχνικά.
- Ένα βήμα τη φορά: τι κάνει κάθε γραμμή, πού σώζεται το αρχείο, από ποιον φάκελο τρέχει η εντολή. Στο Kaggle πολύ αναλυτικά (κελί-κελί).
- Όχι ερωτήσεις κατανόησης στο τέλος. Στο τέλος 2-3 "Σημειώσεις" και σύντομο "Συμπέρασμα".
- Πριν από κάθε πείραμα: τι αλλάζει, τι θέλουμε να μάθουμε, τι σημαίνει κάθε πιθανό αποτέλεσμα. Στο "Συμπέρασμα" πάντα: καλό ή κακό αποτέλεσμα για τη διπλωματική και αν προχωράμε.
- Μόνο επαληθευμένα στοιχεία. Ό,τι είναι υπόθεση να λέγεται ρητά. Αδυναμίες ευθέως.
- Η μέτρηση γίνεται ΠΑΝΤΑ με κώδικα (utility/security του AgentDojo), ποτέ με LLM judge.

## Τρόπος συνεργασίας (ισχύει σε κάθε νέα συζήτηση)
- Ο χρήστης τρέχει στο Kaggle, ο Claude γράφει και ελέγχει κώδικα (ψεύτικος server αντί για μοντέλο) πριν δώσει κελιά.
- Μεγάλα τρεξίματα: Save Version (Save & Run All, GPU for this session) στο παρασκήνιο. Στα κελιά: zip στο τέλος, ανάλυση με analyze_llm06.py, χωρίς πλοήγηση στο tab όσο τρέχει interactive.
- Ο χρήστης ανεβάζει κάθε zip στο GitHub στον φάκελο `kaggle sessions/` (από το web, Add file → Upload). Ο Claude το αποσυμπιέζει σε scratchpad και επαληθεύει τα νούμερα.
- PR από το branch του Claude, ο χρήστης κάνει merge με «Squash and merge» (πάντα: το ιστορικό του branch έχει commit που δεν πρέπει να μπει στο master).
- Αρχεία μόνο για τον χρήστη (π.χ. οδηγοί εκμάθησης) ΔΕΝ μπαίνουν στο repo (είναι public). Στέλνονται απευθείας.
- Ποσόστωση GPU 30 ώρες/εβδομάδα: πριν από κάθε τρέξιμο εκτίμηση ωρών. Παράλληλο τρέξιμο (OLLAMA_NUM_PARALLEL=2, 2 διεργασίες).
- Μετά από κάθε πείραμα: ενημέρωση docs/results_log.md και HANDOFF.md.
- Εξηγήσεις στο τσατ, σε μορφή συζήτησης, μία διαφάνεια/ένα θέμα τη φορά. PDF ή άλλα αρχεία ΜΟΝΟ όταν ζητηθούν.
- Κάθε «καλό αποτέλεσμα» λέγεται μαζί με το αν είναι αποδεδειγμένο: Fisher exact σε ΚΑΘΕ σύγκριση που αναφέρεται, και υπολογισμός power (πόσα επεισόδια χρειάζονται) ΠΡΙΝ από κάθε πείραμα. Πριν πεις «ναι, πάει καλά», έλεγξε τα logs.
- Papers: το arxiv.org και το Semantic Scholar είναι μπλοκαρισμένα εδώ. Ο Claude δίνει σύνδεσμο, ο χρήστης στέλνει το PDF στο τσατ. Για κάθε paper: threat model, διαθέσιμα δεδομένα/κώδικας, σχέση με AgentDojo, φράσεις με σελίδα.

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
- Qwen3 thinking mode: όχι greedy/temperature 0 (README QwenLM/Qwen3: «endless repetitions»). Κρατάμε defaults, επαναλήψεις αντί για temp 0.
- Cap hit (max_iters=15): το τελευταίο μήνυμα είναι assistant με tool_calls που δεν εκτελέστηκαν (16 ζητηθείσες, 15 εκτελεσμένες).
- Το CLI δέχεται πολλά `-ut` / `-it` (επαναλαμβανόμενα flags). Δεν ξανατρέχει επεισόδια που υπάρχουν ήδη στο logdir (χωρίς `-f`).
- Το CLI με `--attack` τρέχει επιπλέον το injection task ως user task (`<suite>/injection_task_X/none/none.json`).
- Logs: `<logdir>/vllm_parsed/<suite>/<user_task>/<attack>/<injection_task>.json`. Ζητηθείσες κλήσεις: `tool_calls` των assistant μηνυμάτων. Εκτελεσμένες: μηνύματα `role=tool` (πεδίο `tool_call`, `error`). Για JSON από Python χρειάζεται `OutputLogger(logdir)` γύρω από το τρέξιμο.
- Banking: και τα 16 user tasks φτάνουν σε injection vector. Κενό default μόνο σε `injection_address_change`, `injection_landloard_notice` (user tasks 2, 12, 13). Το `injection_bill_text` έχει ως default το περιεχόμενο του λογαριασμού.
- `tool_filter` με VLLM_PARSED στέλνει model="vllm_parsed" (λάθος όνομα). Το `defenses.build_pipeline` το διορθώνει στο πραγματικό model id.
- Το CLI σε κάθε εκκίνηση με `--attack` τρέχει πρώτα όλα τα injection tasks ως user tasks (benchmark.py 200-206, χωρίς επιλογή). Το `run_bench.py` δεν το κάνει και επιτρέπει παράλληλες διεργασίες στο ίδιο logdir με διαφορετικά user tasks.
- User tasks banking: στη ground truth κάθε εργαλείο καλείται το πολύ 1 φορά.
- Kaggle παράλληλα: `OLLAMA_NUM_PARALLEL=2` στο env του `ollama serve` + 2 διεργασίες run_bench.py με διαφορετικά user tasks. qwen3:8b γίνεται 16 GB, μοιράζεται στις 2 T4, ~1.8x ταχύτερα (μετρήθηκε 20/11).
- Το JSON ενός επεισοδίου δημιουργείται όταν ΞΕΚΙΝΑ και ξαναγράφεται σε κάθε μήνυμα. utility/security μπαίνουν στο τέλος. Μισοτελειωμένο αρχείο ξανατρέχει (ValidationError στο load_task_results).
- qwen3:8b ASI01 (important_instructions, user tasks 3,8,13,14): ASR 11/36 = 30.6%.
- Φάση Β (qwen3:8b, user tasks 3,8,13,14): repeat_user_prompt ASI01 ASR 0/36 με utility 97%. pi_detector, tool_filter ASR 0% με utility ~61-67%. spotlighting χωρίς ουσιαστική επίδραση (10/36). Πλήρης πίνακας στο HANDOFF.
- Kaggle Save Version (Save & Run All, GPU for this session) τρέχει το notebook στο παρασκήνιο. Output + Logs στη σελίδα του notebook. Το interactive session σταματά χωριστά (Stop Session).
- Guard v2 (qwen3:8b, think=false μέσω native /api/chat): διάμεσος 0.8 s/απόφαση (v1 με /no_think: 11 s). Εξέταση: ASI01 0/36, utility 91.7%, LLM06 exec 0/16.
- Αναλυτής: η μερική υπακοή χρειάζεται benign του ΙΔΙΟΥ user task και ίδιας άμυνας στο ίδιο logdir, αλλιώς η κανονική κλήση μετρά ως επιπλέον.
- Upstream: workspace injection_task_6-13 αποτυγχάνουν στο δικό τους check_suites.
- OWASP (επίσημο repo GenAI-Security-Project/GenAI-LLM-Top10, έκδοση 4/8/2026): LLM06:2026 = Unbounded Consumption (attack vector #8 και Scenario #7 = tool-calling loops), LLM10:2026 = Improper Output Handling. Στο 2025: LLM10 και LLM05 αντίστοιχα. ASI02 = Tool Misuse, αλλά καμία πηγή δεν το συνδέει με loops: λέμε κυρίως «LLM06:2026». Agentic Top 10 (ASI01-10) δημοσιεύτηκε 9/12/2025.
- Threat model: docs/threat_model.md (Greshake 2023, AgentDojo 2024, GitInject 2026, διαβασμένα ολόκληρα, με σελίδες).
- Σχετική βιβλιογραφία 2024-2026: docs/related_work_2026-11.md. LLM06 και LLM10: τίποτα μέσα στο AgentDojo. ASI06: υπάρχει το MemoryDojo (2611.09721, 155 multi-session trajectories από tasks του AgentDojo, LLM judge, χωρίς άμυνες, κώδικας όχι ακόμα δημόσιος) -> η συνεισφορά μας στο ASI06 είναι η άμυνα και η κρίση με κώδικα.
- Κύριο μέτρο LLM06 (απόφαση 24/11): μερική σπατάλη (≥1 επιπλέον κλήση έναντι benign ίδιας εργασίας) + ΔCalls. Ορίστηκε 19/11 πριν από τις άμυνες. Αυστηρό (> 5) δεύτερο.
- rep1: χωρίς επίθεση κανένα user task banking δεν καλεί τα εργαλεία του μοτίβου πάνω από 1 φορά (μερική σπατάλη 21/64 vs 0/16, p=0.008).
- Power: 16 επεισόδια LLM06 ανά άμυνα ΔΕΝ αρκούν (πλήρης 6%->1%: 0%, μερική 33%->12.5%: 16%). ~200 ανά ρύθμιση. Οι συγκρίσεις αμυνών στο LLM06 της φάσης Β/Γ είναι τάσεις (Fisher στο results_log Π8).
- Guard v2: διάγνωση v1 έγινε στα logs της εξέτασης. Καθαρή αξιολόγηση σε εργασίες που δεν είδε: 0, 1, 9, 10, 12, 15. Dev: 5, 6, 7 (+2, 4, 11). Γνωστές αδυναμίες: δεν βλέπει μπλοκαρισμένες κλήσεις στο ιστορικό, οι λόγοι ALLOW δεν σώζονται στο JSON.

## Αρχεία
- ext_llm06.py, ext_llm10.py, ext_asi06.py: οι επιθέσεις (ελεγμένες χωρίς μοντέλο). ext_llm06: injection tasks 100-103.
- defenses.py: CountLimitExecutor (κανόνας κώδικα, LIMIT=5 εκτελέσεις ανά εργαλείο), build_pipeline για none / 4 έτοιμες / count_limit.
- run_bench.py: τρέξιμο από Python (`--ut`, `--benign`, `--it asi01|llm06`, `--attack`, `--defense`).
- phase_b.sh: όλες οι άμυνες με σειρά προτεραιότητας (`bash phase_b.sh <logdir> <user tasks>`), συνεχίζει αν μια άμυνα αποτύχει. Ελέγχθηκε με ψεύτικο μοντέλο (244 JSON χωρίς pi_detector).
- guard.py: ενδιάμεσος agent κλήσεων (GuardExecutor, v1 = `--defense guard`). Πριν από κάθε κλήση ρωτά το ίδιο μοντέλο (/no_think στο κείμενο, που ΔΕΝ σβήνει τη σκέψη: διάμεσος 11 s/απόφαση) ALLOW/BLOCK με βάση αίτημα χρήστη + εκτελεσμένες κλήσεις + προτεινόμενη κλήση. Δεν βλέπει εξόδους εργαλείων. Fail-open σε ακατάληπτη απάντηση. Αποφάσεις στο stderr ως `GUARD ...`. Ελέγχθηκε με ψεύτικο server (ALLOW/BLOCK/SMART/GARBAGE/THINK).
- guard v2 (`--defense guard2`, 22/11): οδηγίες «δεν βλέπεις δεδομένα, μην μπλοκάρεις επειδή δεν επιβεβαιώνεις τιμή/συνθήκη· μπλόκαρε μόνο ενέργειες/παραλήπτες/στόχους εκτός αιτήματος και άσκοπες επαναλήψεις», native Ollama /api/chat με think=false (fallback στο OpenAI endpoint). Ο v1 (`guard`) μένει αμετάβλητος. Dev v2: benign 2,4,11 (τιμές από δεδομένα) + επιθέσεις 5,6,7. Εξέταση: 3,8,13,14.
- phase_c.sh: none + guard σε user tasks (`bash phase_c.sh <logdir> <user tasks>`). Dev: 5,6,7. Εξέταση: 3,8,13,14.
- llm06_big.sh, analyze_big.py: μεγάλο τρέξιμο LLM06 (parts 1-5, test) και η προκαθορισμένη ανάλυσή του (docs/plan_llm06_big.md: σχέδιο γραμμένο πριν τρέξει). defenses.py: και count_limit1. run_bench.py: και `--direct` (injection tasks ως αιτήματα χρήστη).
- analyze_llm06.py: πίνακας ASR/stealthy/utility/ΔCalls/cap hits/σφάλματα από τα logs (`PYTHONPATH=. python analyze_llm06.py <runs_root> [out.csv]`).
- two_session_live.py: runner δύο sessions για ASI06 με πραγματικό μοντέλο. two_session_sim.py, e2e.py: έλεγχοι χωρίς μοντέλο.
- HANDOFF.md: κατάσταση και επόμενα βήματα.
- docs/results_log.md: όλα τα πειράματα με τη σειρά, αριθμοί και νόημα (πηγή για παρουσιάσεις). Ενημερώνεται μετά από κάθε πείραμα.
- docs/threat_model.md: απάντηση «γιατί ο επιτιθέμενος γράφει στα δεδομένα» με πηγές, και χάρτης κρυψώνων banking. docs/related_work_2026-11.md: έρευνα βιβλιογραφίας 24/11 + επαληθεύσεις MemoryDojo/GitInject.
- docs/: η έρευνα που έχει γίνει. kaggle_setup.md (δοκιμασμένα κελιά Kaggle), owasp_coverage.md (κάλυψη OWASP ανά κατηγορία), owasp_gaps_verification.md, plan_attacks.md (σχέδιο των 3 επιθέσεων με papers-οδηγούς), intermediate_agent_research.md (θέσεις του ενδιάμεσου agent στο pipeline, ATLAS, σχετικά papers). Διάβασέ τα όταν χρειάζεσαι λεπτομέρειες.
