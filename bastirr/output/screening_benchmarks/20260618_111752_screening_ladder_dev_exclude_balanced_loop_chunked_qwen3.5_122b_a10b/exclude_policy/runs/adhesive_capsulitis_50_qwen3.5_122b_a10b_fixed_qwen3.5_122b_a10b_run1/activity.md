# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-06-18 11:38  
> **Duration:** 5m 39s  
> **Total tokens:** 208,135 (input: 180,115 / output: 28,020)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** adhesive_capsulitis_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full  
> **Dataset split:** dev  
> **Studies:** 50  
> **Chunk count:** 2  
> **Chunk sizes:** 25, 25  
> **Gatekeeper preset:** qwen3.5_122b_a10b  
> **Gatekeeper model:** qwen3.5-122b-a10b [Qwen 3.5 122B A10B]  
> **Orchestrator preset:** qwen3.5_122b_a10b  
> **Orchestrator model:** qwen3.5-122b-a10b [Qwen 3.5 122B A10B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 5 | 5m 39s | 22,372 / 2,862 |
| Gatekeeper | 6 | 5m 00s | 157,743 / 25,158 |
| **Total** | **11** | **5m 39s** | **180,115 / 28,020** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*11:38:29 — 12s — 4,656 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*11:42:09 — 3m 39s — 152,881 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*11:42:12 — 3s — 5,184 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*11:42:14 — 2s — 5,430 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 5. Orchestrator → Gatekeeper

*11:43:57 — 1m 42s — 39,984 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
