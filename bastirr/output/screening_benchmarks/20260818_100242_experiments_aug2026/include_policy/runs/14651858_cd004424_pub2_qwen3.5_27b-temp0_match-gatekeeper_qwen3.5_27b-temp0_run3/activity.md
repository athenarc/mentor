# Pipeline Activity Log

> **Review:** Antiepileptic drugs for preventing seizures in people with brain tumors  
> **Date:** 2026-08-18 10:09  
> **Duration:** 3m 06s  
> **Total tokens:** 100,248 (input: 89,849 / output: 10,399)

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
| Orchestrator | 4 | 3m 06s | 17,886 / 1,095 |
| Gatekeeper | 4 | 2m 35s | 71,963 / 9,304 |
| **Total** | **8** | **3m 06s** | **89,849 / 10,399** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*10:10:03 — 6s — 3,947 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*10:12:43 — 2m 40s — 85,772 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*10:13:01 — 17s — 5,147 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*10:13:03 — 2s — 5,382 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
