# Pipeline Activity Log

> **Review:** mHealth education interventions in heart failure  
> **Date:** 2026-05-05 12:22  
> **Duration:** 9m 46s  
> **Total tokens:** 913,158 (input: 885,510 / output: 27,648)

> **Benchmark suite:** screening_ladder  
> **Review key:** heart_failure_mhealth_200  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011845.pub2/full  
> **Dataset split:** heart_test  
> **Studies:** 200  
> **Gatekeeper preset:** qwen3.5_27b  
> **Gatekeeper model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator preset:** qwen3.5_27b  
> **Orchestrator model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 9m 46s | 17,849 / 1,339 |
| Gatekeeper | 8 | 9m 15s | 867,661 / 26,309 |
| **Total** | **12** | **9m 46s** | **885,510 / 27,648** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*12:22:23 — 10s — 4,145 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*12:31:45 — 9m 22s — 898,351 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*12:31:54 — 9s — 5,084 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*12:31:59 — 5s — 5,578 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
