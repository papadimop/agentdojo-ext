# Κάλυψη OWASP ανά κατηγορία: AgentDojo και βιβλιογραφία (2026-11-06)

> Διόρθωση 25/11/2026: βλ. docs/related_work_2026-11.md. ASI06 ΔΕΝ είναι πια «ΟΧΙ στο AgentDojo» (MemoryDojo, 2611.09721). Τα CostBomb, 2605.15118 και SED (2609.36603) δεν βρέθηκαν. Το «OTora χρησιμοποιεί InjecAgent» δεν επιβεβαιώθηκε. Η αρίθμηση LLM 2026 επιβεβαιώθηκε στο επίσημο repo του OWASP.

Σύμβολα: [κώδικας] = διαβάστηκε στον κώδικα, [μερικώς] = paper διαβάστηκε εν μέρει, [abstract] = μόνο abstract.
Η αντιστοίχιση AgentDojo -> OWASP είναι δική μας (το AgentDojo δεν αναφέρει OWASP). AgentDojo v1.2.2, commit 089ed468.

## OWASP Top 10 for Agentic Applications (κύρια λίστα)

| ID | Κατηγορία | AgentDojo | Ποιος άλλος (αν όχι) | Κενό; |
|---|---|---|---|---|
| ASI01 | Agent Goal Hijack | ΝΑΙ, όλο το benchmark (π.χ. workspace injection_task_0) | - | Όχι (κορεσμένο) |
| ASI02 | Tool Misuse and Exploitation | ΝΑΙ (π.χ. banking injection_task_5), εκτός loops | - | Όχι |
| ASI03 | Identity and Privilege Abuse | ΜΕΡΙΚΩΣ (banking 7, slack 5) | AgentDyn github suite [κώδικας], EAL-Bench, AuthBench | Μικρό (multi-user) |
| ASI04 | Agentic Supply Chain | ΟΧΙ | "The Surface You Test..." (NeurIPS 2026, πάνω στο AgentDojo) [abstract], MCP-SafetyBench, MSB | Όχι |
| ASI05 | Unexpected Code Execution | ΟΧΙ | AgentDojo-Inspect (1 task, canary file) [κώδικας], MAS Arbitrary Code (COLM 2025) | Όχι |
| ASI06 | Memory & Context Poisoning | ΟΧΙ | XSPI-Bench, Injection-Execution Dissociation, eTAMP, MemSecBench [μερικώς] | Μόνο "μέσα στο AgentDojo" |
| ASI07 | Insecure Inter-Agent Communication | ΟΧΙ | TagAlong-Dojo (AgentDojo, κώδικας όχι δημόσιος), A2ASecBench (ICLR 2026) [μερικώς] | Μερικό, δύσκολο |
| ASI08 | Cascading Failures | ΟΧΙ | From Spark to Fire, ACIArena (QA/μαθηματικά, όχι εργαλεία) [μερικώς] | Μερικό, δύσκολο |
| ASI09 | Human-Agent Trust Exploitation | ΕΛΑΧΙΣΤΑ (phishing σε τρίτους) | ICoA (AgentDojo, GPT-4o judge) [μερικώς] | Ναι, αλλά δύσκολο με κώδικα |
| ASI10 | Rogue Agents | ΟΧΙ | SHADE-Arena, ROGUE, AgentMisalignment [μερικώς] | Μερικό (alignment) |

## OWASP Top 10 for LLM Applications 2026 (σε παρένθεση το 2025)

| ID | Κατηγορία | AgentDojo | Ποιος άλλος | Κενό; |
|---|---|---|---|---|
| LLM01 (01) | Prompt Injection | ΝΑΙ, μόνο indirect | AgentHarm, ASB (direct) | Όχι |
| LLM02 (02) | Sensitive Information Disclosure | ΝΑΙ, ~19 tasks (π.χ. workspace injection_task_4) | - | Όχι |
| LLM03 (06) | Excessive Agency | ΜΕΡΙΚΩΣ (= ASI02) | - | Όχι |
| LLM04 (03) | Supply Chain | ΟΧΙ (επίπεδο μοντέλου, εκτός scope) | βλ. ASI04 | - |
| LLM05 (04) | Data and Model Poisoning | ΟΧΙ | βλ. ASI06 | - |
| LLM06 (10) | Unbounded Consumption | ΟΧΙ (τα 5 dos attacks μετρούν αποτυχία task) | OTora (ICML 2026), Beyond Max Tokens, DoW-BENCH (δικά τους περιβάλλοντα) | ΝΑΙ μέσα στο AgentDojo |
| LLM07 (09) | Misinformation | ΕΛΑΧΙΣΤΑ (travel injection_task_6) | MisinfoTask, Upward Deception (LLM judge) | ΝΑΙ για Fabricated Task Completion με κώδικα |
| LLM08 (07) | Hidden Context Exposure | ΟΧΙ (κανένας από 54 στόχους) | Framing Gap, Whispers in the Machine, Silent Egress (δικά τους περιβάλλοντα) | ΝΑΙ μέσα στο AgentDojo |
| LLM09 (08) | Vector and Embedding Weaknesses | ΟΧΙ (δεν έχει vector store) | RAG benchmarks (όχι agents) | Μερικό, θέλει vector store |
| LLM10 (05) | Improper Output Handling | ΟΧΙ | P2SQL (ICSE 2025), RAS-Eval | ΝΑΙ, θέλει νέο downstream εργαλείο |

## Υποψήφιες κατηγορίες για τη διπλωματική
1. LLM06 Unbounded Consumption
2. LLM08 Hidden Context Exposure
3. LLM07 Misinformation ως Fabricated Task Completion
Εφεδρικές: ASI06 μέσα στο AgentDojo (πολυσύχναστο), LLM10 με downstream εργαλείο, ASI09 με έλεγχο κώδικα.
