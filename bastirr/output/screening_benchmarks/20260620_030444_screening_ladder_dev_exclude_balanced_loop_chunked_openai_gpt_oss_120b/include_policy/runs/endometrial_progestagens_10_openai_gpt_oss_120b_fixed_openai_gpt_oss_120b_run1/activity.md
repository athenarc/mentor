# Pipeline Activity Log

> **Review:** Adjuvant progestagens for endometrial cancer  
> **Date:** 2026-06-20 03:04  
> **Duration:** 1m 36s  
> **Total tokens:** 21,632 (input: 16,450 / output: 5,182)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** endometrial_progestagens_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001040.pub2/full  
> **Dataset split:** dev  
> **Studies:** 10  
> **Chunk count:** 1  
> **Chunk sizes:** 10  
> **Gatekeeper preset:** openai_gpt_oss_120b  
> **Gatekeeper model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator preset:** openai_gpt_oss_120b  
> **Orchestrator model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator policy:** fixed  
> **Orchestrator max steps:** 30  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Gatekeeper | 2 | 1m 04s | 13,107 / 3,470 |
| Orchestrator | 1 | 1m 35s | 3,343 / 1,712 |
| **Total** | **3** | **1m 36s** | **16,450 / 5,182** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*03:06:30 — 1m 35s — 21,632 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
