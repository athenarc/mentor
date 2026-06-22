# Pipeline Activity Log

> **Review:** Interventions for alopecia areata  
> **Date:** 2026-06-20 02:22  
> **Duration:** 1m 36s  
> **Total tokens:** 82,508 (input: 75,771 / output: 6,737)

> **Benchmark suite:** screening_ladder  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** alopecia_areata_25  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004413.pub2/full  
> **Dataset split:** random_test  
> **Studies:** 25  
> **Chunk count:** 1  
> **Chunk sizes:** 25  
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
| Gatekeeper | 4 | 1m 22s | 72,331 / 5,855 |
| Orchestrator | 1 | 1m 36s | 3,440 / 882 |
| **Total** | **5** | **1m 36s** | **75,771 / 6,737** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*02:24:01 — 1m 36s — 82,508 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
