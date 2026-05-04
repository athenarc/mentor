# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-08 20:35  
> **Duration:** 1m 59s  
> **Total tokens:** 24,506 (input: 13,251 / output: 11,255)

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
| Orchestrator | 2 | 1m 59s | 7,179 / 5,664 |
| Gatekeeper | 1 | 58s | 6,072 / 5,591 |
| **Total** | **3** | **1m 59s** | **13,251 / 11,255** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*20:36:10 — 38s — 6,458 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*20:37:31 — 1m 21s — 18,048 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
