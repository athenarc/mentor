# Pipeline Activity Log

> **Review:** Factors that influence the provision of home‐based rehabilitation services for people needing rehabilitation: a qualitative evidence synthesis  
> **Date:** 2026-05-29 04:37  
> **Duration:** 23m 30s  
> **Total tokens:** 1,396,542 (input: 1,328,244 / output: 68,298)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Review key:** home_based_rehabilitation_183  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD014823/full  
> **Dataset split:** dev  
> **Studies:** 183  
> **Gatekeeper preset:** qwen3.5_27b  
> **Gatekeeper model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator preset:** qwen3.5_27b  
> **Orchestrator model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 7 | 23m 30s | 38,876 / 2,227 |
| Gatekeeper | 10 | 22m 31s | 1,289,368 / 66,071 |
| **Total** | **17** | **23m 30s** | **1,328,244 / 68,298** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*04:37:59 — 11s — 4,245 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*04:43:57 — 5m 57s — 645,293 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*04:44:03 — 6s — 5,215 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'evidence_saved = save_screening_evidence_json(
    screening_response=gatekeeper_response,
    output_dir=output_dir,
    expected_n_studies=expected_n_studies
)' due to: ValueError: Incomplete screening response: expected 183 parsed decisions, found 0. Do not save par

---

### 4. Orchestrator → Gatekeeper

*04:57:39 — 13m 36s — 565,946 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'gatekeeper_response = gatekeeper(task=gatekeeper_task, additional_args={"selection_criteria": selection_criteria, "candidates_json": candidates_json})' due to: AgentGenerationError: Error in generating model output:
Error code: 400 - {'error': {'message': "This endpoin

---

### 5. Orchestrator → Gatekeeper

*05:01:09 — 3m 30s — 161,253 tokens*

The orchestrator executed step 5. Used tools: python_interpreter.

---

### 6. Orchestrator (python_interpreter)

*05:01:15 — 6s — 7,114 tokens*

The orchestrator executed step 6. Used tools: python_interpreter.

---

### 7. Final Output (Orchestrator)

*05:01:19 — 4s — 7,476 tokens*

The orchestrator executed step 7. Used tools: python_interpreter. Produced the final output.

---
