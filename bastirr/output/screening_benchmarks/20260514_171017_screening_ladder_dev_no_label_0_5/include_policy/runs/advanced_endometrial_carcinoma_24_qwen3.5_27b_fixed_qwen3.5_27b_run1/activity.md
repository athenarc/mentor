# Pipeline Activity Log

> **Review:** Chemotherapy for advanced, recurrent or metastatic endometrial carcinoma  
> **Date:** 2026-05-14 17:13  
> **Duration:** 4m 25s  
> **Total tokens:** 174,970 (input: 161,921 / output: 13,049)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Review key:** advanced_endometrial_carcinoma_24  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD003915.pub4/full  
> **Dataset split:** dev  
> **Studies:** 24  
> **Gatekeeper preset:** qwen3.5_27b  
> **Gatekeeper model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator preset:** qwen3.5_27b  
> **Orchestrator model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 4m 25s | 22,577 / 1,352 |
| Gatekeeper | 4 | 3m 56s | 139,344 / 11,697 |
| **Total** | **8** | **4m 25s** | **161,921 / 13,049** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*17:13:35 — 8s — 3,962 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*17:17:37 — 4m 01s — 155,304 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*17:17:49 — 12s — 7,620 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*17:17:52 — 3s — 8,084 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
