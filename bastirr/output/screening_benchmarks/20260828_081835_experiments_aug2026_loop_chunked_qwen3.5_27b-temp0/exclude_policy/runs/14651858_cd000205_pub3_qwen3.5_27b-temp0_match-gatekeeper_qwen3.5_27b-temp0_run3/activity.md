# Pipeline Activity Log

> **Review:** Benzodiazepines for antipsychotic‐induced tardive dyskinesia  
> **Date:** 2026-08-28 08:50  
> **Duration:** 14m 19s  
> **Total tokens:** 560,098 (input: 502,394 / output: 57,704)

> **Benchmark suite:** experiments_aug2026  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** 14651858_cd000205_pub3  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000205.pub3/full  
> **Dataset split:** dev  
> **Studies:** 54  
> **Chunk count:** 3  
> **Chunk sizes:** 20, 20, 14  
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
| Orchestrator | 16 | 14m 19s | 83,270 / 5,237 |
| Gatekeeper | 17 | 12m 52s | 419,124 / 52,467 |
| **Total** | **33** | **14m 19s** | **502,394 / 57,704** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*08:50:14 — 7s — 4,057 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*08:55:23 — 5m 09s — 147,561 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*08:55:27 — 4s — 4,995 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*08:55:30 — 3s — 5,398 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 5. Orchestrator (python_interpreter)

*08:55:35 — 5s — 4,081 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 6. Orchestrator → Gatekeeper

*08:59:33 — 3m 57s — 172,365 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 7. Orchestrator (python_interpreter)

*08:59:37 — 5s — 5,087 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 8. Final Output (Orchestrator)

*08:59:42 — 4s — 5,605 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 9. Orchestrator (python_interpreter)

*08:59:50 — 8s — 4,012 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 10. Orchestrator → Gatekeeper

*09:01:19 — 1m 28s — 87,193 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 11. Orchestrator (python_interpreter)

*09:01:26 — 7s — 4,901 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'append_result = append_screening_chunk_decisions_json(
    screening_response=gatekeeper_response,
    output_dir="/mnt/data/dev/SR-agents/bastirr/output/screening_benchmarks/20260828_081835_experiments_aug2026_loop_chunked_qwen3.5_27b-temp0/_raw_runs/20260828_085007_1

---

### 12. Orchestrator → Gatekeeper

*09:04:05 — 2m 39s — 83,464 tokens*

The orchestrator executed step 4. Used tools: python_interpreter.

---

### 13. Orchestrator (python_interpreter)

*09:04:10 — 4s — 6,143 tokens*

The orchestrator executed step 5. Used tools: python_interpreter. Encountered an error.

> ⚠️ **Error:** Code execution failed at line 'append_result = append_screening_chunk_decisions_json(
    screening_response=gatekeeper_response,
    output_dir="/mnt/data/dev/SR-agents/bastirr/output/screening_benchmarks/20260828_081835_experiments_aug2026_loop_chunked_qwen3.5_27b-temp0/_raw_runs/20260828_085007_1

---

### 14. Orchestrator (python_interpreter)

*09:04:12 — 2s — 6,725 tokens*

The orchestrator executed step 6. Used tools: python_interpreter.

---

### 15. Orchestrator (python_interpreter)

*09:04:23 — 11s — 8,824 tokens*

The orchestrator executed step 7. Used tools: python_interpreter.

---

### 16. Final Output (Orchestrator)

*09:04:27 — 4s — 9,687 tokens*

The orchestrator executed step 8. Used tools: python_interpreter. Produced the final output.

---
