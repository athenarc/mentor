# Pipeline Activity Log

> **Review:** Amisulpride for schizophrenia  
> **Date:** 2026-08-25 09:49  
> **Duration:** 12m 03s  
> **Total tokens:** 180,949 (input: 153,047 / output: 27,902)

> **Benchmark suite:** experiments_aug2026  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** 14651858_cd001357  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001357/full  
> **Dataset split:** dev  
> **Studies:** 31  
> **Chunk count:** 2  
> **Chunk sizes:** 20, 11  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Orchestrator max steps:** 20  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 8 | 12m 03s | 34,740 / 2,114 |
| Gatekeeper | 6 | 9m 44s | 118,307 / 25,788 |
| **Total** | **14** | **12m 03s** | **153,047 / 27,902** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*09:49:47 — 32s — 4,093 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*09:55:36 — 5m 48s — 109,458 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*09:55:47 — 12s — 5,028 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*09:55:52 — 5s — 5,202 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 5. Orchestrator (python_interpreter)

*09:56:04 — 12s — 3,884 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'chunk_study_indices_json = json.dumps(chunk_study_indices)' due to: InterpreterError: The variable `json` is not defined.

---

### 6. Orchestrator (python_interpreter)

*09:56:11 — 7s — 4,114 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 7. Orchestrator → Gatekeeper

*10:01:07 — 4m 55s — 43,919 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 8. Final Output (Orchestrator)

*10:01:18 — 12s — 5,251 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
