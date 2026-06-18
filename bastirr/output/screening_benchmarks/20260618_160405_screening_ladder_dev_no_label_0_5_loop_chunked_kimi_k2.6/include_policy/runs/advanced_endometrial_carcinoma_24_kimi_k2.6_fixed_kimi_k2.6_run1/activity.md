# Pipeline Activity Log

> **Review:** Chemotherapy for advanced, recurrent or metastatic endometrial carcinoma  
> **Date:** 2026-06-18 16:17  
> **Duration:** 9m 09s  
> **Total tokens:** 81,321 (input: 63,006 / output: 18,315)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** advanced_endometrial_carcinoma_24  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD003915.pub4/full  
> **Dataset split:** dev  
> **Studies:** 24  
> **Chunk count:** 1  
> **Chunk sizes:** 24  
> **Gatekeeper preset:** kimi_k2.6  
> **Gatekeeper model:** kimi-k2.6 [Kimi K2.6]  
> **Orchestrator preset:** kimi_k2.6  
> **Orchestrator model:** kimi-k2.6 [Kimi K2.6]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Gatekeeper | 4 | 5m 37s | 59,601 / 13,591 |
| Orchestrator | 1 | 9m 09s | 3,405 / 4,724 |
| **Total** | **5** | **9m 09s** | **63,006 / 18,315** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*16:26:26 — 9m 09s — 81,321 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
