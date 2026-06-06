# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-05-14 19:00  
> **Duration:** 9m 06s  
> **Total tokens:** 53,682 (input: 34,906 / output: 18,776)

> **Benchmark suite:** screening_ladder  
> **Review key:** iud_insertion_pain_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full  
> **Dataset split:** random_test  
> **Studies:** 50  
> **Gatekeeper preset:** deepseek_v4_pro--xhigh  
> **Gatekeeper model:** deepseek-v4-pro--xhigh [DeepSeek V4 Pro]  
> **Orchestrator preset:** deepseek_v4_pro--xhigh  
> **Orchestrator model:** deepseek-v4-pro--xhigh [DeepSeek V4 Pro]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 3 | 9m 06s | 13,739 / 4,865 |
| Gatekeeper | 1 | 6m 41s | 21,167 / 13,911 |
| **Total** | **4** | **9m 06s** | **34,906 / 18,776** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*19:01:25 — 43s — 4,967 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*19:08:43 — 7m 17s — 41,092 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Final Output (Orchestrator)

*19:09:49 — 1m 05s — 7,623 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
