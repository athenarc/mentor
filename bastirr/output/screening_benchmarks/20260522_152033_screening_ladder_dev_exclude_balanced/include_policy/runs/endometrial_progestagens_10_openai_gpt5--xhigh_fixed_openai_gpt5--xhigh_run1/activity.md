# Pipeline Activity Log

> **Review:** Adjuvant progestagens for endometrial cancer  
> **Date:** 2026-05-22 15:20  
> **Duration:** 2m 22s  
> **Total tokens:** 29,776 (input: 11,924 / output: 17,852)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Review key:** endometrial_progestagens_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001040.pub2/full  
> **Dataset split:** dev  
> **Studies:** 10  
> **Gatekeeper preset:** openai_gpt5--xhigh  
> **Gatekeeper model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator preset:** openai_gpt5--xhigh  
> **Orchestrator model:** openai-gpt-5--xhigh [OpenAI GPT5]  
> **Orchestrator policy:** fixed   
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 2 | 2m 22s | 6,900 / 9,229 |
| Gatekeeper | 1 | 1m 00s | 5,024 / 8,623 |
| **Total** | **3** | **2m 22s** | **11,924 / 17,852** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*15:21:30 — 46s — 8,670 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*15:23:06 — 1m 36s — 21,106 tokens*

The orchestrator executed step 2. Used tools: python_interpreter. Produced the final output.

---
