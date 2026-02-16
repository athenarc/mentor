# Medical Literature LLM Experiments

An automated systematic review pipeline that transforms PDF research papers into synthesized evidence using a multi-stage LLM workflow.

## Overview

This system automates the systematic review process for medical research questions, specifically designed for vaccine evidence synthesis. It processes PDF research papers through multiple LLM-powered stages to extract, analyze, and synthesize relevant evidence.

## System Architecture

The workflow consists of four sequential LLM-powered stages plus an optional quality evaluation step:

```
Input: Research Question + PDF Sources
    ↓
Stage 1: OCR Extraction (Mistral AI)
    ↓
Stage 2: Markdown Cleaning (DeepSeek)
    ↓
Stage 3: Evidence Extraction (OpenAI GPT)
    ↓
Stage 4: Evidence Synthesis (OpenAI GPT)
    ↓
Output: Structured Answer with Citations
    ↓
[Optional] Stage 5: Quality Evaluation (Gemini/GPT)
    ↓
Evaluation Report: Consistency, Contradictions, Verdict
```

### Stage 1: OCR to Markdown
- **Model**: MistralOCR 3 API 
- **Purpose**: Convert PDF documents to structured markdown
- **Output**: Raw markdown files with extracted text and structure
- **Script**: `scripts/ocr_pdf_to_markdown.py`

### Stage 2: Markdown Cleaning
- **Model**: DeepSeek R1
- **Purpose**: Clean OCR artifacts, remove irrelevant text, fix formatting
- **Removes**: Headers, footers, page numbers, watermarks, non-English text
- **Output**: Clean, properly formatted markdown files
- **Script**: `scripts/ocr_pdf_to_markdown.py`

### Stage 3: Evidence Extraction
- **Model**: OpenAI GPT (configurable: gpt-4o, gpt-5.2)
- **Purpose**: Extract specific evidence relevant to research questions
- **Input**: Research question (indicator) + cleaned markdown
- **Output**: Structured JSON with:
  - Relevant evidence snippets
  - Key data points (e.g., efficacy rates, duration)
  - Study population details
  - Relevance assessment
- **Prompt**: `prompts/extraction_prompt.md`
- **Script**: `scripts/evidence_synthesis.py`

### Stage 4: Evidence Synthesis
- **Model**: OpenAI GPT (configurable: gpt-4o, gpt-5.2)
- **Purpose**: Synthesize extracted evidence into coherent, citation-backed answers
- **Output**: Academic-style text with inline citations (e.g., `[1], [2]`)
- **Prompt**: `prompts/synthesis_prompt.md`
- **Script**: `scripts/evidence_synthesis.py`

### Stage 5: Quality Evaluation (Optional)
- **Model**: Gemini 3.0 Pro
- **Purpose**: Compare AI-generated synthesis against human ground truth
- **Input**: AI answer + Human expert answer + Source list
- **Output**: Structured evaluation report with:
  - Core conclusion alignment check
  - Contradiction detection
  - Evidence overlap analysis
  - Final verdict (Consistent/More Comprehensive/Contradictory)
- **Prompt**: `evaluation/evaluation_prompt.md`
- **Use Case**: Quality assurance, prompt refinement, model comparison

## Project Structure

```
med_llm_experiments/
├── indicators/              # Organized by vaccine and research questions
│   ├── Hexavalent/
│   │   ├── PDFs/           # Source PDF files
│   │   ├── MD/             # Raw OCR output
│   │   ├── MD_cleaned/     # Cleaned markdown
│   │   └── 2. BENEFITS OF THE INTERVENTION/
│   │       └── [Indicator Questions]/
│   │           ├── sources.csv           # Paper IDs and metadata
│   │           ├── extracted_evidence/   # JSON extraction results
│   │           └── synthesis_result.txt  # Final synthesized answer
│   └── RSV/
│       └── [Similar structure]
├── evaluation/              # Quality evaluation results
│   ├── evaluation_prompt.md             # Evaluation task template
│   ├── Hexavalent/
│   │   └── 2. BENEFITS OF THE INTERVENTION/
│   │       ├── 2.2 Efficacy and effectiveness estimates/
│   │       │   └── gemini_evaluation.md
│   │       └── 2.3 Duration of protection/
│   │           └── gemini_evaluation.md
│   └── RSV/
│       └── [Similar structure]
├── notebooks/
│   ├── hexavalent_runner.ipynb    # Main workflow runner
│   ├── rsv_runner.ipynb           # RSV-specific runner
│   └── source_file_validation.ipynb
├── scripts/
│   ├── ocr_pdf_to_markdown.py     # Stages 1 & 2
│   └── evidence_synthesis.py      # Stages 3 & 4
└── prompts/
    ├── extraction_prompt.md       # Evidence extraction instructions
    └── synthesis_prompt.md        # Evidence synthesis instructions
```

## Key Features

### 1. Batch Processing
- Process multiple PDFs in parallel
- Automatic retry logic with exponential backoff
- Progress tracking and logging

### 2. Structured Evidence Organization
- Hierarchical organization: Vaccine → Category → Research Question
- Each indicator has its own `sources.csv` listing relevant papers
- Extracted evidence stored as JSON for reproducibility

### 3. Citation Management
- Automatic paper ID to citation index mapping
- Inline citations in final synthesis (e.g., `[1], [2]`)
- CSV-based source tracking with metadata

### 4. Quality Control
- Two-stage markdown processing (OCR + cleaning)
- Relevance filtering during extraction
- JSON validation and error handling
- **Qualitative evaluation framework** for comparing AI outputs against human ground truth

### 5. Evaluation Framework
- **Systematic quality assessment** using LLM-as-a-judge methodology
- **Evaluation criteria**:
  - Directional consistency (does AI reach same conclusion as human expert?)
  - Factual accuracy (do specific numbers/data points match?)
  - Non-contradiction (does AI avoid claims that oppose human findings?)
- **Verdict categories**:
  - "Consistent (Aligned)" - Perfect agreement
  - "Consistent (More Comprehensive)" - Agrees + adds valid details
  - "Conflicting/Contradictory" - Contains contradictions or false negatives
- **Use cases**: Prompt refinement, model comparison, identifying systematic errors

### 6. Configurable Models
- Support for multiple LLM providers (Mistral, DeepSeek, OpenAI)
- Easy model switching (e.g., gpt-4o → gpt-5.2)
- API key management via `.env` file

## Usage

### Prerequisites

1. Install dependencies:
```bash
pip install mistralai openai pandas python-dotenv
```

2. Create `.env` file with API keys:
```env
MISTRAL_API_KEY=your_mistral_key
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_API_HOST=https://api.deepseek.com
OPENAI_API_KEY=your_openai_key
```

### Running the Pipeline

See `notebooks/hexavalent_runner.ipynb` for a complete example:

```python
import os
from scripts.ocr_pdf_to_markdown import batch_process_pdfs, batch_clean_markdown_files
from scripts.evidence_synthesis import run_evidence_synthesis

# 1. OCR: Convert PDFs to Markdown
results = batch_process_pdfs(
    "indicators/Hexavalent/PDFs",
    api_key=os.getenv("MISTRAL_API_KEY"),
    output_dir="indicators/Hexavalent/MD"
)

# 2. Clean: Remove OCR artifacts
cleaned_results = batch_clean_markdown_files(
    markdown_directory="indicators/Hexavalent/MD",
    output_directory="indicators/Hexavalent/MD_cleaned",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

# 3 & 4. Extract and Synthesize Evidence
run_evidence_synthesis(
    base_path="indicators",
    extraction_prompt_path="prompts/extraction_prompt.md",
    synthesis_prompt_path="prompts/synthesis_prompt.md",
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o",
    vaccine_topic="Hexavalent",
    replace_paper_ids=True
)
```

## Quality Evaluation

The system includes a qualitative evaluation framework to assess AI-generated synthesis quality against human expert ground truth.

### Evaluation Methodology

**LLM-as-a-Judge Approach:**
- Structured prompt guides evaluation LLM (Gemini 2.0 Flash Experimental or GPT)
- Human expert answer serves as anchor for truth
- AI is permitted to add valid information, but contradictions are flagged

**Evaluation Dimensions:**
1. **Core Conclusion Check** - Does AI reach same overall conclusion?
2. **Contradiction Screen** - Any direct factual conflicts?
3. **Evidence Overlap** - Do shared data points align?
4. **Final Verdict** - Categorical assessment

### Preliminary Results (Hexavalent Vaccine)

| Indicator | Question | Verdict | Key Finding |
|-----------|----------|---------|-------------|
| 2.2 | Efficacy/effectiveness estimates | **Conflicting** | AI failed to recognize immunogenicity data (seroprotection rates) as valid efficacy proxy for Diphtheria/Tetanus/Polio |
| 2.3 | Duration of protection | **Consistent (More Comprehensive)** | AI correctly synthesized all duration estimates and added valuable risk group details |

**Key Insights:**
- The system can produce high-quality, comprehensive answers when evidence types are well-understood (2.3)
- Critical failure mode identified: AI misinterprets absence of clinical trial data as "no evidence" (2.3)
- **Actionable improvement**: Update extraction prompt to explicitly recognize immunogenicity as valid effectiveness proxy

### Evaluation Files
- Template: [`evaluation/evaluation_prompt.md`](evaluation/evaluation_prompt.md)
- Results: [`evaluation/Hexavalent/2. BENEFITS OF THE INTERVENTION/`](evaluation/Hexavalent/2.%20BENEFITS%20OF%20THE%20INTERVENTION/)
  - [2.2 Efficacy estimates evaluation](evaluation/Hexavalent/2.%20BENEFITS%20OF%20THE%20INTERVENTION/2.2%20Efficacy%20and%20effectiveness%20estimates/gemini_evaluation.md)
  - [2.3 Duration evaluation](evaluation/Hexavalent/2.%20BENEFITS%20OF%20THE%20INTERVENTION/2.3%20Duration%20of%20protection/gemini_evaluation.md)

## Output Example

**Input**: Research question about vaccine efficacy

**Output**: `synthesis_result.txt`
```
Clinical studies consistently show high efficacy rates across all 
targeted pathogens [1, 2]:

- Diphtheria: 98% seroprotection rates observed in infants after 
  primary series [3]
- Tetanus: 100% seroprotection maintained through 6 months [3, 4]
- Pertussis: Significant reduction in whooping cough incidence 
  (efficacy: 85-95%) [2, 5]

Sources:
[1] Smith et al. (2023) - paper_id_abc123
[2] Johnson et al. (2022) - paper_id_def456
...
```

## Limitations

1. **Linear Pipeline**: Cannot adapt workflow based on intermediate results
2. **Fixed Prompts**: Prompts are static templates, not dynamically generated
3. **No Iterative Refinement**: System doesn't retry or improve on poor results
4. **Manual Organization**: Requires pre-organized folder structure and `sources.csv` files
5. **Domain-Specific Knowledge Gaps**: As shown in evaluation, AI may misinterpret domain-specific evidence types (e.g., immunogenicity as efficacy proxy)

## Future Enhancements

- [ ] **Update extraction prompts** based on evaluation findings (e.g., recognize immunogenicity data)
- [ ] Add automatic quality assessment between stages using LLM-as-judge
- [ ] Implement retry logic for low-confidence extractions
- [ ] Add dynamic prompt generation based on question type and intermediate results
- [ ] Incorporate feedback loops for iterative improvement
- [ ] Expand evaluation to more indicators and vaccines
- [ ] Quantitative evaluation metrics (ROUGE, BERTScore) to complement qualitative assessment
- [ ] Web interface for non-technical users
- [ ] Automatic paper retrieval via PubMed/Semantic Scholar APIs
