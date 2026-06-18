# Pipeline Activity Log

> **Review:** Interventions for alopecia areata  
> **Date:** 2026-06-18 14:50  
> **Duration:** 9m 20s  
> **Total tokens:** 700,464 (input: 623,370 / output: 77,094)

> **Benchmark suite:** screening_ladder  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** alopecia_areata_25  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD004413.pub2/full  
> **Dataset split:** random_test  
> **Studies:** 25  
> **Chunk count:** 1  
> **Chunk sizes:** 25  
> **Gatekeeper preset:** nvidia_nemotron_3_super_120b_a12b  
> **Gatekeeper model:** nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B]  
> **Orchestrator preset:** nvidia_nemotron_3_super_120b_a12b  
> **Orchestrator model:** nvidia-nemotron-3-super-120b-a12b [NVIDIA Nemotron 3 Super 120B A12B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Gatekeeper | 8 | 8m 39s | 619,786 / 70,525 |
| Orchestrator | 1 | 9m 20s | 3,584 / 6,569 |
| **Total** | **9** | **9m 20s** | **623,370 / 77,094** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*15:00:10 — 9m 20s — 700,464 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
