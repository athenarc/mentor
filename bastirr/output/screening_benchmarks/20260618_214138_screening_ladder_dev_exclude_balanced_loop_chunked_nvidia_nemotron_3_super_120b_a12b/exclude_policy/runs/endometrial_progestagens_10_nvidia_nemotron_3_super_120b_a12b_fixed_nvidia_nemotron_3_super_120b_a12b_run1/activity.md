# Pipeline Activity Log

> **Review:** Adjuvant progestagens for endometrial cancer  
> **Date:** 2026-06-18 21:41  
> **Duration:** 32s  
> **Total tokens:** 14,705 (input: 8,316 / output: 6,389)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** endometrial_progestagens_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001040.pub2/full  
> **Dataset split:** dev  
> **Studies:** 10  
> **Chunk count:** 1  
> **Chunk sizes:** 10  
> **Gatekeeper preset:** nvidia_nemotron_3_super_120b_a12b  
> **Gatekeeper model:** nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B]  
> **Orchestrator preset:** nvidia_nemotron_3_super_120b_a12b  
> **Orchestrator model:** nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Gatekeeper | 1 | 24s | 4,868 / 4,845 |
| Orchestrator | 1 | 31s | 3,448 / 1,544 |
| **Total** | **2** | **32s** | **8,316 / 6,389** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*21:42:17 — 31s — 14,705 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
