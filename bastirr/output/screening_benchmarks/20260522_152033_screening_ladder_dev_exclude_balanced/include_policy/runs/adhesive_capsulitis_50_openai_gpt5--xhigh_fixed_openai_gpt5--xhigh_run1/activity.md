# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-05-22 15:28  
> **Duration:** 3m 30s  
> **Total tokens:** 50,510 (input: 25,858 / output: 24,652)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Review key:** adhesive_capsulitis_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full  
> **Dataset split:** dev  
> **Studies:** 50  
> **Gatekeeper preset:** openai_gpt5--xhigh  
> **Gatekeeper model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5--xhigh  
> **Orchestrator model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 3m 30s | 7,611 / 8,973 |
| Gatekeeper | 1 | 2m 00s | 18,247 / 15,679 |
| **Total** | **3** | **3m 30s** | **25,858 / 24,652** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*15:29:17 — 45s — 8,003 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*15:32:02 — 2m 44s — 42,507 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
