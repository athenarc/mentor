# Dataset Download Guide

This guide provides detailed instructions for downloading the systematic review datasets.

## Overview

The dataset files are hosted on Mendeley Data and are too large to include in this GitHub repository. The total download size is approximately **600MB** (compressed) and will expand to **~2GB** when extracted.

## Prerequisites

- Bash shell (available on macOS, Linux, WSL, Git Bash on Windows)
- `curl` or `wget` for downloading
- `unzip` for extraction
- Internet connection
- Approximately 3GB of free disk space

## Installation & Download

### Method 1: Automated Script (Recommended)

1. **Clone this repository:**
   ```bash
   git clone https://github.com/pkoloveas/systematic_review_dataset_EDA.git
   cd systematic_review_dataset_EDA
   ```

2. **Run the download script:**
   ```bash
   ./download_dataset.sh
   ```
   
   By default, the script will:
   - Download the main ZIP file with progress tracking
   - Verify file integrity using SHA256 checksum
   - Automatically extract all files (including nested ZIPs)
   - Automatically clean up ZIP files after extraction

3. **Advanced options:**
   ```bash
   # Download without auto-extraction:
   ./download_dataset.sh --no-unzip
   
   # Extract but keep ZIP files:
   ./download_dataset.sh --no-delete
   
   # Both options (download only, keep ZIPs):
   ./download_dataset.sh --no-unzip --no-delete
   
   # Show help and all options:
   ./download_dataset.sh --help
   ```

### Method 2: Manual Download

If you prefer to download manually or encounter issues with the automated script:

1. **Download the dataset:**
   - URL: https://data.mendeley.com/public-api/zip/7sgmg89zb6/download/1
   - Or visit: https://data.mendeley.com/datasets/7sgmg89zb6/1

2. **Verify the download (optional but recommended):**
   ```bash
   # On macOS/Linux:
   shasum -a 256 "Title and Abstract Screening Data for Systematic Review.zip"
   
   # On Windows (PowerShell):
   Get-FileHash -Algorithm SHA256 "Title and Abstract Screening Data for Systematic Review.zip"
   ```
   
   Expected checksum: `27dc9142917b9b528bfcc4bc57532181fb7d792883e19d02b1a001f0ce6a0eba`

3. **Extract the ZIP file:**
   - Extract the contents to the repository root directory
   - **Note:** The main ZIP contains 2 nested ZIPs:
     - `20240827_Systematic_Review_Data.zip`
     - `20240827_Systematic_review_manual_search_data.zip`
   - You'll need to extract these nested ZIPs as well
   - Final directories should be:
     - `20240827_Systematic_Review_Data/`
     - `20240827_Systematic_review_manual_search_data/`

## Dataset Structure

The download has a nested structure:

```
Title and Abstract Screening Data for Systematic Review.zip (main download)
 ├── 20240827_Systematic_Review_Data.zip (nested)
 └── 20240827_Systematic_review_manual_search_data.zip (nested)
```

The automated script handles all extraction automatically. If extracting manually, remember to extract all three ZIP files.

## What Gets Downloaded

After extraction, you'll have:

### Dataset 1: Cochrane Library Dataset
Location: `20240827_Systematic_Review_Data/`

- `20240827_dev_set.csv` - Training data (90%, ~1.2GB, 7,458 reviews)
- `20240827_val_set.csv` - Validation data (5%, ~71MB, 419 reviews)
- `20240827_random_test_set.csv` - Random test data (5%, ~71MB, 426 reviews)
- `20240827_heart_test_set.csv` - Heart health test data (~54MB, 205 reviews)
- `20240827_HIV_test_set.csv` - HIV test data (~12MB, 100 reviews)

### Dataset 2: Simulated Real-World Search
Location: `20240827_Systematic_review_manual_search_data/`

- 22 CSV files (CD*.csv) representing individual systematic reviews
- Highly imbalanced datasets simulating actual search processes

## Troubleshooting

### Download Issues

**Problem:** Download is slow or times out
```bash
# Try downloading with wget or curl instead:
wget -O "Title and Abstract Screening Data for Systematic Review.zip" \
  "https://data.mendeley.com/public-api/zip/7sgmg89zb6/download/1"

# Or with curl:
curl -L -o "Title and Abstract Screening Data for Systematic Review.zip" \
  "https://data.mendeley.com/public-api/zip/7sgmg89zb6/download/1"
```

**Problem:** Checksum verification fails
- Delete the downloaded ZIP file and try again
- The file may have been corrupted during download

### Extraction Issues

**Problem:** "Not enough disk space"
- Ensure you have at least 3GB of free space
- The compressed ZIP is ~600MB, extracted files are ~2GB

**Problem:** Permission errors
```bash
# Make sure you have write permissions in the directory:
ls -ld .
# If needed, fix permissions:
chmod u+w .
```

### Missing Dependencies

**Problem:** `unzip: command not found`
```bash
# On macOS (install via Homebrew):
brew install unzip

# On Ubuntu/Debian:
sudo apt-get install unzip

# On CentOS/RHEL:
sudo yum install unzip
```

**Problem:** `curl: command not found` and `wget: command not found`
```bash
# On macOS (curl is usually pre-installed):
brew install wget

# On Ubuntu/Debian:
sudo apt-get install wget

# On CentOS/RHEL:
sudo yum install wget
```

## Verifying Installation

After download and extraction, verify the structure:

```bash
# Check directories exist:
ls -d 20240827_*

# Count files in each directory:
ls 20240827_Systematic_Review_Data/ | wc -l       # Should show 5
ls 20240827_Systematic_review_manual_search_data/ | wc -l  # Should show 22

# Check file sizes (on macOS/Linux):
du -sh 20240827_Systematic_Review_Data/
du -sh 20240827_Systematic_review_manual_search_data/
```

## Next Steps

Once the dataset is downloaded:

1. Explore the data:
   ```bash
   # Install Python dependencies if needed:
   pip install -r requirements.txt
   
   # Open the notebook:
   # Quick preview of a small file:
   head -5 20240827_Systematic_review_manual_search_data/CD011218_data_cleaned.csv
   ```

2. Run the exploratory data analysis notebook:
   ```bash
   jupyter notebook eda_systematic_review.ipynb
   ```

3. Start building your ML models!

## Dataset Information

- **Source:** Mendeley Data (DOI: 10.17632/7sgmg89zb6.1)
- **License:** CC BY 4.0 (Creative Commons Attribution)
- **Citation:** Chan et al. (2025), Research Synthesis Methods, 16, 308–322
- **Size:** ~600MB compressed, ~2GB extracted
- **Total Records:** 544,157 titles and abstracts (Dataset 1) + 142,504 publications (Dataset 2)

## Support

If you encounter issues:

1. Check the [Issues](https://github.com/pkoloveas/systematic_review_dataset_EDA/issues) page
2. Review the original dataset documentation: https://data.mendeley.com/datasets/7sgmg89zb6/1
3. Open a new issue with details about your problem

## License & Citation

When using this dataset, please cite:

> Chan, G. C. K., He, E., Leung, J., & Verspoor, K. (2025). A comprehensive systematic review dataset is a rich resource for training and evaluation of AI systems for title and abstract screening. *Research Synthesis Methods*, 16, 308–322. doi:10.1017/rsm.2025.1

The dataset is licensed under CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
