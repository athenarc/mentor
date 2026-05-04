# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-04-09 00:15  
> **Duration:** 2m 04s  
> **Total tokens:** 22,709 (input: 13,360 / output: 9,349)

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
| Orchestrator | 2 | 2m 04s | 7,240 / 5,132 |
| Gatekeeper | 1 | 47s | 6,120 / 4,217 |
| **Total** | **3** | **2m 04s** | **13,360 / 9,349** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:16:28 — 1m 02s — 6,401 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:17:30 — 1m 01s — 16,308 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
