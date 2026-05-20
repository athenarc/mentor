# Pipeline Activity Log

> **Review:** Surgical methods for first trimester termination of pregnancy  
> **Date:** 2026-05-18 21:37  
> **Duration:** 1m 10s  
> **Total tokens:** 31,199 (input: 26,775 / output: 4,424)

> **Benchmark suite:** screening_ladder_dev_no_label_0_5  
> **Review key:** surgical_termination_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD002900/full  
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
| Orchestrator | 3 | 1m 10s | 11,945 / 1,390 |
| Gatekeeper | 2 | 46s | 14,830 / 3,034 |
| **Total** | **5** | **1m 10s** | **26,775 / 4,424** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*21:37:50 — 8s — 3,882 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*21:38:47 — 56s — 21,811 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Final Output (Orchestrator)

*21:38:53 — 6s — 5,506 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
