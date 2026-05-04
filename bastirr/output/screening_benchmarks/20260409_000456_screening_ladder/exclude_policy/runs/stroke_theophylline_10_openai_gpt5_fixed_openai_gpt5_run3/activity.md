# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-09 00:10  
> **Duration:** 2m 14s  
> **Total tokens:** 23,176 (input: 13,203 / output: 9,973)

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
| Orchestrator | 2 | 2m 14s | 7,110 / 4,846 |
| Gatekeeper | 1 | 57s | 6,093 / 5,127 |
| **Total** | **3** | **2m 14s** | **13,203 / 9,973** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:11:00 — 47s — 5,796 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:12:27 — 1m 27s — 17,380 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
