# Pipeline Activity Log

> **Review:** mHealth education interventions in heart failure  
> **Date:** 2026-05-29 01:58  
> **Duration:** 9m 11s  
> **Total tokens:** 240,155 (input: 209,670 / output: 30,485)

> **Benchmark suite:** screening_ladder  
> **Review key:** heart_failure_mhealth_200  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011845.pub2/full  
> **Dataset split:** heart_test  
> **Studies:** 200  
> **Gatekeeper preset:** deepseek_v4_pro--xhigh  
> **Gatekeeper model:** deepseek-v4-pro--xhigh [DeepSeek V4 Pro]  
> **Orchestrator preset:** deepseek_v4_pro--xhigh  
> **Orchestrator model:** deepseek-v4-pro--xhigh [DeepSeek V4 Pro]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 9m 11s | 30,069 / 3,273 |
| Gatekeeper | 2 | 8m 05s | 179,601 / 27,212 |
| **Total** | **6** | **9m 11s** | **209,670 / 30,485** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:58:51 — 33s — 5,305 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*02:07:11 — 8m 19s — 211,408 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*02:07:17 — 6s — 5,256 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*02:07:30 — 13s — 18,186 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
