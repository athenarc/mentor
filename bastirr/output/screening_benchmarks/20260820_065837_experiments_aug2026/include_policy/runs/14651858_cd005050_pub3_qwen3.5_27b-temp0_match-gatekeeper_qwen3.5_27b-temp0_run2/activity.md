# Pipeline Activity Log

> **Review:** Influenza vaccines for preventing cardiovascular disease  
> **Date:** 2026-08-20 07:04  
> **Duration:** 3m 26s  
> **Total tokens:** 220,674 (input: 206,952 / output: 13,722)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd005050_pub3  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005050.pub3/full  
> **Dataset split:** heart_test  
> **Studies:** 56  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 3m 26s | 17,782 / 1,195 |
| Gatekeeper | 3 | 3m 01s | 189,170 / 12,527 |
| **Total** | **7** | **3m 26s** | **206,952 / 13,722** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*07:04:53 — 5s — 3,739 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*07:08:00 — 3m 06s — 205,992 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*07:08:13 — 13s — 5,247 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*07:08:15 — 2s — 5,696 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
