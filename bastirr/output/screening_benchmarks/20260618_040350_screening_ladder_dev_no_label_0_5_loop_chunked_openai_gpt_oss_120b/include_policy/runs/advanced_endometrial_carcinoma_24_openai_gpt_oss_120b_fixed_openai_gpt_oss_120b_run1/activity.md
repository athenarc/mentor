# Pipeline Activity Log

> **Review:** Chemotherapy for advanced, recurrent or metastatic endometrial carcinoma  
> **Date:** 2026-06-18 05:09  
> **Duration:** 40m 04s  
> **Total tokens:** 74,460 (input: 69,537 / output: 4,923)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** advanced_endometrial_carcinoma_24  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD003915.pub4/full  
> **Dataset split:** dev  
> **Studies:** 24  
> **Chunk count:** 1  
> **Chunk sizes:** 24  
> **Gatekeeper preset:** openai_gpt_oss_120b  
> **Gatekeeper model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator preset:** openai_gpt_oss_120b  
> **Orchestrator model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Gatekeeper | 5 | 34m 10s | 66,127 / 4,386 |
| Orchestrator | 1 | 40m 04s | 3,410 / 537 |
| **Total** | **6** | **40m 04s** | **69,537 / 4,923** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*05:49:20 — 40m 04s — 74,460 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
