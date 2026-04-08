# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-08 00:27  
> **Duration:** 1m 58s  
> **Total tokens:** 20,968 (input: 12,397 / output: 8,571)

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
| Orchestrator | 2 | 1m 58s | 6,550 / 3,070 |
| Gatekeeper | 1 | 1m 14s | 5,847 / 5,501 |
| **Total** | **3** | **1m 58s** | **12,397 / 8,571** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:28:04 — 28s — 4,918 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:29:33 — 1m 29s — 16,050 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
