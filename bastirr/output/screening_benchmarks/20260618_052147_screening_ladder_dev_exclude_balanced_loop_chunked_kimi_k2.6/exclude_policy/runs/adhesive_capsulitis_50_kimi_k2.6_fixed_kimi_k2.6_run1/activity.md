# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-06-18 06:34  
> **Duration:** 37m 18s  
> **Total tokens:** 297,131 (input: 207,946 / output: 89,185)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** adhesive_capsulitis_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full  
> **Dataset split:** dev  
> **Studies:** 50  
> **Chunk count:** 2  
> **Chunk sizes:** 25, 25  
> **Gatekeeper preset:** kimi_k2.6  
> **Gatekeeper model:** kimi-k2.6 [Kimi K2.6]  
> **Orchestrator preset:** kimi_k2.6  
> **Orchestrator model:** kimi-k2.6 [Kimi K2.6]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 9 | 37m 18s | 40,825 / 3,017 |
| Gatekeeper | 13 | 35m 54s | 167,121 / 86,168 |
| **Total** | **22** | **37m 18s** | **207,946 / 89,185** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*06:34:48 — 10s — 3,893 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*06:45:30 — 10m 41s — 82,435 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*06:45:39 — 9s — 5,296 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator (python_interpreter)

*06:45:41 — 2s — 5,439 tokens*

The orchestrator executed step 4. Used tools: python_interpreter.

---

### 5. Final Output (Orchestrator)

*06:45:43 — 2s — 5,599 tokens*

The orchestrator executed step 5. Used tools: python_interpreter. Produced the final output.

---

### 6. Orchestrator (python_interpreter)

*06:45:56 — 13s — 3,890 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 7. Orchestrator → Gatekeeper

*07:11:45 — 25m 48s — 179,764 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 8. Orchestrator (python_interpreter)

*07:11:53 — 8s — 5,343 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 9. Final Output (Orchestrator)

*07:11:56 — 3s — 5,472 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
