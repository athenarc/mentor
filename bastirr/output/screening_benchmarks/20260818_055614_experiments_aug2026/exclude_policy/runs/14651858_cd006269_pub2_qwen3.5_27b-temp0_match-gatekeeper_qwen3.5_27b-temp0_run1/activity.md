# Pipeline Activity Log

> **Review:** Concomitant hyperthermia and radiation therapy for treating locally advanced rectal cancer  
> **Date:** 2026-08-18 05:56  
> **Duration:** 1h 18m  
> **Total tokens:** 453,950 (input: 310,143 / output: 143,807)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd006269_pub2  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD006269.pub2/full  
> **Dataset split:** val  
> **Studies:** 46  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 1h 18m | 23,250 / 1,879 |
| Gatekeeper | 6 | 1h 17m | 286,893 / 141,928 |
| **Total** | **10** | **1h 18m** | **310,143 / 143,807** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*05:56:26 — 11s — 3,817 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*07:14:15 — 1h 17m — 433,436 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*07:14:31 — 16s — 5,499 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*07:14:40 — 9s — 11,198 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
