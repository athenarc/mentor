# Pipeline Activity Log

> **Review:** mHealth education interventions in heart failure  
> **Date:** 2026-04-08 01:33  
> **Duration:** 2m 27s  
> **Total tokens:** 96,908 (input: 86,093 / output: 10,815)

> **Benchmark suite:** screening_ladder  
> **Review key:** heart_failure_mhealth_200  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011845.pub2/full  
> **Dataset split:** heart_test  
> **Studies:** 200  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI API]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI API]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** exclude_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 2m 27s | 6,912 / 3,105 |
| Gatekeeper | 1 | 1m 51s | 79,181 / 7,710 |
| **Total** | **3** | **2m 27s** | **86,093 / 10,815** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*01:33:51 — 19s — 4,915 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*01:36:00 — 2m 08s — 91,993 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
