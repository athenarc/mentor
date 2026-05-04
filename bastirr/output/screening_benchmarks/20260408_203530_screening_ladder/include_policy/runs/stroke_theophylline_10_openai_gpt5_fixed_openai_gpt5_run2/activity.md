# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-08 20:37  
> **Duration:** 1m 47s  
> **Total tokens:** 23,351 (input: 13,448 / output: 9,903)

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
| Orchestrator | 2 | 1m 47s | 7,409 / 4,969 |
| Gatekeeper | 1 | 55s | 6,039 / 4,934 |
| **Total** | **3** | **1m 47s** | **13,448 / 9,903** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*20:38:08 — 36s — 6,677 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*20:39:19 — 1m 11s — 16,674 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
