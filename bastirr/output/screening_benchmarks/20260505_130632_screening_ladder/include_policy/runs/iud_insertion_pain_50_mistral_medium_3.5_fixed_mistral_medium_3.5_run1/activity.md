# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-05-05 13:07  
> **Duration:** 1m 24s  
> **Total tokens:** 128,301 (input: 117,172 / output: 11,129)

> **Benchmark suite:** screening_ladder  
> **Review key:** iud_insertion_pain_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full  
> **Dataset split:** random_test  
> **Studies:** 50  
> **Gatekeeper preset:** mistral_medium_3.5  
> **Gatekeeper model:** mistral-medium-3.5 [Mistral Medium 3.5]  
> **Orchestrator preset:** mistral_medium_3.5  
> **Orchestrator model:** mistral-medium-3.5 [Mistral Medium 3.5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 3 | 1m 24s | 12,063 / 619 |
| Gatekeeper | 3 | 1m 16s | 105,109 / 10,510 |
| **Total** | **6** | **1m 24s** | **117,172 / 11,129** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*13:07:44 — 3s — 3,701 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*13:09:03 — 1m 18s — 119,776 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Final Output (Orchestrator)

*13:09:05 — 2s — 4,824 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
