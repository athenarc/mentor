# Pipeline Activity Log

> **Review:** Psychological therapies for the treatment of anxiety disorders in chronic obstructive pulmonary disease  
> **Date:** 2026-08-18 18:54  
> **Duration:** 19m 45s  
> **Total tokens:** 288,192 (input: 207,350 / output: 80,842)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd010673_pub2  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD010673.pub2/full  
> **Dataset split:** dev  
> **Studies:** 58  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 3 | 19m 44s | 13,405 / 1,073 |
| Gatekeeper | 5 | 18m 55s | 193,945 / 79,769 |
| **Total** | **8** | **19m 45s** | **207,350 / 80,842** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*18:55:14 — 20s — 4,254 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*19:14:33 — 19m 18s — 278,448 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Final Output (Orchestrator)

*19:14:38 — 6s — 5,490 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
