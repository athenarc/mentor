# Pipeline Activity Log

> **Review:** Benzodiazepines for antipsychotic‐induced tardive dyskinesia  
> **Date:** 2026-08-28 08:37  
> **Duration:** 12m 23s  
> **Total tokens:** 287,551 (input: 254,690 / output: 32,861)

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
| Orchestrator | 12 | 12m 23s | 53,239 / 3,154 |
| Gatekeeper | 10 | 11m 15s | 201,451 / 29,707 |
| **Total** | **22** | **12m 23s** | **254,690 / 32,861** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*08:37:33 — 4s — 4,054 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*08:42:09 — 4m 35s — 64,536 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*08:42:18 — 9s — 5,144 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*08:42:20 — 2s — 5,459 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 5. Orchestrator (python_interpreter)

*08:42:24 — 4s — 4,081 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 6. Orchestrator → Gatekeeper

*08:45:20 — 2m 55s — 38,859 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 7. Orchestrator (python_interpreter)

*08:45:26 — 6s — 4,955 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 8. Final Output (Orchestrator)

*08:45:31 — 5s — 5,259 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 9. Orchestrator (python_interpreter)

*08:45:35 — 4s — 4,009 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 10. Orchestrator → Gatekeeper

*08:49:38 — 4m 03s — 141,103 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 11. Orchestrator (python_interpreter)

*08:49:47 — 9s — 4,890 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 12. Final Output (Orchestrator)

*08:49:52 — 5s — 5,202 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
