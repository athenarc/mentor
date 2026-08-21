# Pipeline Activity Log

> **Review:** Carbamazepine versus phenytoin monotherapy for epilepsy: an individual participant data review  
> **Date:** 2026-08-20 02:32  
> **Duration:** 3m 15s  
> **Total tokens:** 240,688 (input: 228,078 / output: 12,610)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd001911_pub4  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001911.pub4/full  
> **Dataset split:** dev  
> **Studies:** 57  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 3 | 3m 14s | 13,936 / 1,085 |
| Gatekeeper | 6 | 2m 58s | 214,142 / 11,525 |
| **Total** | **9** | **3m 15s** | **228,078 / 12,610** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*02:32:32 — 8s — 4,222 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*02:35:35 — 3m 02s — 230,520 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Final Output (Orchestrator)

*02:35:39 — 4s — 5,946 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
