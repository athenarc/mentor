# Pipeline Activity Log

> **Review:** Adjuvant progestagens for endometrial cancer  
> **Date:** 2026-05-19 00:04  
> **Duration:** 3m 39s  
> **Total tokens:** 69,120 (input: 61,446 / output: 7,674)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Review key:** endometrial_progestagens_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001040.pub2/full  
> **Dataset split:** dev  
> **Studies:** 10  
> **Gatekeeper preset:** openai_gpt_oss_120b  
> **Gatekeeper model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator preset:** openai_gpt_oss_120b  
> **Orchestrator model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 3m 39s | 17,187 / 2,491 |
| Gatekeeper | 7 | 2m 36s | 44,259 / 5,183 |
| **Total** | **11** | **3m 39s** | **61,446 / 7,674** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*00:04:35 — 14s — 3,748 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*00:06:48 — 2m 12s — 40,872 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*00:07:00 — 11s — 4,596 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator → Gatekeeper

*00:08:00 — 1m 00s — 19,904 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
