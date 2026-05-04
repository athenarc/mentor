# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-08 21:10  
> **Duration:** 2m 46s  
> **Total tokens:** 39,860 (input: 29,010 / output: 10,850)

> **Benchmark suite:** screening_ladder  
> **Review key:** iud_insertion_pain_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full  
> **Dataset split:** random_test  
> **Studies:** 50  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 2m 46s | 7,368 / 5,632 |
| Gatekeeper | 1 | 1m 28s | 21,642 / 5,218 |
| **Total** | **3** | **2m 46s** | **29,010 / 10,850** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*21:11:30 — 39s — 6,418 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*21:13:37 — 2m 07s — 33,442 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
