# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-06-18 04:27  
> **Duration:** 6m 10s  
> **Total tokens:** 129,944 (input: 95,721 / output: 34,223)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** adhesive_capsulitis_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full  
> **Dataset split:** dev  
> **Studies:** 50  
> **Chunk count:** 2  
> **Chunk sizes:** 25, 25  
> **Gatekeeper preset:** deepseek_v4_pro--xhigh  
> **Gatekeeper model:** deepseek-v4-pro--xhigh [DeepSeek V4 Pro]  
> **Orchestrator preset:** deepseek_v4_pro--xhigh  
> **Orchestrator model:** deepseek-v4-pro--xhigh [DeepSeek V4 Pro]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 6 | 6m 10s | 27,742 / 9,370 |
| Gatekeeper | 5 | 4m 28s | 67,979 / 24,853 |
| **Total** | **11** | **6m 10s** | **95,721 / 34,223** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*04:27:28 — 12s — 4,695 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*04:30:37 — 3m 08s — 60,394 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*04:30:40 — 3s — 4,879 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*04:30:42 — 3s — 5,070 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 5. Orchestrator → Gatekeeper

*04:33:14 — 2m 31s — 46,557 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 6. Final Output (Orchestrator)

*04:33:27 — 13s — 8,349 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
