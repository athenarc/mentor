# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-06-18 01:51  
> **Duration:** 1m 32s  
> **Total tokens:** 15,950 (input: 9,425 / output: 6,525)

> **Benchmark suite:** screening_ladder  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
> **Studies:** 10  
> **Chunk count:** 1  
> **Chunk sizes:** 10  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** openai-gpt-5 [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** openai-gpt-5 [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Gatekeeper | 1 | 48s | 6,097 / 3,630 |
| Orchestrator | 1 | 1m 32s | 3,328 / 2,895 |
| **Total** | **2** | **1m 32s** | **9,425 / 6,525** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*01:52:46 — 1m 32s — 15,950 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
