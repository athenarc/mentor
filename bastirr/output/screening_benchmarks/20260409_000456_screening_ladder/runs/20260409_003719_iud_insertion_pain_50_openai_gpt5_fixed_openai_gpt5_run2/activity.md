# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-09 00:37  
> **Duration:** 3m 36s  
> **Total tokens:** 41,946 (input: 29,066 / output: 12,880)

> **Benchmark suite:** screening_ladder  
> **Review key:** iud_insertion_pain_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full  
> **Dataset split:** random_test  
> **Studies:** 50  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI API]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI API]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** exclude_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 3m 36s | 7,409 / 6,049 |
| Gatekeeper | 1 | 1m 55s | 21,657 / 6,831 |
| **Total** | **3** | **3m 36s** | **29,066 / 12,880** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:38:16 — 57s — 6,068 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:40:56 — 2m 39s — 35,878 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
