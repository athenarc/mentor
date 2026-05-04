# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-08 21:01  
> **Duration:** 3m 19s  
> **Total tokens:** 43,496 (input: 28,977 / output: 14,519)

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
| Orchestrator | 2 | 3m 18s | 7,436 / 9,094 |
| Gatekeeper | 1 | 1m 10s | 21,541 / 5,425 |
| **Total** | **3** | **3m 19s** | **28,977 / 14,519** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*21:02:42 — 1m 35s — 9,391 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*21:04:25 — 1m 43s — 34,105 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
