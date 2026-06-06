# Pipeline Activity Log

> **Review:** Chemotherapy for advanced, recurrent or metastatic endometrial carcinoma  
> **Date:** 2026-05-29 04:22  
> **Duration:** 6m 28s  
> **Total tokens:** 270,486 (input: 251,202 / output: 19,284)

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
| Orchestrator | 4 | 6m 28s | 20,810 / 1,066 |
| Gatekeeper | 5 | 6m 00s | 230,392 / 18,218 |
| **Total** | **9** | **6m 28s** | **251,202 / 19,284** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*04:22:08 — 6s — 3,763 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*04:28:16 — 6m 08s — 252,763 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*04:28:26 — 10s — 6,769 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*04:28:30 — 4s — 7,191 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
