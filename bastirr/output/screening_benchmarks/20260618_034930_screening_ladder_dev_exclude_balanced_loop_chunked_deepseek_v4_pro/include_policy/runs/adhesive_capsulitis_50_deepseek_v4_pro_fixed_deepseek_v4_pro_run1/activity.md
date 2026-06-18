# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-06-18 03:56  
> **Duration:** 3m 21s  
> **Total tokens:** 65,369 (input: 44,252 / output: 21,117)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** adhesive_capsulitis_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full  
> **Dataset split:** dev  
> **Studies:** 50  
> **Chunk count:** 2  
> **Chunk sizes:** 25, 25  
> **Gatekeeper preset:** deepseek_v4_pro  
> **Gatekeeper model:** deepseek-v4-pro [DeepSeek V4 Pro]  
> **Orchestrator preset:** deepseek_v4_pro  
> **Orchestrator model:** deepseek-v4-pro [DeepSeek V4 Pro]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Gatekeeper | 3 | 2m 42s | 37,130 / 17,227 |
| Orchestrator | 2 | 3m 21s | 7,122 / 3,890 |
| **Total** | **5** | **3m 21s** | **44,252 / 21,117** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*03:58:21 — 1m 25s — 23,193 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---

### 2. Orchestrator → Gatekeeper

*04:00:18 — 1m 56s — 42,176 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
