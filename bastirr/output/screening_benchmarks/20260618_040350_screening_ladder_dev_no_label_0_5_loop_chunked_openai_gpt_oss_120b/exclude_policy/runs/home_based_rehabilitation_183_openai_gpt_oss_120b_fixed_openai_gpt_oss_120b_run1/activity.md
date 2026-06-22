# Pipeline Activity Log

> **Review:** Factors that influence the provision of home‐based rehabilitation services for people needing rehabilitation: a qualitative evidence synthesis  
> **Date:** 2026-06-20 01:55  
> **Duration:** 21m 46s  
> **Total tokens:** 603,038 (input: 525,457 / output: 77,581)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** home_based_rehabilitation_183  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD014823/full  
> **Dataset split:** dev  
> **Studies:** 183  
> **Chunk count:** 6  
> **Chunk sizes:** 31, 31, 31, 30, 30, 30  
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
| Gatekeeper | 28 | 19m 58s | 492,996 / 71,401 |
| Orchestrator | 9 | 21m 46s | 32,461 / 6,180 |
| **Total** | **37** | **21m 46s** | **525,457 / 77,581** |

---

## Activity Timeline

### 1. Orchestrator → Gatekeeper

*01:59:21 — 3m 30s — 89,261 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---

### 2. Orchestrator → Gatekeeper

*02:00:47 — 1m 26s — 67,800 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---

### 3. Orchestrator — Step 1

*02:00:55 — 8s — 3,924 tokens*

The orchestrator executed step 1. Encountered an error.

> ⚠️ **Error:** Error in code parsing:
expected string or bytes-like object, got 'NoneType'
Make sure to provide correct code blobs.

---

### 4. Orchestrator (python_interpreter)

*02:01:07 — 12s — 4,225 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 5. Orchestrator → Gatekeeper

*02:07:18 — 6m 11s — 185,920 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---

### 6. Orchestrator (python_interpreter)

*02:07:31 — 12s — 4,229 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 7. Orchestrator → Gatekeeper

*02:09:52 — 2m 21s — 43,178 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---

### 8. Orchestrator → Gatekeeper

*02:11:33 — 1m 40s — 40,451 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---

### 9. Orchestrator → Gatekeeper

*02:17:37 — 6m 04s — 164,050 tokens*

The orchestrator executed step 1. Used tools: python_interpreter. Produced the final output.

---
