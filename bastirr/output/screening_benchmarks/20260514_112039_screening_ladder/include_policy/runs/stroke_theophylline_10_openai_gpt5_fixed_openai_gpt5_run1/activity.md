# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-05-14 11:20  
> **Duration:** 2m 39s  
> **Total tokens:** 30,966 (input: 13,437 / output: 17,529)

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
| Orchestrator | 2 | 2m 39s | 7,337 / 7,832 |
| Gatekeeper | 1 | 1m 24s | 6,100 / 9,697 |
| **Total** | **3** | **2m 39s** | **13,437 / 17,529** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*11:21:17 — 36s — 7,251 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*11:23:19 — 2m 02s — 23,715 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
