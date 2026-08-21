# Pipeline Activity Log

> **Review:** Doppler trans‐thoracic echocardiography for detection of pulmonary hypertension in adults  
> **Date:** 2026-08-18 15:23  
> **Duration:** 15m 18s  
> **Total tokens:** 1,267,476 (input: 1,239,571 / output: 27,905)

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
| Orchestrator | 5 | 15m 18s | 26,702 / 1,529 |
| Gatekeeper | 12 | 14m 31s | 1,212,869 / 26,376 |
| **Total** | **17** | **15m 18s** | **1,239,571 / 27,905** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*15:23:22 — 10s — 4,589 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*15:38:19 — 14m 57s — 1,244,499 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*15:38:25 — 5s — 5,930 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator (python_interpreter)

*15:38:29 — 4s — 6,140 tokens*

The orchestrator executed step 4. Used tools: python_interpreter.

---

### 5. Final Output (Orchestrator)

*15:38:30 — 2s — 6,318 tokens*

The orchestrator executed step 5. Used tools: python_interpreter. Produced the final output.

---
