# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-05-12 15:54  
> **Duration:** 3m 39s  
> **Total tokens:** 126,619 (input: 112,854 / output: 13,765)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Review key:** adhesive_capsulitis_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full  
> **Dataset split:** dev  
> **Studies:** 50  
> **Gatekeeper preset:** qwen3.5_27b  
> **Gatekeeper model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator preset:** qwen3.5_27b  
> **Orchestrator model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 3m 39s | 17,969 / 1,311 |
| Gatekeeper | 3 | 3m 12s | 94,885 / 12,454 |
| **Total** | **7** | **3m 39s** | **112,854 / 13,765** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*15:54:52 — 9s — 4,115 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*15:58:14 — 3m 22s — 111,881 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*15:58:19 — 5s — 5,189 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*15:58:22 — 3s — 5,434 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
