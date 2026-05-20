# Pipeline Activity Log

> **Review:** Factors that influence the provision of home‐based rehabilitation services for people needing rehabilitation: a qualitative evidence synthesis  
> **Date:** 2026-05-14 17:45  
> **Duration:** 5m 42s  
> **Total tokens:** 560,287 (input: 542,453 / output: 17,834)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Review key:** home_based_rehabilitation_183  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD014823/full  
> **Dataset split:** dev  
> **Studies:** 183  
> **Gatekeeper preset:** qwen3.5_27b  
> **Gatekeeper model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator preset:** qwen3.5_27b  
> **Orchestrator model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 5m 42s | 18,403 / 1,197 |
| Gatekeeper | 6 | 5m 18s | 524,050 / 16,637 |
| **Total** | **10** | **5m 42s** | **542,453 / 17,834** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*17:45:38 — 8s — 4,040 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*17:51:02 — 5m 24s — 545,325 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*17:51:09 — 7s — 5,275 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*17:51:12 — 3s — 5,647 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
