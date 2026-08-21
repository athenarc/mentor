# Pipeline Activity Log

> **Review:** Paracetamol (acetaminophen) with or without an antiemetic for acute migraine headaches in adults  
> **Date:** 2026-08-19 06:39  
> **Duration:** 9m 25s  
> **Total tokens:** 450,607 (input: 427,108 / output: 23,499)

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
| Orchestrator | 5 | 9m 25s | 23,324 / 1,401 |
| Gatekeeper | 5 | 8m 59s | 403,784 / 22,098 |
| **Total** | **10** | **9m 25s** | **427,108 / 23,499** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*06:39:51 — 9s — 4,091 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator (python_interpreter)

*06:39:54 — 4s — 4,383 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator → Gatekeeper

*06:49:00 — 9m 05s — 430,859 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator (python_interpreter)

*06:49:06 — 6s — 5,492 tokens*

The orchestrator executed step 4. Used tools: python_interpreter.

---

### 5. Final Output (Orchestrator)

*06:49:08 — 2s — 5,782 tokens*

The orchestrator executed step 5. Used tools: python_interpreter. Produced the final output.

---
