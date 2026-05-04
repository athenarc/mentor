# Pipeline Activity Log

> **Review:** mHealth education interventions in heart failure  
> **Date:** 2026-04-09 01:22  
> **Duration:** 9m 06s  
> **Total tokens:** 103,856 (input: 87,131 / output: 16,725)

> **Benchmark suite:** screening_ladder  
> **Review key:** heart_failure_mhealth_200  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011845.pub2/full  
> **Dataset split:** heart_test  
> **Studies:** 200  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** exclude_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 9m 06s | 7,743 / 7,104 |
| Gatekeeper | 1 | 7m 36s | 79,388 / 9,621 |
| **Total** | **3** | **9m 06s** | **87,131 / 16,725** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:23:25 — 46s — 7,424 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:31:46 — 8m 21s — 96,432 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
