# Pipeline Activity Log

> **Review:** Amisulpride for schizophrenia  
> **Date:** 2026-08-17 19:46  
> **Duration:** 8m 24s  
> **Total tokens:** 342,454 (input: 325,115 / output: 17,339)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd001357  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001357/full  
> **Dataset split:** dev  
> **Studies:** 31  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 8 | 8m 23s | 44,134 / 2,060 |
| Gatekeeper | 10 | 7m 39s | 280,981 / 15,279 |
| **Total** | **18** | **8m 24s** | **325,115 / 17,339** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*19:46:38 — 8s — 3,977 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator (python_interpreter)

*19:46:41 — 3s — 4,254 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator → Gatekeeper

*19:50:52 — 4m 11s — 136,837 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator (python_interpreter)

*19:50:56 — 4s — 5,290 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'evidence_saved = save_screening_evidence_json(
    screening_response=gatekeeper_response,
    output_dir=output_dir,
    expected_n_studies=expected_n_studies
)' due to: ValueError: Incomplete screening response: expected 31 parsed decisions, found 0. Do not save part

---

### 5. Orchestrator (python_interpreter)

*19:50:59 — 3s — 5,627 tokens*

The orchestrator executed step 5. Used tools: python_interpreter.

---

### 6. Orchestrator → Gatekeeper

*19:54:42 — 3m 43s — 171,034 tokens*

The orchestrator executed step 6. Used tools: python_interpreter.

---

### 7. Orchestrator (python_interpreter)

*19:54:51 — 8s — 7,559 tokens*

The orchestrator executed step 7. Used tools: python_interpreter.

---

### 8. Final Output (Orchestrator)

*19:54:53 — 2s — 7,876 tokens*

The orchestrator executed step 8. Used tools: python_interpreter. Produced the final output.

---
