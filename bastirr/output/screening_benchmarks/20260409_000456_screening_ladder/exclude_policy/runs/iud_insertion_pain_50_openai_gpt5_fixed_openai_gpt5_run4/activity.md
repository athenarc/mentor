# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-04-09 00:46  
> **Duration:** 4m 38s  
> **Total tokens:** 44,632 (input: 29,137 / output: 15,495)

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
> **Gold label policy:** exclude_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 4m 38s | 7,495 / 5,436 |
| Gatekeeper | 1 | 3m 34s | 21,642 / 10,059 |
| **Total** | **3** | **4m 38s** | **29,137 / 15,495** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:46:33 — 24s — 5,900 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:50:47 — 4m 14s — 38,732 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
