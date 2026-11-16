# Επαλήθευση: τα τρία κενά στέκουν, αλλά πιο στενά

**Σύντομη απάντηση.** Όσα είπα για το τι καλύπτει το AgentDojo ισχύουν. Τα έλεγξα στον ίδιο τον κώδικα και ήταν όλα σωστά, με μικρές διορθώσεις. Για το τι κάνει η υπόλοιπη βιβλιογραφία, ένας ισχυρισμός ήταν λάθος: είχα πει ότι κανείς δεν ελέγχει με κώδικα το "Fabricated Task Completion". Υπάρχουν επίσης αρκετές νέες εργασίες που πλησιάζουν τα κενά. Και οι τρεις υποψήφιες κατευθύνσεις βγαίνουν **GAP WEAKENED**, δηλαδή το κενό στενεύει χωρίς να κλείνει. Κανείς δεν έχει φτιάξει καμία από τις τρεις μέσα στο AgentDojo. Και για τις τρεις όμως η ιδέα της επίθεσης και ο τρόπος μέτρησης υπάρχουν ήδη σε άλλα περιβάλλοντα. Αυτό που μένει δικό σου είναι κυρίως benchmark engineering: να τις ενσωματώσεις στο AgentDojo, να δοκιμάσεις άμυνες και να κάνεις συγκρίσιμες μετρήσεις σε open models.

## Πόσο σίγουρο είναι

Βεβαιότητα 100% (ή "1000%") δεν μπορεί να υπάρξει για βιβλιογραφία. Μια εργασία που ανέβηκε χθες ή που δεν έχει ευρετηριαστεί ακόμα μπορεί πάντα να μας ξέφυγε. Ο έλεγχος έγινε ως εξής:

- **Αναζητήσεις:** περίπου 200 web αναζητήσεις σε 4 κατευθύνσεις (51 για Unbounded, 43 για Fabricated, 42 για Hidden Context, 63 για τις υπόλοιπες εργασίες και νέα papers). Μαζί με τις 48 προηγούμενες για το Hidden Context είναι περίπου 240.
- **Κώδικας:** έλεγχος του AgentDojo στον ίδιο τον κώδικα, με εγκατάσταση και εκτέλεση.
- **Τι ήταν μπλοκαρισμένο:** Google Scholar, Semantic Scholar, OpenReview, OpenAlex, οι σελίδες arXiv abs/listing και η αναζήτηση στο GitHub. Γι' αυτό **δεν έχουμε ακόμα τις λίστες "cited-by"**, δηλαδή ποιες εργασίες παραθέτουν το AgentDojo ή το InjecAgent. Αυτό είναι το μεγαλύτερο ανοιχτό ρίσκο.

Επίπεδα βεβαιότητας σε αυτό το κείμενο:

- **[επαληθεύτηκε σε κώδικα]**: οι ισχυρισμοί για το AgentDojo. Υψηλή βεβαιότητα.
- **[επαληθεύτηκε σε σελίδες paper]**: ετικέτες [full], [partial], [abstract only], [title only]. Το [partial] σημαίνει ότι το κείμενο το διάβασε εργαλείο που κάνει περίληψη, οπότε οι ακριβείς αριθμοί θέλουν δεύτερο έλεγχο πριν μπουν στη διπλωματική.
- **[δεν βρέθηκε μετά από αναζήτηση]**: ισχύει για το ότι "κανείς δεν το έχει κάνει μέσα στο AgentDojo". Είναι η πιο αδύναμη μορφή απόδειξης.

## 1. Το AgentDojo στον κώδικα: όλοι οι ισχυρισμοί σωστοί

Ελέγχθηκε η τελευταία έκδοση: agentdojo 0.1.35 (benchmark v1.2.2), commit `089ed468`. Νεότερη έκδοση στο PyPI δεν υπάρχει ([PyPI](https://pypi.org/pypi/agentdojo/json)). Ισχύουν τα εξής:

- Οι επιθέσεις βάζουν μόνο κείμενο σε placeholders των δεδομένων.
- Υπάρχουν 35 injection tasks (14/7/9/5).
- Κανένα task δεν στοχεύει system prompt ή tool schemas.
- Μόνο το travel injection_task_6 κοιτάζει την τελική απάντηση (`model_output`).
- Δεν υπάρχει memory, multi-agent ή shell tool, και ισχύει `max_iters=15`.

Πηγή για όλα: [repo στο commit](https://github.com/ethz-spylab/agentdojo/tree/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo) [επαληθεύτηκε σε κώδικα].

Μικρές διορθώσεις:

- **agentdojo-inspect (NIST):** τα 2 bash user tasks βρίσκονται σε ξεχωριστή suite, `workspace_plus_with_bash_user_tasks`, όχι στο κανονικό workspace ([repo](https://github.com/usnistgov/agentdojo-inspect/tree/a491020f/examples/inspect/workspace_plus)).
- **Ποια έκδοση των tasks τρέχει:** το `load_suites.py` δεν φορτώνει ποτέ τα αρχεία της v1_1_2. Έτσι η v1.2.2 τρέχει στην πράξη την **v1 έκδοση** των workspace injection_task_0/4/5 και του travel injection_task_3. Όταν παραθέτεις τον κώδικα αυτών των tasks, να παραθέτεις το αρχείο της v1 ([load_suites.py](https://github.com/ethz-spylab/agentdojo/blob/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo/task_suite/load_suites.py)).
- **Οι DoS επιθέσεις:**
  - Τρέχουν μόνο με το **πρώτο** injection task κάθε suite.
  - Το security (δηλαδή η επιτυχία της επίθεσης) ορίζεται ως `not utility`.
  - Σφάλματα όπως context length exceeded ή server error μετράνε κι αυτά **ως επιτυχία της επίθεσης**.
  - Δεν καταγράφονται tokens, κόστος ή πλήθος tool calls. Καταγράφεται μόνο η διάρκεια ([benchmark.py](https://github.com/ethz-spylab/agentdojo/blob/089ed468cf3ed0322acc66b0211f26d9d90dbf60/src/agentdojo/benchmark.py)).

## 2. Τι είχα πει και τι ισχύει

| Είχα πει | Τι ισχύει |
|---|---|
| Κανείς δεν ελέγχει Fabricated Task Completion με κώδικα | **ΛΑΘΟΣ.** Το "From Confident Closing to Silent Failure" (2606.09863, ICML 2026 workshop) συγκρίνει τον ισχυρισμό του agent ότι τελείωσε με την πραγματική κατάσταση του περιβάλλοντος, με κώδικα (regex ή status field), στα tau2-bench και AppWorld [partial] ([arXiv](https://arxiv.org/html/2606.09863)) |
| Το "Fabricated Task Completion" είναι σενάριο του OWASP LLM07:2026 | Δεν επαληθεύτηκε. Η φράση δεν βρέθηκε σε δευτερογενείς πηγές ([Giskard](https://www.giskard.ai/glossary/owasp-llm07-2026-misinformation)). Πρέπει να το ελέγξεις στο επίσημο PDF του OWASP |
| Unbounded: OTora, Beyond Max Tokens, DoW-BENCH | Υπάρχουν και πιο κοντινές εργασίες: Sponge Tool Attack (2601.17566, ICML 2026), που μετρά βήματα tool calls έναντι budget με την ακρίβεια να διατηρείται [partial] ([arXiv](https://arxiv.org/pdf/2601.17566)). Επίσης LeechHijack, Mobius Injection και CostBomb |
| Το OTora είναι σε δικό του περιβάλλον | Το OTora **χρησιμοποιεί InjecAgent** για τα Email/OS σενάριά του [partial] ([arXiv](https://arxiv.org/pdf/2605.08876)). Άρα αν μεταφέρεις την ιδέα στο InjecAgent, πέφτεις δίπλα του |
| Το audit 2605.15118 λέει "μηδενική κάλυψη" | Πρέπει να το παραθέσεις διορθωμένο: το AgentDojo έχει DoS, αλλά το μετρά ως αποτυχία του task. Αυτό που λείπει είναι μετρική κατανάλωσης ([arXiv](https://arxiv.org/pdf/2605.15118)) |
| Framing Gap [μερικώς] | Διαβάστηκε ολόκληρο: canary στο context, indirect κανάλι, mock εργαλείο `post_data`, έλεγχος με κώδικα, δικό τους lab, ένα μόνο βήμα. Δεν λέει αν το canary είναι στο system prompt ([arXiv](https://arxiv.org/pdf/2608.27092)) |
| Το 2509.05755 δεν μετρά διαρροή | **Μετρά** (στη v6). Διαρροή system prompt και tool schemas μέσω ορίσματος κακόβουλου MCP tool, με similarity μετρικές ([arXiv](https://arxiv.org/pdf/2509.05755)) |
| Το Whispers μετρά μόνο το chat | Ο τυπικός ορισμός του **περιλαμβάνει και tool calls**. Αυτό που δεν δοκιμάζει είναι secret στο system prompt μαζί με indirect κανάλι ([arXiv](https://arxiv.org/html/2402.06922)) |
| - | Νέο: ContextLeak (2608.27800). Διαρροή tool list και ιστορικού μέσω κακόβουλου tool [full μέσω mirror] ([alphaXiv](https://www.alphaxiv.org/abs/2608.27800.md)) |
| "The Surface You Test...", NeurIPS 2026 | Είναι το arXiv 2605.30454. Ότι τρέχει σε AgentDojo επιβεβαιώθηκε. Το venue NeurIPS **δεν επιβεβαιώθηκε** (ίσως είναι workshop). Υπάρχει και το "Same Payload, Different Channel" (2606.00566) ([arXiv](https://arxiv.org/pdf/2605.30454)) |
| P2SQL χωρίς κώδικα | **Έχει κώδικα** ([PDF](https://syssec.dpss.inesc-id.pt/papers/pedro_icse25.pdf)) |
| From Spark to Fire: όχι εργαλεία | **Χρησιμοποιεί εργαλεία** (Python, calculator, Wikipedia API), αλλά χωρίς ενέργειες που αλλάζουν κατάσταση ([arXiv](https://arxiv.org/html/2603.04474v2)) |
| TagAlong-Dojo | Ο πραγματικός τίτλος είναι "David vs. Goliath..." (2602.02395). Η κυκλοφορία του κώδικα έχει υποσχεθεί, αλλά δεν επαληθεύτηκε ([arXiv](https://arxiv.org/html/2602.02395)) |
| EAL-Bench, NeurIPS 2026 | Είναι NeurIPS 2026 **workshop** ([NeurIPS](https://neurips.cc/virtual/2026/168135)) |
| MAS Arbitrary Code, COLM 2025 | Το venue δεν επιβεβαιώθηκε |
| - | Το MemForm (2610.14431) υπάρχει, αλλά το ξέρουμε μόνο από τον τίτλο [title only] |
| - | Νέο: AJAR (2609.26900) τρέχει πάνω στο **ίδιο AgentDojo v1.2.2** με privilege μετρικές, χωρίς νέα tasks ([arXiv](https://arxiv.org/pdf/2609.26900)) |
| Ο πίνακας benchmark x OWASP είναι νέος | Το 2609.28915 ήδη αντιστοιχίζει attack mechanics σε OWASP (LLM 2025, T1-T15) και περιλαμβάνει το AgentDojo ([arXiv](https://arxiv.org/pdf/2609.28915)). Ο δικός σου πίνακας μένει διακριτός μόνο αν βασίζεται στις λίστες ASI/LLM 2026 και σε task IDs ελεγμένα στον κώδικα |

## 3. Ετυμηγορία ανά υποψήφιο: και τα τρία GAP WEAKENED

| Υποψήφιο | Πιο κοντινή εργασία | Τι μένει διαφορετικό | Κύριο ρίσκο από reviewer |
|---|---|---|---|
| **Unbounded Consumption (task-preserving)**: η επίθεση σπαταλά πόρους ενώ η δουλειά του χρήστη ολοκληρώνεται, ώστε να μη φαίνεται | Sponge Tool Attack για τη μετρική. OTora για το InjecAgent | Injection μέσα από tool output του AgentDojo. Μέτρηση tool calls από τα traces (`security_from_traces`) **μαζί** με το `utility()` στο ίδιο run | "Απλό engineering". Το `max_iters=15` βάζει όριο στο πόσο μπορεί να μεγαλώσει η κατανάλωση. Η μεταφορά στο InjecAgent συμπίπτει με το OTora |
| **Hidden Context Exposure μέσω tool calls**: διαρροή κάτι που υπάρχει μόνο στο system prompt | Framing Gap. Δεύτερα: 2509.05755 v6, ContextLeak | Canary (μοναδικό ψεύτικο string που φαίνεται αν διαρρεύσει) μόνο στο `system_message`, διαρροή μέσα από τα κανονικά εργαλεία των suites, έλεγχος με `security()`, πολλά βήματα μαζί με utility | Οι overt επιθέσεις στο Framing Gap έπιασαν περίπου 0% σε ισχυρό μοντέλο, άρα το ASR μπορεί να βγει σχεδόν 0. Τρεις σχετικές εργασίες ανέβηκαν μόνο τον Αύγουστο του 2026 |
| **Fabricated Task Completion με έλεγχο έναντι state** | 2606.09863 για τη μέθοδο. ICoA για το AgentDojo + injection | Η ψευδής αναφορά προκαλείται από **injection**. Έλεγχος με κώδικα μέσα στο AgentDojo, ενώ το ICoA χρησιμοποιεί GPT-4o judge | "Συνδυασμός δύο υπαρχουσών εργασιών". Λειτουργεί καθαρά μόνο σε user tasks που αλλάζουν κατάσταση. Το regex μπορεί να το ξεγελάσει ο επιτιθέμενος |

Πηγές: Sponge ([arXiv](https://arxiv.org/pdf/2601.17566)), OTora ([arXiv](https://arxiv.org/pdf/2605.08876)), Framing Gap ([arXiv](https://arxiv.org/pdf/2608.27092)), ICoA ([arXiv](https://arxiv.org/pdf/2608.30362)), 2606.09863 ([arXiv](https://arxiv.org/html/2606.09863)).

Ευθέως: σε κανένα από τα τρία δεν είσαι ο πρώτος που έχει την ιδέα. Η συνεισφορά είναι ότι "το έφερες μέσα στο AgentDojo, με κώδικα, με άμυνες, σε open models".

**Κατάταξη (η δική μου κρίση):**

1. **Unbounded.** Δεν υπάρχει εργασία μέσα στο AgentDojo, και η μέτρηση γίνεται εξ ολοκλήρου με κώδικα και στις δύο πλευρές (traces και utility).
2. **Hidden Context.** Ούτε εδώ υπάρχει εργασία μέσα στο AgentDojo, αλλά υπάρχει πραγματικό ρίσκο το ASR να βγει σχεδόν 0, και το πεδίο κινείται γρήγορα.
3. **Fabricated.** Είναι το πιο αδύναμο, γιατί η μέθοδος έχει πλέον κοντινό prior art.

Ο συνδυασμός με τον αμυντικό agent (Φάση Β) δυναμώνει τη διπλωματική, όπως είχαμε ήδη σχεδιάσει. Οι σημειώσεις για το Hidden Context προτείνουν ρητά να προστεθεί άμυνα ή ανάλυση για να απαντηθεί η κριτική "thin engineering".

## 4. Τι λες στον επιβλέποντα και τι ελέγχεις μόνος σου

**Παράγραφος για τον επιβλέποντα:** "Επαλήθευσα την κάλυψη του AgentDojo στον κώδικα (v1.2.2) και ισχύει. Στη βιβλιογραφία βρήκα πιο κοντινές εργασίες απ' όσο νόμιζα. Για καθεμία από τις τρεις κατηγορίες, η επίθεση και η μέτρηση υπάρχουν ήδη σε άλλα περιβάλλοντα (Sponge Tool Attack και OTora, Framing Gap, 2606.09863). Κανείς όμως δεν τις έχει υλοποιήσει μέσα στο AgentDojo με έλεγχο από κώδικα. Προτείνω να τις παρουσιάσουμε ως ενσωμάτωση στο AgentDojo και σύγκριση αμυνών σε open models, όχι ως νέες επιθέσεις, και να τις συνδυάσουμε με τον αμυντικό agent. Πρώτη προτεραιότητα το Unbounded Consumption."

**Τρεις έλεγχοι με κανονικό browser:**

1. **Semantic Scholar:** στη σελίδα κάθε paper, άνοιξε τα "Citations" για το 2406.13352 (AgentDojo) και το 2403.02691 (InjecAgent), με φίλτρο από 2026-09. Ψάξε για λέξεις όπως consumption, cost, token, leak, system prompt, canary, claim, false success, honest.
2. **MemForm:** άνοιξε το arxiv.org/abs/2610.14431. Δες αν χρησιμοποιεί AgentDojo και πώς βαθμολογεί.
3. **arXiv:** γρήγορη αναζήτηση στις υποβολές των τελευταίων δύο εβδομάδων (cs.CR, cs.AI) με τις λέξεις "AgentDojo" και "InjecAgent".

## Σημειώσεις

- Το "δεν βρέθηκε" δεν σημαίνει "δεν υπάρχει". Μέχρι να κάνεις τον έλεγχο 1, το "πρώτο μέσα στο AgentDojo" είναι υπόθεση και όχι γεγονός.
- Ότι το Unbounded είναι πρώτο στην κατάταξη είναι δική μου κρίση. Δεν είναι εύρημα κάποιας πηγής, και το όριο `max_iters=15` πρέπει να το λάβεις υπόψη στον σχεδιασμό.
- Μη γράψεις στη διπλωματική ότι το "Fabricated Task Completion" είναι σενάριο του OWASP πριν το βρεις στο επίσημο κείμενο.

## Συμπέρασμα

Η εικόνα για το AgentDojo είναι σωστή και τεκμηριωμένη στον κώδικα. Τα τρία κενά υπάρχουν μόνο με τη στενή έννοια "μέσα στο AgentDojo". Η διπλωματική πρέπει να παρουσιαστεί ως ενσωμάτωση με άμυνες και όχι ως ανακάλυψη νέων επιθέσεων.
