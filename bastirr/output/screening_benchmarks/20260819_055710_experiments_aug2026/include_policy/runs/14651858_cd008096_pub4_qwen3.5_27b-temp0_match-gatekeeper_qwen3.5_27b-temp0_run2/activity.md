# Pipeline Activity Log

> **Review:** Percutaneous endoscopic gastrostomy versus nasogastric tube feeding for adults with swallowing disturbances  
> **Date:** 2026-08-19 06:11  
> **Duration:** 5m 36s  
> **Total tokens:** 208,277 (input: 186,795 / output: 21,482)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd008096_pub4  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD008096.pub4/full  
> **Dataset split:** dev  
> **Studies:** 66  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 5m 36s | 17,447 / 1,086 |
| Gatekeeper | 4 | 5m 01s | 169,348 / 20,396 |
| **Total** | **8** | **5m 36s** | **186,795 / 21,482** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*06:11:35 — 6s — 3,856 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*06:16:53 — 5m 18s — 194,013 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*06:17:03 — 10s — 4,992 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*06:17:06 — 2s — 5,416 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
