# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-09 00:04  
> **Duration:** 2m 58s  
> **Total tokens:** 35,342 (input: 22,477 / output: 12,865)

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
> **Gold label policy:** exclude_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 2m 58s | 7,206 / 4,832 |
| Gatekeeper | 2 | 1m 46s | 15,271 / 8,033 |
| **Total** | **4** | **2m 58s** | **22,477 / 12,865** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:05:43 — 46s — 6,190 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:07:55 — 2m 12s — 29,152 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
