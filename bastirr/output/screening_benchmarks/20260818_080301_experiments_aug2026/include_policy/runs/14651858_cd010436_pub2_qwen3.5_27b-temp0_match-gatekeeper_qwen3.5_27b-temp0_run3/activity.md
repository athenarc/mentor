# Pipeline Activity Log

> **Review:** Steroid‐eluting sinus stents for improving symptoms in chronic rhinosinusitis patients undergoing functional endoscopic sinus surgery  
> **Date:** 2026-08-18 08:13  
> **Duration:** 5m 15s  
> **Total tokens:** 171,943 (input: 157,283 / output: 14,660)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd010436_pub2  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD010436.pub2/full  
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
| Orchestrator | 4 | 5m 15s | 18,187 / 1,249 |
| Gatekeeper | 4 | 4m 48s | 139,096 / 13,411 |
| **Total** | **8** | **5m 15s** | **157,283 / 14,660** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*08:13:13 — 7s — 3,892 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*08:18:09 — 4m 55s — 156,968 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*08:18:19 — 11s — 5,293 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*08:18:21 — 2s — 5,790 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
