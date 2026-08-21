# Pipeline Activity Log

> **Review:** Paracetamol (acetaminophen) with or without an antiemetic for acute migraine headaches in adults  
> **Date:** 2026-08-19 06:49  
> **Duration:** 5m 50s  
> **Total tokens:** 178,181 (input: 164,282 / output: 13,899)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd008040_pub3  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD008040.pub3/full  
> **Dataset split:** dev  
> **Studies:** 61  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 5m 49s | 18,411 / 1,397 |
| Gatekeeper | 4 | 5m 20s | 145,871 / 12,502 |
| **Total** | **8** | **5m 50s** | **164,282 / 13,899** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*06:49:33 — 11s — 4,218 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*06:54:59 — 5m 25s — 162,970 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*06:55:08 — 9s — 5,281 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*06:55:12 — 5s — 5,712 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
