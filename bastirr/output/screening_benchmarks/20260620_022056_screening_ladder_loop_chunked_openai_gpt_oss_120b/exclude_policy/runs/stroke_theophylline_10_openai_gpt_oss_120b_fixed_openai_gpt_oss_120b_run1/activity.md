# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-06-20 02:20  
> **Duration:** 1m 27s  
> **Total tokens:** 35,007 (input: 29,129 / output: 5,878)

> **Benchmark suite:** screening_ladder  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
> **Studies:** 10  
> **Chunk count:** 1  
> **Chunk sizes:** 10  
> **Gatekeeper preset:** openai_gpt_oss_120b  
> **Gatekeeper model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator preset:** openai_gpt_oss_120b  
> **Orchestrator model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator policy:** fixed  
> **Orchestrator max steps:** 30  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Gatekeeper | 3 | 1m 09s | 25,745 / 4,828 |
| Orchestrator | 1 | 1m 27s | 3,384 / 1,050 |
| **Total** | **4** | **1m 27s** | **29,129 / 5,878** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*02:22:24 — 1m 27s — 35,007 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
