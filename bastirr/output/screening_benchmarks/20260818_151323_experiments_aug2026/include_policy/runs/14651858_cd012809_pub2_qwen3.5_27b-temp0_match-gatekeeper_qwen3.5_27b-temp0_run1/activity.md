# Pipeline Activity Log

> **Review:** Doppler trans‐thoracic echocardiography for detection of pulmonary hypertension in adults  
> **Date:** 2026-08-18 15:13  
> **Duration:** 9m 18s  
> **Total tokens:** 309,116 (input: 278,733 / output: 30,383)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd012809_pub2  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD012809.pub2/full  
> **Dataset split:** dev  
> **Studies:** 155  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 9m 17s | 19,336 / 1,373 |
| Gatekeeper | 3 | 8m 39s | 259,397 / 29,010 |
| **Total** | **7** | **9m 18s** | **278,733 / 30,383** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*15:13:48 — 8s — 4,091 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*15:22:41 — 8m 52s — 293,164 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*15:22:54 — 14s — 5,743 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*15:22:57 — 3s — 6,118 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
