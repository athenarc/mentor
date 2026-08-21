# Pipeline Activity Log

> **Review:** Antiepileptic drugs for preventing seizures in people with brain tumors  
> **Date:** 2026-08-18 10:07  
> **Duration:** 2m 08s  
> **Total tokens:** 133,186 (input: 126,771 / output: 6,415)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd004424_pub2  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004424.pub2/full  
> **Dataset split:** dev  
> **Studies:** 33  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 3 | 2m 08s | 12,674 / 982 |
| Gatekeeper | 4 | 1m 35s | 114,097 / 5,433 |
| **Total** | **7** | **2m 08s** | **126,771 / 6,415** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*10:07:53 — 20s — 3,946 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*10:09:36 — 1m 42s — 124,074 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Final Output (Orchestrator)

*10:09:42 — 6s — 5,166 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
