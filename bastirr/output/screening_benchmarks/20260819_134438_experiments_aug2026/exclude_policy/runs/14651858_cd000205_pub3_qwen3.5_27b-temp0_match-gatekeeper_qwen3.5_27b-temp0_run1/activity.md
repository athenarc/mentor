# Pipeline Activity Log

> **Review:** Benzodiazepines for antipsychotic‐induced tardive dyskinesia  
> **Date:** 2026-08-19 13:44  
> **Duration:** 34m 26s  
> **Total tokens:** 805,257 (input: 734,877 / output: 70,380)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd000205_pub3  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000205.pub3/full  
> **Dataset split:** dev  
> **Studies:** 54  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 9 | 34m 25s | 82,176 / 4,492 |
| Gatekeeper | 11 | 31m 42s | 652,701 / 65,888 |
| **Total** | **20** | **34m 26s** | **734,877 / 70,380** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*13:45:14 — 20s — 4,225 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*13:50:20 — 5m 05s — 111,948 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*13:50:26 — 6s — 5,625 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'evidence_saved = save_screening_evidence_json(
    screening_response=gatekeeper_response,
    output_dir=output_dir,
    expected_n_studies=expected_n_studies
)' due to: ValueError: Incomplete screening response: expected 54 parsed decisions, found 7. Do not save part

---

### 4. Orchestrator → Gatekeeper

*13:56:57 — 6m 30s — 114,440 tokens*

The orchestrator executed step 4. Used tools: python_interpreter.

---

### 5. Orchestrator → Gatekeeper

*13:59:43 — 2m 46s — 112,700 tokens*

The orchestrator executed step 5. Used tools: python_interpreter.

---

### 6. Orchestrator → Gatekeeper

*14:18:31 — 18m 48s — 408,767 tokens*

The orchestrator executed step 6. Used tools: python_interpreter.

---

### 7. Orchestrator (python_interpreter)

*14:18:40 — 9s — 12,229 tokens*

The orchestrator executed step 7. Used tools: python_interpreter.

---

### 8. Orchestrator (python_interpreter)

*14:18:58 — 19s — 17,519 tokens*

The orchestrator executed step 8. Used tools: python_interpreter.

---

### 9. Final Output (Orchestrator)

*14:19:20 — 21s — 17,804 tokens*

The orchestrator executed step 9. Used tools: python_interpreter. Produced the final output.

---
