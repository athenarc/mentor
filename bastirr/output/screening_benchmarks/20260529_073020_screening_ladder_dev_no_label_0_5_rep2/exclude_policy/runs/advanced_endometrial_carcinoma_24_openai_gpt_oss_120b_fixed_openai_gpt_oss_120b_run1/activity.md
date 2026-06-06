# Pipeline Activity Log

> **Review:** Chemotherapy for advanced, recurrent or metastatic endometrial carcinoma  
> **Date:** 2026-05-29 07:31  
> **Duration:** 2m 55s  
> **Total tokens:** 364,617 (input: 356,516 / output: 8,101)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Review key:** advanced_endometrial_carcinoma_24  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD003915.pub4/full  
> **Dataset split:** dev  
> **Studies:** 24  
> **Gatekeeper preset:** openai_gpt_oss_120b  
> **Gatekeeper model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator preset:** openai_gpt_oss_120b  
> **Orchestrator model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 2m 55s | 6,915 / 985 |
| Gatekeeper | 18 | 2m 40s | 349,601 / 7,116 |
| **Total** | **20** | **2m 55s** | **356,516 / 8,101** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*07:31:41 — 8s — 3,921 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*07:34:28 — 2m 47s — 360,696 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
