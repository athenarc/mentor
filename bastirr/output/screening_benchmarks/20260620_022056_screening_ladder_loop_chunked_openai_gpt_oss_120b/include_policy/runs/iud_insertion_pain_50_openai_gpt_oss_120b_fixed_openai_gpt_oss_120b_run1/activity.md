# Pipeline Activity Log

> **Review:** Interventions for pain with intrauterine device insertion  
> **Date:** 2026-06-20 02:24  
> **Duration:** 3m 52s  
> **Total tokens:** 155,415 (input: 140,283 / output: 15,132)

> **Benchmark suite:** screening_ladder  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** iud_insertion_pain_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD007373.pub3/full  
> **Dataset split:** random_test  
> **Studies:** 50  
> **Chunk count:** 2  
> **Chunk sizes:** 25, 25  
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
| Gatekeeper | 7 | 3m 18s | 133,361 / 13,195 |
| Orchestrator | 2 | 3m 52s | 6,922 / 1,937 |
| **Total** | **9** | **3m 52s** | **140,283 / 15,132** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*02:25:30 — 1m 28s — 40,787 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---

### 2. Orchestrator → Gatekeeper

*02:27:54 — 2m 24s — 114,628 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
