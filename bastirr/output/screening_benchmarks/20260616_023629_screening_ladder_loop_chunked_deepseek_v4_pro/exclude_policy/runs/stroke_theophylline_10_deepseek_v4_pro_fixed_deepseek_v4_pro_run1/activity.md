# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-06-16 02:36  
> **Duration:** 2m 13s  
> **Total tokens:** 50,072 (input: 35,607 / output: 14,465)

> **Benchmark suite:** screening_ladder  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
> **Studies:** 10  
> **Chunk count:** 1  
> **Chunk sizes:** 10  
> **Gatekeeper preset:** deepseek_v4_pro  
> **Gatekeeper model:** deepseek-v4-pro [DeepSeek V4 Pro]  
> **Orchestrator preset:** deepseek_v4_pro  
> **Orchestrator model:** deepseek-v4-pro [DeepSeek V4 Pro]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Gatekeeper | 4 | 1m 45s | 32,187 / 11,448 |
| Orchestrator | 1 | 2m 13s | 3,420 / 3,017 |
| **Total** | **5** | **2m 13s** | **35,607 / 14,465** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*02:38:43 — 2m 13s — 50,072 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
