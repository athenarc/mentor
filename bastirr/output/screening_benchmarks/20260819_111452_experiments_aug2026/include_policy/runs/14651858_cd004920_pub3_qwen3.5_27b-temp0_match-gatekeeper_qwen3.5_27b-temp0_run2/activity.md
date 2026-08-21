# Pipeline Activity Log

> **Review:** Antifungal agents for preventing fungal infections in non‐neutropenic critically ill patients  
> **Date:** 2026-08-19 11:29  
> **Duration:** 11m 39s  
> **Total tokens:** 276,716 (input: 256,448 / output: 20,268)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd004920_pub3  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004920.pub3/full  
> **Dataset split:** dev  
> **Studies:** 70  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 11m 39s | 19,417 / 1,441 |
| Gatekeeper | 5 | 11m 12s | 237,031 / 18,827 |
| **Total** | **9** | **11m 39s** | **256,448 / 20,268** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*11:29:30 — 10s — 4,199 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*11:40:48 — 11m 18s — 260,713 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*11:40:54 — 6s — 5,685 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*11:40:59 — 5s — 6,119 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
