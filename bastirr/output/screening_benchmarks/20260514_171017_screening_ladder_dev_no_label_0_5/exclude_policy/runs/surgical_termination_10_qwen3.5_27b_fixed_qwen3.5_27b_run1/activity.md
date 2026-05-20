# Pipeline Activity Log

> **Review:** Surgical methods for first trimester termination of pregnancy  
> **Date:** 2026-05-14 17:10  
> **Duration:** 2m 51s  
> **Total tokens:** 73,029 (input: 63,702 / output: 9,327)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Review key:** surgical_termination_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD002900/full  
> **Dataset split:** dev  
> **Studies:** 10  
> **Gatekeeper preset:** qwen3.5_27b  
> **Gatekeeper model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator preset:** qwen3.5_27b  
> **Orchestrator model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 3 | 2m 51s | 13,051 / 1,128 |
| Gatekeeper | 3 | 2m 30s | 50,651 / 8,199 |
| **Total** | **6** | **2m 51s** | **63,702 / 9,327** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*17:10:36 — 10s — 4,007 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*17:13:12 — 2m 35s — 63,240 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Final Output (Orchestrator)

*17:13:18 — 6s — 5,782 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
