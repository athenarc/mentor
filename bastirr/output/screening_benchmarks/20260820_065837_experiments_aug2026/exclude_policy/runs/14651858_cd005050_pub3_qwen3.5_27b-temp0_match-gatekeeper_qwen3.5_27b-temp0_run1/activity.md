# Pipeline Activity Log

> **Review:** Influenza vaccines for preventing cardiovascular disease  
> **Date:** 2026-08-20 06:58  
> **Duration:** 6m 09s  
> **Total tokens:** 644,195 (input: 630,693 / output: 13,502)

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
| Orchestrator | 4 | 6m 08s | 17,564 / 1,239 |
| Gatekeeper | 9 | 5m 39s | 613,129 / 12,263 |
| **Total** | **13** | **6m 09s** | **630,693 / 13,502** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*06:58:49 — 11s — 3,738 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*07:04:38 — 5m 48s — 629,649 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*07:04:45 — 6s — 5,157 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*07:04:48 — 3s — 5,651 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
