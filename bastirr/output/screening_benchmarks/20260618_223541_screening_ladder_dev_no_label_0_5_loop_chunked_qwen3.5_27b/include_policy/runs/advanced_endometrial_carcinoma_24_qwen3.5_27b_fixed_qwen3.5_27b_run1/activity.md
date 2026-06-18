# Pipeline Activity Log

> **Review:** Chemotherapy for advanced, recurrent or metastatic endometrial carcinoma  
> **Date:** 2026-06-18 22:37  
> **Duration:** 9m 18s  
> **Total tokens:** 152,435 (input: 130,300 / output: 22,135)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** advanced_endometrial_carcinoma_24  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD003915.pub4/full  
> **Dataset split:** dev  
> **Studies:** 24  
> **Chunk count:** 1  
> **Chunk sizes:** 24  
> **Gatekeeper preset:** qwen3.5_27b  
> **Gatekeeper model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator preset:** qwen3.5_27b  
> **Orchestrator model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 9m 18s | 17,280 / 954 |
| Gatekeeper | 3 | 8m 59s | 113,020 / 21,181 |
| **Total** | **7** | **9m 18s** | **130,300 / 22,135** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*22:37:26 — 6s — 4,053 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*22:46:29 — 9m 03s — 138,537 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*22:46:35 — 6s — 4,771 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*22:46:38 — 3s — 5,074 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
