# Pipeline Activity Log

> **Review:** Manual therapy and exercise for adhesive capsulitis (frozen shoulder)  
> **Date:** 2026-05-19 00:11  
> **Duration:** 2m 52s  
> **Total tokens:** 55,963 (input: 50,857 / output: 5,106)

> **Benchmark suite:** screening_ladder_dev_exclude_balanced  
> **Review key:** adhesive_capsulitis_50  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011275/full  
> **Dataset split:** dev  
> **Studies:** 50  
> **Gatekeeper preset:** openai_gpt_oss_120b  
> **Gatekeeper model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator preset:** openai_gpt_oss_120b  
> **Orchestrator model:** gpt-oss-120b [OpenAI GPT-OSS 120B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 2m 52s | 14,302 / 1,205 |
| Gatekeeper | 2 | 2m 05s | 36,555 / 3,901 |
| **Total** | **6** | **2m 52s** | **50,857 / 5,106** |

---

## Activity Timeline

### 1. Orchestrator — Step 1

*00:11:21 — 12s — 3,365 tokens*

The orchestrator executed step 1. Encountered an error.

> ⚠️ **Error:** Error in code parsing:
Your code snippet is invalid, because the regex pattern <code>(.*?)</code> was not found in it.
Here is your code snippet:
We will now execute the first code block.</code>
Make sure to include code with the correct pattern, for instance:
Thoughts: Your thoughts
<code>
# Your p

---

### 2. Orchestrator — Step 2

*00:11:23 — 3s — 3,569 tokens*

The orchestrator executed step 2. Encountered an error.

> ⚠️ **Error:** Error in code parsing:
expected string or bytes-like object, got 'NoneType'
Make sure to provide correct code blobs.

---

### 3. Orchestrator (python_interpreter)

*00:11:39 — 16s — 4,140 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator → Gatekeeper

*00:14:02 — 2m 22s — 44,889 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
