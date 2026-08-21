# Pipeline Activity Log

> **Review:** Pars plana vitrectomy with internal limiting membrane flap versus pars plana vitrectomy with conventional internal limiting membrane peeling for large macular hole  
> **Date:** 2026-08-21 16:34  
> **Duration:** 11m 22s  
> **Total tokens:** 120,154 (input: 104,286 / output: 15,868)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd015031_pub2  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD015031.pub2/full  
> **Dataset split:** dev  
> **Studies:** 50  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 11m 22s | 17,742 / 1,203 |
| Gatekeeper | 3 | 10m 39s | 86,544 / 14,665 |
| **Total** | **7** | **11m 22s** | **104,286 / 15,868** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*16:34:27 — 5s — 3,990 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*16:45:22 — 10m 54s — 105,559 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*16:45:42 — 20s — 5,100 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*16:45:45 — 3s — 5,505 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
