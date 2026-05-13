# Pipeline Activity Log

> **Review:** Adjuvant progestagens for endometrial cancer  
> **Date:** 2026-05-12 18:33  
> **Duration:** 1m 44s  
> **Total tokens:** 20,052 (input: 11,924 / output: 8,128)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Review key:** endometrial_progestagens_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001040.pub2/full  
> **Dataset split:** dev  
> **Studies:** 10  
> **Gatekeeper preset:** openai_gpt5  
> **Gatekeeper model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5  
> **Orchestrator model:** gpt-5 [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 1m 44s | 6,884 / 4,049 |
| Gatekeeper | 1 | 35s | 5,040 / 4,079 |
| **Total** | **3** | **1m 44s** | **11,924 / 8,128** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*18:34:22 — 46s — 5,782 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*18:35:20 — 58s — 14,270 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
