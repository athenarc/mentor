# Pipeline Activity Log

> **Review:** Chemotherapy for advanced, recurrent or metastatic endometrial carcinoma  
> **Date:** 2026-06-18 12:54  
> **Duration:** 2m 27s  
> **Total tokens:** 29,931 (input: 16,121 / output: 13,810)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** advanced_endometrial_carcinoma_24  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD003915.pub4/full  
> **Dataset split:** dev  
> **Studies:** 24  
> **Chunk count:** 1  
> **Chunk sizes:** 24  
> **Gatekeeper preset:** openai_gpt5--xhigh  
> **Gatekeeper model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5--xhigh  
> **Orchestrator model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Gatekeeper | 1 | 1m 39s | 12,729 / 8,996 |
| Orchestrator | 1 | 2m 27s | 3,392 / 4,814 |
| **Total** | **2** | **2m 27s** | **16,121 / 13,810** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*12:56:47 — 2m 27s — 29,931 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
