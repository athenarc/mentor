# Pipeline Activity Log

> **Review:** Paracetamol (acetaminophen) with or without an antiemetic for acute migraine headaches in adults  
> **Date:** 2026-08-19 06:28  
> **Duration:** 11m 16s  
> **Total tokens:** 315,982 (input: 298,198 / output: 17,784)

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
| Orchestrator | 4 | 11m 15s | 25,934 / 896 |
| Gatekeeper | 4 | 10m 11s | 272,264 / 16,888 |
| **Total** | **8** | **11m 16s** | **298,198 / 17,784** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*06:28:47 — 34s — 3,944 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*06:39:15 — 10m 28s — 293,624 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*06:39:25 — 11s — 9,046 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*06:39:27 — 2s — 9,368 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
