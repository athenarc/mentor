# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-08 20:42  
> **Duration:** 1m 45s  
> **Total tokens:** 23,086 (input: 13,186 / output: 9,900)

> **Benchmark suite:** screening_ladder  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
> **Studies:** 10  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 1m 45s | 7,110 / 4,448 |
| Gatekeeper | 1 | 60s | 6,076 / 5,452 |
| **Total** | **3** | **1m 45s** | **13,186 / 9,900** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*20:42:41 — 27s — 5,947 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*20:43:59 — 1m 18s — 17,139 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
