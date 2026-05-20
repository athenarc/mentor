# Pipeline Activity Log

> **Review:** Factors that influence the provision of home‐based rehabilitation services for people needing rehabilitation: a qualitative evidence synthesis  
> **Date:** 2026-05-14 16:20  
> **Duration:** 12m 39s  
> **Total tokens:** 1,284,958 (input: 1,219,273 / output: 65,685)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Review key:** home_based_rehabilitation_183  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD014823/full  
> **Dataset split:** dev  
> **Studies:** 183  
> **Gatekeeper preset:** qwen3.5_122b_a10b  
> **Gatekeeper model:** qwen3.5-122b-a10b [Qwen 3.5 122B A10B]  
> **Orchestrator preset:** qwen3.5_122b_a10b  
> **Orchestrator model:** qwen3.5-122b-a10b [Qwen 3.5 122B A10B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 5 | 12m 39s | 502,046 / 1,578 |
| Gatekeeper | 7 | 11m 22s | 717,227 / 64,107 |
| **Total** | **12** | **12m 39s** | **1,219,273 / 65,685** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*16:20:04 — 3s — 3,826 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'print(f"Candidates loaded: {len(candidates_json.get('studies', []))}")' due to: InterpreterError: Object {"title": "Factors that influence the provision of home‐based rehabilitation services for people needing rehabilitation: a qualitative evidence synthesis", "objecti

---

### 2. Orchestrator (python_interpreter)

*16:20:22 — 19s — 72,778 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'print(f"Number of studies: {len(candidates_data.get('studies', []))}")' due to: InterpreterError: Object {"title": "Factors that influence the provision of home‐based rehabilitation services for people needing rehabilitation: a qualitative evidence synthesis", "objecti

---

### 3. Orchestrator (python_interpreter)

*16:20:57 — 35s — 141,655 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator → Gatekeeper

*16:27:18 — 6m 20s — 618,662 tokens*

The orchestrator executed step 4. Used tools: python_interpreter.

---

### 5. Orchestrator → Gatekeeper

*16:32:40 — 5m 22s — 448,037 tokens*

The orchestrator executed step 5. Used tools: python_interpreter. Produced the final output.

---
