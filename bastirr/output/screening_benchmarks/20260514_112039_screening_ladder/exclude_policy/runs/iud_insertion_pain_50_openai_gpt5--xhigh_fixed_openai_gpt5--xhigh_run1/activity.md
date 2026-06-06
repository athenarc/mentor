# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-05-14 11:28  
> **Duration:** 3m 02s  
> **Total tokens:** 49,836 (input: 28,683 / output: 21,153)

> **Benchmark suite:** screening_ladder  
> **Review key:** iud_insertion_pain_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full  
> **Dataset split:** random_test  
> **Studies:** 50  
> **Gatekeeper preset:** openai_gpt5--xhigh  
> **Gatekeeper model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5--xhigh  
> **Orchestrator model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 3m 02s | 7,185 / 7,416 |
| Gatekeeper | 1 | 1m 57s | 21,498 / 13,737 |
| **Total** | **3** | **3m 02s** | **28,683 / 21,153** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*11:28:44 — 40s — 8,402 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*11:31:05 — 2m 21s — 41,434 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
