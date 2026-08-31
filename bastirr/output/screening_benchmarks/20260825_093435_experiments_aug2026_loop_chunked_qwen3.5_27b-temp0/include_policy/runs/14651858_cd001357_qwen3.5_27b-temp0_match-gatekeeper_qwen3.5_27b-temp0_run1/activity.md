# Pipeline Activity Log

> **Review:** Amisulpride for schizophrenia  
> **Date:** 2026-08-25 09:34  
> **Duration:** 14m 07s  
> **Total tokens:** 257,095 (input: 220,824 / output: 36,271)

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
| Orchestrator | 10 | 14m 06s | 46,830 / 2,851 |
| Gatekeeper | 9 | 12m 46s | 173,994 / 33,420 |
| **Total** | **19** | **14m 07s** | **220,824 / 36,271** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*09:35:01 — 9s — 4,011 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*09:43:56 — 8m 55s — 122,224 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*09:44:06 — 10s — 4,906 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'append_result = append_screening_chunk_decisions_json(
    screening_response=gatekeeper_response,
    output_dir=output_dir,
    expected_study_indices_json=chunk_study_indices_json,
    expected_n_studies=expected_n_studies
)' due to: ValueError: Chunk response did n

---

### 4. Orchestrator → Gatekeeper

*09:46:20 — 2m 13s — 58,048 tokens*

The orchestrator executed step 4. Used tools: python_interpreter.

---

### 5. Orchestrator (python_interpreter)

*09:46:25 — 5s — 6,246 tokens*

The orchestrator executed step 5. Used tools: python_interpreter.

---

### 6. Final Output (Orchestrator)

*09:46:29 — 4s — 6,687 tokens*

The orchestrator executed step 6. Used tools: python_interpreter. Produced the final output.

---

### 7. Orchestrator (python_interpreter)

*09:46:40 — 11s — 3,869 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 8. Orchestrator → Gatekeeper

*09:48:34 — 1m 53s — 41,387 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 9. Orchestrator (python_interpreter)

*09:48:51 — 18s — 4,658 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 10. Final Output (Orchestrator)

*09:48:59 — 8s — 5,059 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
