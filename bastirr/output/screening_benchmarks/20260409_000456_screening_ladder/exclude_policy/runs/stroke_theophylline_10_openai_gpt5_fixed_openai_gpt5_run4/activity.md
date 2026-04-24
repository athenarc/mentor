# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-09 00:12  
> **Duration:** 2m 57s  
> **Total tokens:** 23,024 (input: 13,167 / output: 9,857)

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
| Orchestrator | 2 | 2m 57s | 7,130 / 5,780 |
| Gatekeeper | 1 | 1m 39s | 6,037 / 4,077 |
| **Total** | **3** | **2m 57s** | **13,167 / 9,857** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:13:20 — 52s — 7,172 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:15:25 — 2m 05s — 15,852 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
