# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-08 21:16  
> **Duration:** 8m 27s  
> **Total tokens:** 80,023 (input: 64,226 / output: 15,797)

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
| Orchestrator | 2 | 8m 27s | 7,344 / 5,359 |
| Gatekeeper | 2 | 6m 45s | 56,882 / 10,438 |
| **Total** | **4** | **8m 27s** | **64,226 / 15,797** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*21:17:59 — 1m 10s — 6,745 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*21:25:16 — 7m 17s — 73,278 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
