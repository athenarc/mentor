# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-05-29 01:44  
> **Duration:** 8m 55s  
> **Total tokens:** 92,916 (input: 69,985 / output: 22,931)

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
| Orchestrator | 4 | 8m 55s | 16,898 / 4,707 |
| Gatekeeper | 2 | 4m 28s | 53,087 / 18,224 |
| **Total** | **6** | **8m 55s** | **69,985 / 22,931** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:45:49 — 1m 15s — 7,633 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:50:24 — 4m 34s — 75,561 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*01:50:27 — 3s — 4,690 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*01:53:29 — 3m 02s — 5,032 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
