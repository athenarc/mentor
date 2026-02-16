import os
import re
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from mistralai import Mistral, DocumentURLChunk
from mistralai.models. ocrresponse import OCRResponse
from openai import OpenAI

# ============================================================================
# CONFIGURATION
# ============================================================================

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "your_mistral_api_key_here")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_deepseek_api_key_here")
DEEPSEEK_API_HOST = os.getenv("DEEPSEEK_API_HOST", "your_deepseek_api_host_here")

OUTPUT_DIR = Path("./ocr_output")
OUTPUT_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def safe_filename(filename: str) -> str:
    """Convert filename to safe format."""
    name = Path(filename).stem
    safe_name = re.sub(r'[^\w\s-]', '', name)
    safe_name = re.sub(r'[-\s]+', '-', safe_name)
    return safe_name. strip('-_')[:100]


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def clean_markdown_output(
    markdown_content: str,
    api_key: str = DEEPSEEK_API_KEY,
    model: str = "deepseek-reasoner"
) -> str:
    """
    Clean and process markdown content using DeepSeek API.
    
    Removes irrelevant text, fixes layout inconsistencies, and keeps only English text.
    
    Args:
        markdown_content: Raw markdown content to clean
        api_key: DeepSeek API key
        model: DeepSeek model to use (default: deepseek-chat)
    
    Returns:
        Cleaned markdown content
    """
    if not markdown_content or not markdown_content.strip():
        logger.warning("Empty markdown content provided for cleaning")
        return ""
    
    logger.info("Cleaning markdown with DeepSeek...")
    
    client = OpenAI(
        api_key=api_key,
        base_url=DEEPSEEK_API_HOST
    )
    
    system_prompt = """You are an expert document processor. Your task is to clean and format markdown documents from OCR output.

Your responsibilities:
1. Remove irrelevant text (headers, footers, page numbers, watermarks, metadata)
2. Fix layout inconsistencies (inconsistent spacing, broken formatting, misaligned text)
3. Keep ONLY text written in English - remove any text in other languages
4. Preserve the semantic structure and meaningful content
5. Ensure proper markdown formatting (headings, lists, paragraphs)
6. Fix obvious OCR errors when possible
7. Remove duplicate content

Return only the cleaned markdown. Do not add explanations or comments."""

    user_prompt = f"""Please clean and process the following markdown document:

{markdown_content}

Remember to:
- Remove irrelevant text
- Fix layout issues
- Keep only English text
- Maintain proper markdown structure"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=16000
        )
        
        cleaned_content = response.choices[0].message.content
        logger.info(f"✓ Markdown cleaned successfully (reduced from {len(markdown_content)} to {len(cleaned_content)} chars)")
        
        return cleaned_content
    
    except Exception as e:
        logger.error(f"✗ Failed to clean markdown with DeepSeek: {e}")
        raise RuntimeError(f"DeepSeek cleaning failed: {str(e)}")


# ============================================================================
# MAIN OCR SERVICE CLASS
# ============================================================================

class MistralOCRService: 
    """Service for processing PDFs with Mistral AI OCR (text only)."""
    
    def __init__(self, api_key:  str, output_dir: Path = OUTPUT_DIR):
        """
        Initialize the Mistral OCR service.
        
        Args:
            api_key: Mistral API key
            output_dir: Directory to save markdown files
        """
        self. mistral_client = Mistral(api_key=api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Mistral OCR Service initialized. Output dir: {self.output_dir}")
    
    def _get_combined_markdown(self, ocr_response: OCRResponse) -> str:
        """
        Combine OCR response pages into a single markdown document.
        
        Args:
            ocr_response: Response from Mistral OCR API
        
        Returns:
            Combined markdown text
        """
        if not ocr_response.pages:
            logger.warning("OCR response contains no pages")
            return ""
        
        markdowns = []
        
        for idx, page in enumerate(ocr_response.pages, 1):
            logger.info(f"Processing page {idx}/{len(ocr_response.pages)}")
            # Simply append the markdown text from each page
            markdowns.append(page.markdown)
        
        return "\n\n".join(markdowns)
    
    def process_pdf_file(self, pdf_path: str, save_markdown: bool = True, force: bool = False) -> str:
        """
        Process a PDF file from a file path.
        
        Args:
            pdf_path: Path to PDF file
            save_markdown: Whether to save the markdown to a file
            force: If True, reprocess even if output file exists
        
        Returns: 
            Extracted markdown content
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found:  {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File must be a PDF:  {pdf_path}")
        
        # Check if output already exists
        if not force and save_markdown:
            expected_output = self._get_output_path(pdf_path.name)
            if expected_output.exists():
                logger.info(f"⏭️  Skipping {pdf_path.name} (output already exists: {expected_output.name})")
                with open(expected_output, 'r', encoding='utf-8') as f:
                    return f.read()
        
        # Read PDF bytes
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        logger.info(f"Read PDF file: {pdf_path. name} ({format_file_size(len(pdf_bytes))})")
        
        # Process PDF
        markdown = self. process_pdf_bytes(
            pdf_bytes=pdf_bytes,
            filename=pdf_path.name,
            save_markdown=save_markdown
        )
        
        return markdown
    
    def process_pdf_bytes(
        self, 
        pdf_bytes: bytes, 
        filename: Optional[str] = None,
        save_markdown: bool = True
    ) -> str:
        """
        Process PDF bytes with Mistral OCR and return markdown.
        
        Args:
            pdf_bytes: PDF file content as bytes
            filename: Original filename (optional)
            save_markdown: Whether to save the markdown to a file
        
        Returns:
            Extracted markdown content
        """
        if not pdf_bytes:
            raise ValueError("Empty PDF bytes provided")
        
        # Validate PDF signature
        if not pdf_bytes. startswith(b'%PDF-'):
            raise ValueError("Invalid PDF file:  does not start with PDF signature")
        
        filename = filename or "document.pdf"
        logger.info(f"Starting OCR processing:  {filename} ({format_file_size(len(pdf_bytes))})")
        
        uploaded_file = None
        
        try:
            # Step 1: Upload file to Mistral
            logger.info("Uploading file to Mistral AI...")
            uploaded_file = self.mistral_client.files.upload(
                file={
                    "file_name":  filename,
                    "content": pdf_bytes,
                },
                purpose="ocr"
            )
            
            if not hasattr(uploaded_file, 'id'):
                raise RuntimeError(f"Invalid response from Mistral API: {uploaded_file}")
            
            logger.info(f"✓ File uploaded with ID: {uploaded_file.id}")
            
            # Step 2: Get signed URL for the uploaded file
            logger.info("Getting signed URL...")
            signed_url = self.mistral_client.files.get_signed_url(
                file_id=uploaded_file.id,
                expiry=1  # 1 hour expiry
            )
            logger.info(f"✓ Got signed URL")
            
            # Step 3: Process OCR (text only, no images)
            logger.info("Processing OCR (this may take a while)...")
            ocr_response = self.mistral_client.ocr.process(
                document=DocumentURLChunk(document_url=signed_url. url),
                model="mistral-ocr-latest",
                include_image_base64=False  # Skip image processing
            )
            
            logger.info(f"✓ OCR processing completed")
            logger.info(f"  Pages extracted: {len(ocr_response.pages) if ocr_response.pages else 0}")
            
            # Step 4: Convert to markdown (text only)
            markdown = self._get_combined_markdown(ocr_response)
            
            if not markdown:
                logger.warning("No content extracted from PDF")
                markdown = "# No Content\n\nNo text could be extracted from the PDF."
            
            # Step 5: Save to file if requested
            if save_markdown:
                output_path = self.save_markdown(markdown, filename)
                logger.info(f"✓ Markdown saved to: {output_path}")
            
            logger.info("✓ OCR processing completed successfully")
            return markdown
            
        except Exception as e:
            logger.error(f"✗ OCR processing failed: {e}")
            raise RuntimeError(f"Failed to process PDF with OCR: {str(e)}")
        
        finally:
            # Step 6: Cleanup - Delete uploaded file from Mistral
            if uploaded_file and hasattr(uploaded_file, 'id'):
                try:
                    self.mistral_client.files.delete(file_id=uploaded_file.id)
                    logger.info(f"✓ Cleaned up Mistral file ID: {uploaded_file.id}")
                except Exception as e: 
                    logger.warning(f"Failed to delete Mistral file {uploaded_file.id}: {e}")
    
    def _get_output_path(self, original_filename: Optional[str] = None) -> Path:
        """
        Get the output path for a given PDF filename.
        
        Args:
            original_filename: Original PDF filename
        
        Returns:
            Path to output markdown file
        """
        if original_filename:
            base_name = Path(original_filename).stem
            safe_name = safe_filename(base_name)
            output_filename = f"{safe_name}.md"
        else:
            output_filename = "extracted.md"
        
        return self.output_dir / output_filename
    
    def save_markdown(self, content: str, original_filename: Optional[str] = None) -> Path:
        """
        Save markdown content to a file.
        
        Args:
            content:  Markdown content to save
            original_filename: Original PDF filename
        
        Returns:
            Path to saved markdown file
        """
        if not content:
            logger.warning("Empty content provided for saving")
            content = "# No Content\n\nNo text could be extracted."
        
        # Generate deterministic output filename (no timestamp)
        output_path = self._get_output_path(original_filename)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    def process_multiple_pdfs(self, pdf_paths: list, save_markdown: bool = True, force: bool = False) -> dict:
        """
        Process multiple PDF files.
        
        Args:
            pdf_paths: List of paths to PDF files
            save_markdown: Whether to save markdown files
            force: If True, reprocess even if output files exist
        
        Returns:
            Dictionary mapping filenames to markdown content
        """
        results = {}
        skipped = 0
        processed = 0
        
        for idx, pdf_path in enumerate(pdf_paths, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing file {idx}/{len(pdf_paths)}: {pdf_path}")
            logger.info(f"{'='*60}")
            
            try: 
                markdown = self.process_pdf_file(pdf_path, save_markdown=save_markdown, force=force)
                # Check if it was skipped
                expected_output = self._get_output_path(Path(pdf_path).name)
                was_skipped = not force and save_markdown and expected_output.exists()
                
                results[str(pdf_path)] = {
                    'status': 'success',
                    'markdown': markdown,
                    'length': len(markdown),
                    'skipped': was_skipped
                }
                if was_skipped:
                    skipped += 1
                else:
                    processed += 1
            except Exception as e: 
                logger.error(f"Failed to process {pdf_path}: {e}")
                results[str(pdf_path)] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Batch processing complete: {processed} processed, {skipped} skipped")
        logger.info(f"{'='*60}")
        
        return results


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def quick_process_pdf(pdf_path: str, api_key: str = MISTRAL_API_KEY, force: bool = False) -> str:
    """
    Quick function to process a single PDF file.
    
    Args:
        pdf_path: Path to PDF file
        api_key: Mistral API key
        force: If True, reprocess even if output file exists
    
    Returns:
        Extracted markdown content
    """
    service = MistralOCRService(api_key=api_key)
    return service.process_pdf_file(pdf_path, force=force)


def batch_process_pdfs(pdf_directory: str, api_key: str = MISTRAL_API_KEY, output_dir: Optional[Path] = None, force: bool = False) -> dict:
    """
    Process all PDF files in a directory.
    
    Args:
        pdf_directory: Directory containing PDF files
        api_key: Mistral API key
        output_dir: Directory to save markdown files (optional)
        force: If True, reprocess even if output files exist
    
    Returns: 
        Dictionary with processing results
    """
    pdf_dir = Path(pdf_directory)
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {pdf_directory}")
        return {}
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    service = MistralOCRService(api_key=api_key, output_dir=output_dir or OUTPUT_DIR)
    return service.process_multiple_pdfs(pdf_files, force=force)


# ============================================================================
# DEEPSEEK CLEANING FUNCTIONS
# ============================================================================

def clean_markdown_file(
    markdown_path: str,
    output_path: Optional[str] = None,
    api_key: str = DEEPSEEK_API_KEY,
    force: bool = False
) -> str:
    """
    Clean a markdown file using DeepSeek.
    
    Args:
        markdown_path: Path to markdown file
        output_path: Path to save cleaned markdown (if None, overwrites original)
        api_key: DeepSeek API key
        force: If True, reprocess even if output exists
    
    Returns:
        Cleaned markdown content
    """
    markdown_path = Path(markdown_path)
    
    if not markdown_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")
    
    # Determine output path
    if output_path is None:
        output_path = markdown_path
    else:
        output_path = Path(output_path)
    
    # Check if already processed
    if not force and output_path.exists() and output_path != markdown_path:
        logger.info(f"⏭️  Skipping {markdown_path.name} (cleaned version already exists)")
        with open(output_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    # Read original content
    logger.info(f"Reading {markdown_path.name}...")
    with open(markdown_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Clean with DeepSeek
    cleaned_content = clean_markdown_output(original_content, api_key=api_key)
    
    # Save cleaned content
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    logger.info(f"✓ Cleaned markdown saved to: {output_path}")
    
    return cleaned_content


def batch_clean_markdown_files(
    markdown_directory: str,
    output_directory: Optional[str] = None,
    api_key: str = DEEPSEEK_API_KEY,
    force: bool = False
) -> dict:
    """
    Clean all markdown files in a directory using DeepSeek.
    
    Args:
        markdown_directory: Directory containing markdown files
        output_directory: Directory to save cleaned files (if None, overwrites originals)
        api_key: DeepSeek API key
        force: If True, reprocess even if output files exist
    
    Returns:
        Dictionary with cleaning results
    """
    md_dir = Path(markdown_directory)
    md_files = list(md_dir.glob("*.md"))
    
    if not md_files:
        logger.warning(f"No markdown files found in {markdown_directory}")
        return {}
    
    logger.info(f"Found {len(md_files)} markdown files to clean")
    
    # Create output directory if specified
    if output_directory:
        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = None
    
    results = {}
    skipped = 0
    processed = 0
    
    for idx, md_path in enumerate(md_files, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"Cleaning file {idx}/{len(md_files)}: {md_path.name}")
        logger.info(f"{'='*60}")
        
        try:
            # Determine output path
            if output_dir:
                output_path = output_dir / md_path.name
            else:
                output_path = md_path
            
            # Check if already processed
            if not force and output_dir and output_path.exists():
                logger.info(f"⏭️  Skipping {md_path.name} (cleaned version already exists)")
                with open(output_path, 'r', encoding='utf-8') as f:
                    cleaned_content = f.read()
                skipped += 1
            else:
                cleaned_content = clean_markdown_file(
                    str(md_path),
                    str(output_path) if output_dir else None,
                    api_key=api_key,
                    force=force
                )
                processed += 1
            
            results[str(md_path)] = {
                'status': 'success',
                'output_path': str(output_path),
                'length': len(cleaned_content)
            }
            
        except Exception as e:
            logger.error(f"Failed to clean {md_path}: {e}")
            results[str(md_path)] = {
                'status': 'error',
                'error': str(e)
            }
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Batch cleaning complete: {processed} processed, {skipped} skipped")
    logger.info(f"{'='*60}")
    
    return results