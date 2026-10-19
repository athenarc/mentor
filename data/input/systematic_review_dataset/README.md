# Systematic Review Datasets for Title and Abstract Screening

**Overview**
This repository references two large datasets compiled to support the training and evaluation of AI systems for systematic review automation, specifically for title and abstract screening. These datasets are currently the largest of their kind, covering health and medical research. They include detailed metadata for reviews and labeling for individual publications to facilitate the development of fully automated screening tools.

## Data Access
*   **Repository:** Mendeley Data
*   **URL:** https://data.mendeley.com/datasets/7sgmg89zb6/1
*   **DOI:** 10.17632/7sgmg89zb6.1
*   **Article Open Data Badge:** This dataset was awarded Open Data and Open Materials badges for transparent practices.

## Getting Started: Download the Dataset

Due to the large size of the dataset files (>1GB), they are not included in this repository. Use the provided download script to fetch the data from Mendeley Data.

### Quick Start

```bash
# Run the download script (auto-extracts and cleans up by default)
./download_dataset.sh
```

The script will:
- Download the dataset ZIP file (~600MB)
- Verify file integrity using SHA256 checksum
- Automatically extract all files (including nested ZIPs)
- Extract to correct directories:
  - `20240827_Systematic_Review_Data/` - Main training/validation/test splits
  - `20240827_Systematic_review_manual_search_data/` - Simulated real-world search data
- Automatically clean up ZIP files after extraction

### Advanced Options

```bash
# Download only (don't extract):
./download_dataset.sh --no-unzip

# Extract but keep ZIP files:
./download_dataset.sh --no-delete

# Download without extraction or cleanup:
./download_dataset.sh --no-unzip --no-delete

# Show help:
./download_dataset.sh --help
```

### Manual Download

If you prefer to download manually:
1. Download from: https://data.mendeley.com/public-api/zip/7sgmg89zb6/download/1
2. Verify SHA256 checksum: `27dc9142917b9b528bfcc4bc57532181fb7d792883e19d02b1a001f0ce6a0eba`
3. Extract the ZIP file contents into this repository's root directory

## Dataset 1: The Cochrane Library Dataset

### Description
This dataset was constructed by searching the Cochrane Library on 15 December 2023 to collect data on all published systematic reviews. It contains 8,608 systematic reviews and 544,157 titles and abstracts. It covers 51 distinct research topic areas ranging from allergy to mental health to medical research methodology.

### Content and Metadata
For each systematic review, the dataset includes the following metadata:
*   **Review Title**
*   **Background Information**
*   **Objectives**
*   **Selection Criteria**

### Labeling Schema
Individual studies associated with each review are labeled into three categories:
1.  **Included:** Publications included in the final evidence synthesis.
2.  **Excluded after Full-Text Screening:** Publications included during title/abstract screening but excluded later.
3.  **Excluded during Title/Abstract Screening:** Publications rejected during the initial screening phase.

*Note regarding labeling:* The list of "additional studies" found in Cochrane reviews was used to approximate the set of publications excluded during title and abstract screening. Consequently, this set is generally smaller than the set of excluded publications in a real-world systematic review search and contains studies somewhat related to the topic.

### Data Splits
To evaluate model performance across different domains, the dataset is organized into five subsets:
*   **Training Set:** 90% of the randomly selected reviews (N = 7,458).
*   **Validation Set:** 5% of the randomly selected reviews (N = 419).
*   **Test Set (Random):** 5% of the randomly selected reviews (N = 426).
*   **Test Set (Heart):** Withheld reviews on the topic of heart health (N = 205) for out-of-domain testing.
*   **Test Set (HIV):** Withheld reviews on the topic of HIV (N = 100) for out-of-domain testing.

### Statistics (Training Set)
*   **Total Reviews:** 7,458
*   **Topic Areas:** 51
*   **Included Publications:** 81,120 (Mean: 12.9 per review)
*   **Excluded (Full-Text):** 161,003 (Mean: 23.7 per review)
*   **Excluded (Title/Abstract):** 224,622 (Mean: 30.2 per review)

## Dataset 2: Simulated Real-World Search Dataset

### Description
To evaluate screening performance under realistic conditions where datasets are highly imbalanced, a second dataset was compiled by simulating the actual search processes of 22 systematic reviews published in the Cochrane Library between 15 December 2023 and 15 May 2024.

### Methodology
The dataset was created by following the exact search strategies of the selected reviews to construct the initial set of retrieved publications. The search was replicated in Medline, Embase, and Cochrane Central.

### Statistics
*   **Number of Reviews:** 22
*   **Total Retrieved Publications:** 142,504
*   **Mean Publications per Review:** 6,477
*   **Max Publications in a Review:** 49,162
*   **Characteristics:** This dataset is much more imbalanced than Dataset 1, with the vast majority of publications being irrelevant.

## Potential Applications
These datasets are designed for:
*   Training AI models for full automation of systematic review screening.
*   Evaluating false-positive and false-negative rates across diverse research topics.
*   Developing models that utilize rich metadata (background, objectives) rather than just review titles.
*   Exploring the nuance between clear exclusions and ambiguous studies (those excluded only after full-text reading).

## Citation
If you use this dataset, please cite the following article:

> Chan, G. C. K., He, E., Leung, J., & Verspoor, K. (2025). A comprehensive systematic review dataset is a rich resource for training and evaluation of AI systems for title and abstract screening. *Research Synthesis Methods*, 16, 308–322. doi:10.1017/rsm.2025.1

**License:** Creative Commons Attribution licence (https://creativecommons.org/licenses/by/4.0).