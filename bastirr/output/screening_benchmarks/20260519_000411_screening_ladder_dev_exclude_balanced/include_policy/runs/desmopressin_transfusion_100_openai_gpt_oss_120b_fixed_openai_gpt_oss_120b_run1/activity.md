# Pipeline Activity Log

> **Review:** Desmopressin use for minimising perioperative blood transfusion  
> **Date:** 2026-05-19 00:14  
> **Duration:** 11m 05s  
> **Total tokens:** 296,269 (input: 275,538 / output: 20,731)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Review key:** desmopressin_transfusion_100  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001884.pub3/full  
> **Dataset split:** dev  
> **Studies:** 100  
> **Gatekeeper preset:** openai_gpt_oss_120b  
> **Gatekeeper model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator preset:** openai_gpt_oss_120b  
> **Orchestrator model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 11m 05s | 6,873 / 927 |
| Gatekeeper | 6 | 10m 50s | 268,665 / 19,804 |
| **Total** | **8** | **11m 05s** | **275,538 / 20,731** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:14:19 — 7s — 3,686 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:25:17 — 10m 58s — 292,583 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
