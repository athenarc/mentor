# Pipeline Activity Log

> **Review:** Interventions for alopecia areata  
> **Date:** 2026-04-08 20:56  
> **Duration:** 4m 09s  
> **Total tokens:** 57,325 (input: 36,720 / output: 20,605)

> **Benchmark suite:** screening_ladder  
> **Review key:** alopecia_areata_25  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004413.pub2/full  
> **Dataset split:** random_test  
> **Studies:** 25  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI API]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI API]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 4m 09s | 7,226 / 5,714 |
| Gatekeeper | 2 | 2m 34s | 29,494 / 14,891 |
| **Total** | **4** | **4m 09s** | **36,720 / 20,605** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*20:57:44 — 48s — 7,054 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*21:01:05 — 3m 20s — 50,271 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
