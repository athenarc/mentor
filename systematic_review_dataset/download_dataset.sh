#!/usr/bin/env bash

#######################################################################
# Download and extract the Systematic Review Dataset from Mendeley Data
#
# Dataset: Title and Abstract Screening Data for Systematic Review
# DOI: 10.17632/7sgmg89zb6.1
# License: CC BY 4.0
#
# Usage: ./download_dataset.sh [OPTIONS]
# Options:
#   --no-unzip        Don't automatically extract ZIP files
#   --no-delete       Don't automatically delete ZIP files after extraction
#   -h, --help        Show this help message
#######################################################################

set -e  # Exit on error

# Dataset metadata
DOWNLOAD_URL="https://data.mendeley.com/public-api/zip/7sgmg89zb6/download/1"
ZIP_FILENAME="Title and Abstract Screening Data for Systematic Review.zip"
EXPECTED_CHECKSUM="27dc9142917b9b528bfcc4bc57532181fb7d792883e19d02b1a001f0ce6a0eba"

# Default flags (enabled by default)
AUTO_UNZIP=true
AUTO_DELETE=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

#######################################################################
# Helper Functions
#######################################################################

print_header() {
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

show_help() {
    cat << EOF
Download Systematic Review Dataset

USAGE:
    ./download_dataset.sh [OPTIONS]

OPTIONS:
    --no-unzip        Don't automatically extract ZIP files (keep them compressed)
    --no-delete       Don't automatically delete ZIP files after extraction
    -h, --help        Show this help message

EXAMPLES:
    # Download and auto-extract everything (default):
    ./download_dataset.sh

    # Download but don't extract:
    ./download_dataset.sh --no-unzip

    # Extract but keep ZIP files:
    ./download_dataset.sh --no-delete

    # Download only (no extraction, keep ZIPs):
    ./download_dataset.sh --no-unzip --no-delete

DATASET INFO:
    Source:    Mendeley Data (DOI: 10.17632/7sgmg89zb6.1)
    License:   CC BY 4.0
    Citation:  Chan et al. (2025), Research Synthesis Methods, 16, 308–322
    Size:      ~600MB compressed, ~2GB extracted

EOF
    exit 0
}

calculate_checksum() {
    local file="$1"
    if command -v shasum &> /dev/null; then
        shasum -a 256 "$file" | awk '{print $1}'
    elif command -v sha256sum &> /dev/null; then
        sha256sum "$file" | awk '{print $1}'
    else
        print_error "Neither shasum nor sha256sum found. Cannot verify checksum."
        return 1
    fi
}

download_file() {
    local url="$1"
    local output="$2"
    
    print_info "Downloading dataset from Mendeley Data..."
    echo "URL: $url"
    
    if command -v curl &> /dev/null; then
        curl -L --progress-bar -o "$output" "$url"
    elif command -v wget &> /dev/null; then
        wget --show-progress -O "$output" "$url"
    else
        print_error "Neither curl nor wget found. Please install one of them."
        exit 1
    fi
    
    print_success "Download complete: $output"
}

verify_checksum() {
    local file="$1"
    local expected="$2"
    
    print_info "Verifying file integrity..."
    
    local actual
    actual=$(calculate_checksum "$file")
    
    if [ "$actual" = "$expected" ]; then
        print_success "Checksum verified: $actual"
        return 0
    else
        print_error "Checksum mismatch!"
        echo "  Expected: $expected"
        echo "  Actual:   $actual"
        return 1
    fi
}

extract_zip() {
    local zip_file="$1"
    local extract_to="${2:-.}"
    
    if [ ! -f "$zip_file" ]; then
        print_error "ZIP file not found: $zip_file"
        return 1
    fi
    
    print_info "Extracting: $(basename "$zip_file")"
    
    if command -v unzip &> /dev/null; then
        unzip -q -o "$zip_file" -d "$extract_to"
    else
        print_error "unzip command not found. Please install unzip."
        return 1
    fi
    
    print_success "Extraction complete: $(basename "$zip_file")"
}

#######################################################################
# Parse Arguments
#######################################################################

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-unzip)
            AUTO_UNZIP=false
            shift
            ;;
        --no-delete)
            AUTO_DELETE=false
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

#######################################################################
# Main Execution
#######################################################################

main() {
    # Get script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    
    print_header "Systematic Review Dataset Downloader"
    echo ""
    echo "Dataset: Title and Abstract Screening Data for Systematic Review"
    echo "DOI: 10.17632/7sgmg89zb6.1"
    echo "License: CC BY 4.0"
    echo "Citation: Chan et al. (2025), Research Synthesis Methods, 16, 308–322"
    echo ""
    print_header ""
    echo ""
    
    # Show configuration
    print_info "Configuration:"
    echo "  Auto-unzip: $AUTO_UNZIP"
    echo "  Auto-delete: $AUTO_DELETE"
    echo ""
    
    # Check if dataset directories already exist
    if [ -d "20240827_Systematic_Review_Data" ] && [ -d "20240827_Systematic_review_manual_search_data" ]; then
        print_warning "Dataset directories already exist."
        read -p "Do you want to re-download and overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborted."
            exit 0
        fi
    fi
    
    # Download the main ZIP file
    if [ ! -f "$ZIP_FILENAME" ]; then
        download_file "$DOWNLOAD_URL" "$ZIP_FILENAME"
    else
        print_info "Main ZIP file already exists: $ZIP_FILENAME"
    fi
    
    # Verify checksum
    if ! verify_checksum "$ZIP_FILENAME" "$EXPECTED_CHECKSUM"; then
        print_error "File integrity check failed. Please delete the file and try again."
        exit 1
    fi
    
    # Extract main ZIP if auto-unzip is enabled
    if [ "$AUTO_UNZIP" = true ]; then
        echo ""
        print_header "Extracting Dataset Files"
        echo ""
        
        # Extract main ZIP (contains 2 nested ZIPs and a directory)
        extract_zip "$ZIP_FILENAME" "."
        
        # Extract nested ZIPs
        NESTED_ZIPS=(
            "20240827_Systematic_Review_Data.zip"
            "20240827_Systematic_review_manual_search_data.zip"
        )
        
        for nested_zip in "${NESTED_ZIPS[@]}"; do
            if [ -f "$nested_zip" ]; then
                extract_zip "$nested_zip" "."
                
                # Delete nested ZIP if auto-delete is enabled
                if [ "$AUTO_DELETE" = true ]; then
                    rm "$nested_zip"
                    print_success "Deleted: $nested_zip"
                fi
            else
                print_warning "Nested ZIP not found (might be inside a directory): $nested_zip"
            fi
        done
        
        # Check if ZIPs are in a subdirectory
        if [ -d "Title and Abstract Screening Data for Systematic Review" ]; then
            cd "Title and Abstract Screening Data for Systematic Review"
            
            for nested_zip in "${NESTED_ZIPS[@]}"; do
                if [ -f "$nested_zip" ]; then
                    extract_zip "$nested_zip" "$SCRIPT_DIR"
                    
                    # Delete nested ZIP if auto-delete is enabled
                    if [ "$AUTO_DELETE" = true ]; then
                        rm "$nested_zip"
                        print_success "Deleted: $nested_zip"
                    fi
                fi
            done
            
            cd "$SCRIPT_DIR"
            
            # Remove the now-empty subdirectory if auto-delete is enabled
            if [ "$AUTO_DELETE" = true ]; then
                rm -rf "Title and Abstract Screening Data for Systematic Review"
                print_success "Cleaned up extraction directory"
            fi
        fi
        
        # Delete main ZIP if auto-delete is enabled
        if [ "$AUTO_DELETE" = true ]; then
            rm "$ZIP_FILENAME"
            print_success "Deleted: $ZIP_FILENAME"
        fi
    else
        print_info "Skipping extraction (--no-unzip flag set)"
        print_info "To extract manually, run: unzip \"$ZIP_FILENAME\""
    fi
    
    # Final summary
    echo ""
    print_header "Setup Complete!"
    echo ""
    
    if [ "$AUTO_UNZIP" = true ]; then
        print_success "Dataset files are ready!"
        echo ""
        echo "Dataset structure:"
        echo "  • 20240827_Systematic_Review_Data/"
        echo "      Contains: dev_set, val_set, random_test_set, heart_test_set, HIV_test_set"
        echo "  • 20240827_Systematic_review_manual_search_data/"
        echo "      Contains: 22 individual review datasets (CD*.csv)"
        echo ""
        echo "You can now proceed with your analysis!"
    else
        print_success "Download complete!"
        echo ""
        echo "To extract the dataset, run:"
        echo "  ./download_dataset.sh"
        echo ""
        echo "Or extract manually with:"
        echo "  unzip \"$ZIP_FILENAME\""
    fi
    
    if [ "$AUTO_DELETE" = false ] && [ "$AUTO_UNZIP" = true ]; then
        echo ""
        print_info "ZIP files have been preserved (--no-delete flag)"
    fi
}

# Run main function
main

exit 0
