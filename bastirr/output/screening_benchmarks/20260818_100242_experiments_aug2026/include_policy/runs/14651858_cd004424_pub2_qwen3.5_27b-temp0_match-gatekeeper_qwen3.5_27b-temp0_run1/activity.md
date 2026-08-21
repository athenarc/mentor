# Pipeline Activity Log

> **Review:** Antiepileptic drugs for preventing seizures in people with brain tumors  
> **Date:** 2026-08-18 10:02  
> **Duration:** 4m 21s  
> **Total tokens:** 217,792 (input: 205,011 / output: 12,781)

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
| Orchestrator | 4 | 4m 20s | 57,340 / 1,008 |
| Gatekeeper | 6 | 3m 42s | 147,671 / 11,773 |
| **Total** | **10** | **4m 21s** | **205,011 / 12,781** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*10:03:11 — 12s — 3,849 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*10:07:02 — 3m 51s — 174,719 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*10:07:14 — 12s — 19,472 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*10:07:19 — 4s — 19,752 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
