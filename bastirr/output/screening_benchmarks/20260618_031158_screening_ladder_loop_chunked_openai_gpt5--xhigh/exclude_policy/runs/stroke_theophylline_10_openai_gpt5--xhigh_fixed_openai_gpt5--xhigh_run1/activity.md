# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-06-18 03:11  
> **Duration:** 1m 50s  
> **Total tokens:** 19,153 (input: 9,523 / output: 9,630)

> **Benchmark suite:** screening_ladder  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
> **Studies:** 10  
> **Chunk count:** 1  
> **Chunk sizes:** 10  
> **Gatekeeper preset:** openai_gpt5--xhigh  
> **Gatekeeper model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5--xhigh  
> **Orchestrator model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Gatekeeper | 1 | 57s | 6,191 / 4,559 |
| Orchestrator | 1 | 1m 50s | 3,332 / 5,071 |
| **Total** | **2** | **1m 50s** | **9,523 / 9,630** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*03:13:50 — 1m 50s — 19,153 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
