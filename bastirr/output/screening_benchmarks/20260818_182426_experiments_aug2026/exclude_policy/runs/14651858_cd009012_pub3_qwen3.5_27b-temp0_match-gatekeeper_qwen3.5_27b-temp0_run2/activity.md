# Pipeline Activity Log

> **Review:** Early versus delayed antiretroviral treatment in HIV‐positive people with cryptococcal meningitis  
> **Date:** 2026-08-18 18:29  
> **Duration:** 2m 53s  
> **Total tokens:** 126,508 (input: 117,814 / output: 8,694)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd009012_pub3  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD009012.pub3/full  
> **Dataset split:** dev  
> **Studies:** 30  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 2m 53s | 17,539 / 1,271 |
| Gatekeeper | 3 | 2m 11s | 100,275 / 7,423 |
| **Total** | **7** | **2m 53s** | **117,814 / 8,694** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*18:29:23 — 5s — 3,915 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*18:31:44 — 2m 20s — 111,943 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*18:31:53 — 9s — 5,086 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*18:32:11 — 18s — 5,564 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
