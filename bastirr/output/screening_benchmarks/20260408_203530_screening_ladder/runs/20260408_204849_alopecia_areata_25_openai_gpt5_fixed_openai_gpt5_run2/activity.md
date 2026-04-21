# Pipeline Activity Log

> **Review:** Interventions for alopecia areata  
> **Date:** 2026-04-08 20:48  
> **Duration:** 2m 47s  
> **Total tokens:** 29,318 (input: 18,088 / output: 11,230)

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
| Orchestrator | 2 | 2m 47s | 7,171 / 4,838 |
| Gatekeeper | 1 | 1m 59s | 10,917 / 6,392 |
| **Total** | **3** | **2m 47s** | **18,088 / 11,230** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*20:49:21 — 32s — 6,523 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*20:51:37 — 2m 15s — 22,795 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
