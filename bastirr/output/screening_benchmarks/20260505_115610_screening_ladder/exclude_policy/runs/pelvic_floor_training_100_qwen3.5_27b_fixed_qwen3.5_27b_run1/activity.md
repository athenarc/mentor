# Pipeline Activity Log

> **Review:** Pelvic floor muscle training versus no treatment, or inactive control treatments, for urinary incontinence in women  
> **Date:** 2026-05-05 12:16  
> **Duration:** 5m 51s  
> **Total tokens:** 250,427 (input: 225,729 / output: 24,698)

> **Benchmark suite:** screening_ladder  
> **Review key:** pelvic_floor_training_100  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005654.pub4/full  
> **Dataset split:** random_test  
> **Studies:** 100  
> **Gatekeeper preset:** qwen3.5_27b  
> **Gatekeeper model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator preset:** qwen3.5_27b  
> **Orchestrator model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 5m 51s | 18,774 / 1,424 |
| Gatekeeper | 4 | 5m 23s | 206,955 / 23,274 |
| **Total** | **8** | **5m 51s** | **225,729 / 24,698** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*12:16:34 — 14s — 4,284 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*12:22:04 — 5m 29s — 234,968 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*12:22:09 — 5s — 5,476 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*12:22:12 — 3s — 5,699 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
