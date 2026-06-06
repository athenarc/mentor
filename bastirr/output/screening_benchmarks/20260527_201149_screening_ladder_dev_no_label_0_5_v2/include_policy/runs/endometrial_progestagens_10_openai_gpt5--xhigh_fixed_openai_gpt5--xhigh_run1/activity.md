# Pipeline Activity Log

> **Review:** Adjuvant progestagens for endometrial cancer  
> **Date:** 2026-05-27 20:11  
> **Duration:** 7m 40s  
> **Total tokens:** 26,142 (input: 12,011 / output: 14,131)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5_v2  
> **Review key:** endometrial_progestagens_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001040.pub2/full  
> **Dataset split:** dev  
> **Studies:** 10  
> **Gatekeeper preset:** openai_gpt5--xhigh  
> **Gatekeeper model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5--xhigh  
> **Orchestrator model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 7m 40s | 6,925 / 7,403 |
| Gatekeeper | 1 | 3m 41s | 5,086 / 6,728 |
| **Total** | **3** | **7m 40s** | **12,011 / 14,131** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*20:14:23 — 2m 24s — 7,029 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*20:19:39 — 5m 15s — 19,113 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
