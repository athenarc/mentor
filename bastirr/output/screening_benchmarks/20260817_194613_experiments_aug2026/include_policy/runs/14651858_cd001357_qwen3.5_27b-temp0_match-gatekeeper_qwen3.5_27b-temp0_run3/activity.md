# Pipeline Activity Log

> **Review:** Amisulpride for schizophrenia  
> **Date:** 2026-08-17 20:00  
> **Duration:** 25m 56s  
> **Total tokens:** 445,507 (input: 403,279 / output: 42,228)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd001357  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001357/full  
> **Dataset split:** dev  
> **Studies:** 31  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 6 | 25m 56s | 28,031 / 1,464 |
| Gatekeeper | 7 | 25m 12s | 375,248 / 40,764 |
| **Total** | **13** | **25m 56s** | **403,279 / 42,228** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*20:00:33 — 13s — 3,979 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator (python_interpreter)

*20:00:38 — 5s — 4,266 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator → Gatekeeper

*20:26:02 — 25m 24s — 420,679 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator (python_interpreter)

*20:26:12 — 10s — 5,287 tokens*

The orchestrator executed step 4. Used tools: python_interpreter.

---

### 5. Orchestrator (python_interpreter)

*20:26:14 — 2s — 5,515 tokens*

The orchestrator executed step 5. Used tools: python_interpreter.

---

### 6. Final Output (Orchestrator)

*20:26:17 — 3s — 5,781 tokens*

The orchestrator executed step 6. Used tools: python_interpreter. Produced the final output.

---
