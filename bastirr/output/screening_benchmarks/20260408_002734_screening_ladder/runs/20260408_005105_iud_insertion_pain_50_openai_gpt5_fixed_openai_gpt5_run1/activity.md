# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-08 00:51  
> **Duration:** 2m 33s  
> **Total tokens:** 41,383 (input: 27,968 / output: 13,415)

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
| Orchestrator | 2 | 2m 33s | 6,686 / 2,681 |
| Gatekeeper | 1 | 2m 03s | 21,282 / 10,734 |
| **Total** | **3** | **2m 33s** | **27,968 / 13,415** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:51:24 — 19s — 4,753 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:53:39 — 2m 14s — 36,630 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
