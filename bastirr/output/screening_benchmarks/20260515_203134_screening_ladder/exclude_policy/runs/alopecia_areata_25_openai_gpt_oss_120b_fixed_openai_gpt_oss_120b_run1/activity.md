# Pipeline Activity Log

> **Review:** Interventions for alopecia areata  
> **Date:** 2026-05-15 20:34  
> **Duration:** 1m 58s  
> **Total tokens:** 54,162 (input: 48,480 / output: 5,682)

> **Benchmark suite:** screening_ladder  
> **Review key:** alopecia_areata_25  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004413.pub2/full  
> **Dataset split:** random_test  
> **Studies:** 25  
> **Gatekeeper preset:** openai_gpt_oss_120b  
> **Gatekeeper model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator preset:** openai_gpt_oss_120b  
> **Orchestrator model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 1m 58s | 6,864 / 1,124 |
| Gatekeeper | 3 | 1m 42s | 41,616 / 4,558 |
| **Total** | **5** | **1m 58s** | **48,480 / 5,682** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*20:34:47 — 4s — 3,703 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*20:36:41 — 1m 54s — 50,459 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
