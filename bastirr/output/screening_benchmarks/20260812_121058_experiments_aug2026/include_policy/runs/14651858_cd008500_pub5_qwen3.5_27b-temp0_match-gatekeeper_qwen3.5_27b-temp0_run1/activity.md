# Pipeline Activity Log

> **Review:** Primary prophylaxis for venous thromboembolism in ambulatory cancer patients receiving chemotherapy  
> **Date:** 2026-08-12 12:10  
> **Duration:** 23m 05s  
> **Total tokens:** 676,453 (input: 611,535 / output: 64,918)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd008500_pub5  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD008500.pub5/full  
> **Dataset split:** val  
> **Studies:** 83  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 23m 04s | 17,976 / 1,292 |
| Gatekeeper | 5 | 22m 39s | 593,559 / 63,626 |
| **Total** | **9** | **23m 05s** | **611,535 / 64,918** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*12:11:09 — 10s — 4,175 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*12:33:55 — 22m 45s — 661,728 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*12:34:01 — 6s — 5,179 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*12:34:04 — 3s — 5,371 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
