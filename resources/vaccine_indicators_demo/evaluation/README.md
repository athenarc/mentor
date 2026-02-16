# Evaluation Results

This directory contains qualitative evaluations of AI-generated systematic review answers compared against human expert ground truth.

## Methodology

**Evaluation Framework:** LLM-as-a-Judge  
**Evaluator Model:** Gemini 3 Pro  
**Evaluation Prompt:** [evaluation_prompt.md](evaluation_prompt.md)

### Evaluation Criteria

1. **Core Conclusion Check** - Does AI reach the same overall conclusion as human expert?
2. **Contradiction Screen** - Any direct factual conflicts or false negatives?
3. **Evidence Overlap** - Do shared data points and numbers align?
4. **Final Verdict** - Categorical assessment:
   - `Consistent (Aligned)` - Perfect agreement
   - `Consistent (More Comprehensive)` - Agrees + adds valid details
   - `Conflicting/Contradictory` - Contains contradictions or critical errors

### Key Principles

- **Human answer is the anchor for truth**
- **Additions are permitted** - AI can include valid evidence the human omitted
- **Contradictions are forbidden** - AI must not oppose human findings

## Results Summary

### Hexavalent Vaccine - Benefits of Intervention

| Indicator | Question | Verdict | Status |
|-----------|----------|---------|--------|
| 2.2 | Efficacy and effectiveness estimates | ❌ Conflicting/Contradictory | [View Report](Hexavalent/2.%20BENEFITS%20OF%20THE%20INTERVENTION/2.2%20Efficacy%20and%20effectiveness%20estimates/gemini_evaluation.md) |
| 2.3 | Duration of protection and waning | ✅ Consistent (More Comprehensive) | [View Report](Hexavalent/2.%20BENEFITS%20OF%20THE%20INTERVENTION/2.3%20Duration%20of%20protection/gemini_evaluation.md) |

## Key Findings

### Critical Failure Mode Identified (Indicator 2.2)

> **[TODO] Investigate**

**Issue:** AI failed to recognize **immunogenicity data** (seroprotection/seroconversion rates) as valid proxies for efficacy/effectiveness.

**Impact:** AI claimed "no efficacy estimates provided" for Diphtheria, Tetanus, and Polio despite sources containing abundant seroprotection data—a false negative that directly contradicts the human expert conclusion.

**Root Cause:** In vaccinology, when clinical efficacy trials are unethical or impractical (as with Tetanus), immunogenicity serves as the standard effectiveness proxy. The AI did not understand this domain-specific evidence hierarchy.

**Recommendation:** Update extraction prompt to explicitly instruct recognition of:
- Seroprotection/seroconversion rates as efficacy proxies
- Vaccine evidence hierarchy: Clinical > Immunological > Preclinical
- Absence of clinical trials ≠ absence of evidence

### Success Pattern (Indicator 2.3)

**Outcome:** AI achieved "Consistent (More Comprehensive)" verdict—the ideal scenario.

**Strengths:**
- Accurately synthesized complex duration data across multiple vaccine components
- Added valuable population-specific details (HIV+ individuals, premature infants)
- All duration estimates matched human answer with proper citations
- No contradictions or factual errors

**Insight:** When evidence types are straightforward (duration = time periods), the AI performs excellently and can even enhance answers with relevant granularity.

## Actionable Improvements

1. **Prompt Engineering:**
   - Add explicit guidance about immunogenicity as efficacy proxy
   - Include vaccinology-specific evidence interpretation rules
   - Provide examples of valid indirect effectiveness measures

2. **Expand Evaluation Coverage:**
   - Test remaining Hexavalent indicators
   - Evaluate RSV vaccine answers
   - Compare performance across different question types

3. **Quantitative Metrics:**
   - Complement qualitative evaluation with ROUGE, BERTScore
   - Track consistency rates across indicators
   - Measure citation accuracy

## Directory Structure

```
evaluation/
├── evaluation_prompt.md                    # Evaluation task template
├── README.md                               # This file
├── Hexavalent/
│   └── 2. BENEFITS OF THE INTERVENTION/
│       ├── 2.2 Efficacy and effectiveness estimates/
│       │   └── gemini_evaluation.md
│       └── 2.3 Duration of protection/
│           └── gemini_evaluation.md
└── RSV/
    └── [To be added]
```

## Usage

To perform a new evaluation:

1. Ensure you have:
   - AI-generated synthesis result
   - Human expert ground truth answer
   - Shared source list

2. Adapt the [evaluation_prompt.md](evaluation_prompt.md) template with your data

3. Submit to your evaluation LLM (Gemini, GPT-4, etc.)

4. Save results in the appropriate directory matching the indicator structure

5. Update this README with new findings
