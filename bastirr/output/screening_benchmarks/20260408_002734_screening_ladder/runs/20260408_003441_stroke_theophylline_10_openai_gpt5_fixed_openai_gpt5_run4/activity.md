# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-08 00:34  
> **Duration:** 2m 22s  
> **Total tokens:** 32,077 (input: 21,630 / output: 10,447)

> **Benchmark suite:** screening_ladder  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
> **Studies:** 10  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI API]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI API]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** exclude_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 2m 22s | 6,544 / 3,177 |
| Gatekeeper | 2 | 1m 33s | 15,086 / 7,270 |
| **Total** | **4** | **2m 22s** | **21,630 / 10,447** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:35:05 — 24s — 4,701 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:37:03 — 1m 57s — 27,376 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
