# Pipeline Activity Log

> **Review:** Routine provision of feedback from patient‐reported outcome measurements to healthcare providers and patients in clinical practice  
> **Date:** 2026-05-12 16:17  
> **Duration:** 13m 10s  
> **Total tokens:** 496,461 (input: 453,244 / output: 43,217)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Review key:** prom_feedback_194  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011589.pub2/full  
> **Dataset split:** dev  
> **Studies:** 194  
> **Gatekeeper preset:** qwen3.5_27b  
> **Gatekeeper model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator preset:** qwen3.5_27b  
> **Orchestrator model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 13m 10s | 17,481 / 1,225 |
| Gatekeeper | 4 | 12m 46s | 435,763 / 41,992 |
| **Total** | **8** | **13m 10s** | **453,244 / 43,217** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*16:17:27 — 5s — 3,763 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*16:30:22 — 12m 55s — 482,106 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*16:30:30 — 7s — 5,132 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*16:30:32 — 3s — 5,460 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
