# Pipeline Activity Log

> **Review:** Red blood cell transfusion to treat or prevent complications in sickle cell disease: an overview of Cochrane reviews  
> **Date:** 2026-08-18 11:43  
> **Duration:** 2m 48s  
> **Total tokens:** 115,627 (input: 103,811 / output: 11,816)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd012082_pub2  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD012082.pub2/full  
> **Dataset split:** dev  
> **Studies:** 37  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 2m 48s | 18,609 / 1,342 |
| Gatekeeper | 3 | 2m 25s | 85,202 / 10,474 |
| **Total** | **7** | **2m 48s** | **103,811 / 11,816** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*11:43:24 — 8s — 4,092 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*11:45:53 — 2m 29s — 100,353 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*11:45:59 — 6s — 5,407 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*11:46:05 — 6s — 5,775 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
