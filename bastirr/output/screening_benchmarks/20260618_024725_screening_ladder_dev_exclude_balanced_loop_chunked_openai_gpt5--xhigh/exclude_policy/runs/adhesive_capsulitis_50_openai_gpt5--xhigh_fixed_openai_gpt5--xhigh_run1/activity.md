# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-06-18 02:55  
> **Duration:** 18m 10s  
> **Total tokens:** 205,646 (input: 121,216 / output: 84,430)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** adhesive_capsulitis_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full  
> **Dataset split:** dev  
> **Studies:** 50  
> **Chunk count:** 2  
> **Chunk sizes:** 25, 25  
> **Gatekeeper preset:** openai_gpt5--xhigh  
> **Gatekeeper model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5--xhigh  
> **Orchestrator model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Gatekeeper | 6 | 13m 31s | 98,910 / 64,007 |
| Orchestrator | 5 | 18m 10s | 22,306 / 20,423 |
| **Total** | **11** | **18m 10s** | **121,216 / 84,430** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*02:58:35 — 3m 25s — 29,426 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Final Output (Orchestrator)

*02:58:48 — 13s — 6,864 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---

### 3. Orchestrator (python_interpreter)

*03:00:03 — 1m 14s — 10,817 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 4. Orchestrator → Gatekeeper

*03:07:10 — 7m 06s — 64,994 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 5. Orchestrator → Gatekeeper

*03:13:20 — 6m 10s — 93,545 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
