import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EvidenceSynthesizer:
    """Automates systematic review workflow by processing papers with LLM."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize the Evidence Synthesizer.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use (default: gpt-4o, change to gpt-5.2 when available)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"Evidence Synthesizer initialized with model: {self.model}")
    
    def find_indicator_folders(self, base_path: str, vaccine_topic: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Find all indicator folders that contain sources.csv.
        
        Args:
            base_path: Base directory path (e.g., './indicators')
            vaccine_topic: Optional vaccine topic to filter by (e.g., 'Hexavalent', 'RSV')
        
        Returns:
            List of dictionaries containing metadata for each indicator
        """
        base_path = Path(base_path)
        indicator_folders = []
        
        # Traverse the directory structure
        for vaccine_topic_dir in base_path.iterdir():
            if not vaccine_topic_dir.is_dir():
                continue
            
            current_vaccine_topic = vaccine_topic_dir.name
            
            # Skip MD and PDFs folders
            if current_vaccine_topic in ['MD', 'PDFs', 'MD_cleaned']:
                continue
            
            # Filter by vaccine topic if specified
            if vaccine_topic and current_vaccine_topic != vaccine_topic:
                logger.debug(f"Skipping {current_vaccine_topic} (filtering for {vaccine_topic})")
                continue
            
            vaccine_topic_name = current_vaccine_topic
            
            # Look for category folders
            for category_dir in vaccine_topic_dir.iterdir():
                if not category_dir.is_dir():
                    continue
                
                category = category_dir.name
                
                # Look for indicator question folders
                for indicator_dir in category_dir.iterdir():
                    if not indicator_dir.is_dir():
                        continue
                    
                    indicator_question = indicator_dir.name
                    sources_csv = indicator_dir / "sources.csv"
                    
                    # Check if sources.csv exists
                    if sources_csv.exists():
                        indicator_folders.append({
                            'vaccine_topic': vaccine_topic_name,
                            'category': category,
                            'indicator_question': indicator_question,
                            'indicator_path': str(indicator_dir),
                            'sources_csv': str(sources_csv)
                        })
                        logger.info(f"Found indicator: {vaccine_topic_name}/{category}/{indicator_question}")
        
        logger.info(f"Total indicators found: {len(indicator_folders)}")
        return indicator_folders
    
    def parse_sources_csv(self, csv_path: str) -> List[str]:
        """
        Parse sources.csv and extract paper IDs.
        
        Args:
            csv_path: Path to sources.csv file
        
        Returns:
            List of paper IDs
        """
        try:
            df = pd.read_csv(csv_path, delimiter=';')
            
            if 'paper_id' not in df.columns:
                logger.error(f"'paper_id' column not found in {csv_path}")
                return []
            
            paper_ids = df['paper_id'].dropna().tolist()
            logger.info(f"Found {len(paper_ids)} paper IDs in {csv_path}")
            return paper_ids
        
        except Exception as e:
            logger.error(f"Error parsing {csv_path}: {e}")
            return []
    
    def build_paper_id_to_index_map(self, csv_path: str) -> Dict[str, str]:
        """
        Build a mapping from paper_id to index from sources.csv.
        
        Args:
            csv_path: Path to sources.csv file
        
        Returns:
            Dictionary mapping paper_id to index (as string)
        """
        try:
            df = pd.read_csv(csv_path, delimiter=';')
            
            if 'paper_id' not in df.columns or 'index' not in df.columns:
                logger.error(f"Required columns not found in {csv_path}")
                return {}
            
            # Create mapping from paper_id to index
            mapping = {}
            for _, row in df.iterrows():
                if pd.notna(row['paper_id']) and pd.notna(row['index']):
                    mapping[str(row['paper_id']).strip()] = str(int(row['index']))
            
            logger.info(f"Built mapping for {len(mapping)} papers")
            return mapping
        
        except Exception as e:
            logger.error(f"Error building mapping from {csv_path}: {e}")
            return {}
    
    def replace_paper_ids_with_indices(self, text: str, paper_id_to_index: Dict[str, str]) -> str:
        """
        Replace paper IDs with their corresponding indices in the text.
        
        Args:
            text: Text containing paper IDs (e.g., in brackets [paper_id])
            paper_id_to_index: Dictionary mapping paper_id to index
        
        Returns:
            Text with paper IDs replaced by indices
        """
        import re
        
        modified_text = text
        replacements_made = 0
        
        # Find all occurrences of paper_ids in brackets or parentheses
        for paper_id, index in paper_id_to_index.items():
            # Replace [paper_id] with [index]
            pattern1 = re.escape(f"[{paper_id}]")
            if re.search(pattern1, modified_text):
                modified_text = re.sub(pattern1, f"[{index}]", modified_text)
                replacements_made += 1
                logger.debug(f"Replaced [{paper_id}] with [{index}]")
            
            # Replace (paper_id) with (index)
            pattern2 = re.escape(f"({paper_id})")
            if re.search(pattern2, modified_text):
                modified_text = re.sub(pattern2, f"({index})", modified_text)
                replacements_made += 1
                logger.debug(f"Replaced ({paper_id}) with ({index})")
            
            # Replace bare paper_id (with word boundaries)
            pattern3 = r'\b' + re.escape(paper_id) + r'\b'
            if re.search(pattern3, modified_text):
                modified_text = re.sub(pattern3, index, modified_text)
                replacements_made += 1
                logger.debug(f"Replaced bare {paper_id} with {index}")
        
        logger.info(f"Made {replacements_made} replacements")
        return modified_text
    
    def load_paper_content(self, vaccine_topic: str, paper_id: str, base_path: str = "./indicators") -> Optional[str]:
        """
        Load markdown content for a given paper.
        Handles both exact filename matches and timestamped filenames.
        
        Args:
            vaccine_topic: Vaccine topic name
            paper_id: Paper ID
            base_path: Base indicators directory
        
        Returns:
            Markdown content or None if file not found
        """
        # Try MD_cleaned first, then MD
        for folder in ["MD_cleaned", "MD"]:
            folder_path = Path(base_path) / vaccine_topic / folder
            
            if not folder_path.exists():
                continue
            
            # First try exact match
            exact_path = folder_path / f"{paper_id}.md"
            if exact_path.exists():
                try:
                    with open(exact_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    logger.info(f"Loaded paper: {paper_id} ({len(content)} chars) from {exact_path.name}")
                    return content
                except Exception as e:
                    logger.error(f"Error loading paper {paper_id}: {e}")
                    continue
            
            # If not found, search for files starting with paper_id followed by underscore (timestamped files)
            matching_files = list(folder_path.glob(f"{paper_id}_*.md"))
            if matching_files:
                # Use the first match
                paper_path = matching_files[0]
                try:
                    with open(paper_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    logger.info(f"Loaded paper: {paper_id} ({len(content)} chars) from {paper_path.name}")
                    return content
                except Exception as e:
                    logger.error(f"Error loading paper {paper_id}: {e}")
                    continue
        
        logger.warning(f"Paper not found: {paper_id} (tried MD_cleaned and MD folders)")
        return None
    
    def load_prompt_template(self, prompt_path: str) -> str:
        """
        Load prompt template from file.
        
        Args:
            prompt_path: Path to prompt markdown file
        
        Returns:
            Prompt template content
        """
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading prompt template {prompt_path}: {e}")
            raise
    
    def extract_evidence_from_paper(
        self,
        paper_content: str,
        extraction_prompt_template: str,
        paper_id: str,
        vaccine_topic: str = "",
        category: str = "",
        indicator_question: str = ""
    ) -> Optional[Dict]:
        """
        Extract evidence from a single paper using LLM.
        
        Args:
            paper_content: Markdown content of the paper
            extraction_prompt_template: Prompt template for extraction
            paper_id: Paper ID for logging
            vaccine_topic: Vaccine topic name
            category: Category name
            indicator_question: Indicator question
        
        Returns:
            Extracted evidence as JSON dict or None if failed
        """
        try:
            # Inject all variables into prompt
            prompt = extraction_prompt_template
            prompt = prompt.replace("{VACCINE_TOPIC}", vaccine_topic)
            prompt = prompt.replace("{CATEGORY}", category)
            prompt = prompt.replace("{INDICATOR_QUESTION}", indicator_question)
            prompt = prompt.replace("{PAPER_ID}", paper_id)
            prompt = prompt.replace("{FULL_PAPER_TEXT}", paper_content)
            prompt = prompt.replace("{PAPER_CONTENT}", paper_content)  # Fallback for old variable name
            
            logger.info(f"Extracting evidence from paper: {paper_id}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert medical researcher performing systematic literature review."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"✓ Successfully extracted evidence from {paper_id}")
            return result
        
        except Exception as e:
            logger.error(f"✗ Failed to extract evidence from {paper_id}: {e}")
            return None
    
    def synthesize_evidence(
        self,
        aggregated_evidence: List[Dict],
        synthesis_prompt_template: str,
        vaccine_topic: str,
        category: str,
        indicator_question: str
    ) -> str:
        """
        Synthesize evidence from all papers for an indicator.
        
        Args:
            aggregated_evidence: List of extracted evidence JSONs
            synthesis_prompt_template: Prompt template for synthesis
            vaccine_topic: Vaccine topic name
            category: Category name
            indicator_question: Indicator question
        
        Returns:
            Synthesized text
        """
        try:
            # Convert aggregated evidence to string
            aggregated_json_str = json.dumps(aggregated_evidence, indent=2)
            
            # Replace placeholders in prompt
            prompt = synthesis_prompt_template
            prompt = prompt.replace("{VACCINE_TOPIC}", vaccine_topic)
            prompt = prompt.replace("{CATEGORY}", category)
            prompt = prompt.replace("{INDICATOR_QUESTION}", indicator_question)
            prompt = prompt.replace("{AGGREGATED_JSON_LIST}", aggregated_json_str)
            
            logger.info(f"Synthesizing evidence for: {vaccine_topic}/{category}/{indicator_question}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert medical researcher synthesizing evidence for systematic reviews."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            
            result = response.choices[0].message.content
            logger.info(f"✓ Successfully synthesized evidence")
            return result
        
        except Exception as e:
            logger.error(f"✗ Failed to synthesize evidence: {e}")
            raise
    
    def process_indicator(
        self,
        indicator_metadata: Dict,
        extraction_prompt_template: str,
        synthesis_prompt_template: str,
        base_path: str = "./indicators",
        replace_paper_ids: bool = False
    ) -> bool:
        """
        Process a single indicator: extract from papers and synthesize.
        
        Args:
            indicator_metadata: Metadata dict containing paths and names
            extraction_prompt_template: Template for extraction prompt
            synthesis_prompt_template: Template for synthesis prompt
            base_path: Base indicators directory
            replace_paper_ids: If True, replace paper IDs with indices from sources.csv
        
        Returns:
            True if successful, False otherwise
        """
        vaccine_topic = indicator_metadata['vaccine_topic']
        category = indicator_metadata['category']
        indicator_question = indicator_metadata['indicator_question']
        indicator_path = Path(indicator_metadata['indicator_path'])
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing: {vaccine_topic}/{category}/{indicator_question}")
        logger.info(f"{'='*80}")
        
        # Create LLM_output folder
        llm_output_dir = indicator_path / "LLM_output"
        llm_output_dir.mkdir(exist_ok=True)
        logger.info(f"Output directory: {llm_output_dir}")
        
        # Parse sources.csv
        paper_ids = self.parse_sources_csv(indicator_metadata['sources_csv'])
        if not paper_ids:
            logger.warning(f"No papers found for this indicator. Skipping.")
            return False
        
        # Step 1: Extract evidence from each paper
        extracted_evidence = []
        
        for idx, paper_id in enumerate(paper_ids, 1):
            logger.info(f"\n[{idx}/{len(paper_ids)}] Processing paper: {paper_id}")
            
            # Load paper content
            paper_content = self.load_paper_content(vaccine_topic, paper_id, base_path)
            if paper_content is None:
                logger.warning(f"Skipping paper {paper_id} (not found)")
                continue
            
            # Extract evidence
            evidence = self.extract_evidence_from_paper(
                paper_content,
                extraction_prompt_template,
                paper_id,
                vaccine_topic,
                category,
                indicator_question
            )
            
            if evidence:
                # Add paper_id to evidence
                evidence['paper_id'] = paper_id
                
                # Save individual extraction
                extraction_file = llm_output_dir / f"{paper_id}_extraction.json"
                with open(extraction_file, 'w', encoding='utf-8') as f:
                    json.dump(evidence, f, indent=2)
                logger.info(f"Saved extraction to: {extraction_file}")
                
                extracted_evidence.append(evidence)
        
        if not extracted_evidence:
            logger.warning(f"No evidence extracted for this indicator. Skipping synthesis.")
            return False
        
        # Save aggregated evidence
        aggregated_file = llm_output_dir / "aggregated_evidence.json"
        with open(aggregated_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_evidence, f, indent=2)
        logger.info(f"Saved aggregated evidence to: {aggregated_file}")
        
        # Step 2: Synthesize evidence
        synthesis_result = self.synthesize_evidence(
            extracted_evidence,
            synthesis_prompt_template,
            vaccine_topic,
            category,
            indicator_question
        )
        
        # Step 3: Replace paper IDs with indices from sources.csv (if enabled)
        if replace_paper_ids:
            logger.info("Replacing paper IDs with source indices...")
            paper_id_to_index = self.build_paper_id_to_index_map(indicator_metadata['sources_csv'])
            if paper_id_to_index:
                synthesis_result = self.replace_paper_ids_with_indices(synthesis_result, paper_id_to_index)
                logger.info("✓ Paper IDs replaced with indices")
            else:
                logger.warning("Could not build paper ID to index mapping, skipping replacement")
        
        # Save synthesis result
        synthesis_file = llm_output_dir / "synthesis_result.md"
        with open(synthesis_file, 'w', encoding='utf-8') as f:
            f.write(synthesis_result)
        logger.info(f"Saved synthesis to: {synthesis_file}")
        
        logger.info(f"✓ Successfully processed indicator")
        return True
    
    def run_full_workflow(
        self,
        base_path: str = "./indicators",
        extraction_prompt_path: str = "prompts/extraction_prompt.md",
        synthesis_prompt_path: str = "prompts/synthesis_prompt.md",
        vaccine_topic: Optional[str] = None,
        replace_paper_ids: bool = False
    ):
        """
        Run the complete evidence synthesis workflow.
        
        Args:
            base_path: Base indicators directory
            extraction_prompt_path: Path to extraction prompt template
            synthesis_prompt_path: Path to synthesis prompt template
            vaccine_topic: Optional vaccine topic to filter by (e.g., 'Hexavalent', 'RSV')
            replace_paper_ids: If True, replace paper IDs with indices from sources.csv (default: False)
        """
        logger.info("="*80)
        logger.info("Starting Evidence Synthesis Workflow")
        logger.info("="*80)
        
        # Load prompt templates
        logger.info("Loading prompt templates...")
        extraction_prompt = self.load_prompt_template(extraction_prompt_path)
        synthesis_prompt = self.load_prompt_template(synthesis_prompt_path)
        
        # Find all indicator folders
        if vaccine_topic:
            logger.info(f"Scanning directory: {base_path} (filtering for {vaccine_topic})")
        else:
            logger.info(f"Scanning directory: {base_path} (all vaccine topics)")
        indicators = self.find_indicator_folders(base_path, vaccine_topic)
        
        if not indicators:
            logger.warning("No indicators found!")
            return
        
        # Process each indicator
        success_count = 0
        failure_count = 0
        
        for idx, indicator in enumerate(indicators, 1):
            logger.info(f"\n\n{'#'*80}")
            logger.info(f"Indicator {idx}/{len(indicators)}")
            logger.info(f"{'#'*80}")
            
            try:
                success = self.process_indicator(
                    indicator,
                    extraction_prompt,
                    synthesis_prompt,
                    base_path,
                    replace_paper_ids
                )
                if success:
                    success_count += 1
                else:
                    failure_count += 1
            except Exception as e:
                logger.error(f"Error processing indicator: {e}")
                failure_count += 1
        
        # Final summary
        logger.info("\n\n" + "="*80)
        logger.info("WORKFLOW COMPLETE")
        logger.info("="*80)
        logger.info(f"Total indicators: {len(indicators)}")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {failure_count}")
        logger.info("="*80)


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def run_evidence_synthesis(
    base_path: str = "./indicators",
    extraction_prompt_path: str = "prompts/extraction_prompt.md",
    synthesis_prompt_path: str = "prompts/synthesis_prompt.md",
    api_key: Optional[str] = None,
    model: str = "gpt-4o",
    vaccine_topic: Optional[str] = None,
    replace_paper_ids: bool = False
):
    """
    Convenience function to run the complete evidence synthesis workflow.
    
    Args:
        base_path: Base indicators directory
        extraction_prompt_path: Path to extraction prompt template
        synthesis_prompt_path: Path to synthesis prompt template
        api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        model: Model to use (change to gpt-5.2 when available)
        vaccine_topic: Optional vaccine topic to filter by (e.g., 'Hexavalent', 'RSV')
        replace_paper_ids: If True, replace paper IDs with indices from sources.csv (default: False)
    """
    synthesizer = EvidenceSynthesizer(api_key=api_key, model=model)
    synthesizer.run_full_workflow(base_path, extraction_prompt_path, synthesis_prompt_path, vaccine_topic, replace_paper_ids)


def replace_paper_ids_in_synthesis_results(
    base_path: str = "./indicators",
    vaccine_topic: Optional[str] = None
):
    """
    Post-process existing synthesis results to replace paper IDs with indices.
    Useful for running on already-generated synthesis results.
    
    Args:
        base_path: Base indicators directory
        vaccine_topic: Optional vaccine topic to filter by (e.g., 'Hexavalent', 'RSV')
    """
    base_path = Path(base_path)
    processed_count = 0
    
    # Find all synthesis_result.md files
    pattern = "**/**/LLM_output/synthesis_result.md"
    synthesis_files = list(base_path.glob(pattern))
    
    logger.info(f"Found {len(synthesis_files)} synthesis result files")
    
    for synthesis_file in synthesis_files:
        # Parse the path to get metadata
        parts = synthesis_file.parts
        try:
            # Find indicators folder index
            indicators_idx = parts.index('indicators')
            vaccine = parts[indicators_idx + 1]
            
            # Filter by vaccine topic if specified
            if vaccine_topic and vaccine != vaccine_topic:
                continue
            
            # Find sources.csv in the parent directory
            indicator_dir = synthesis_file.parent.parent
            sources_csv = indicator_dir / "sources.csv"
            
            if not sources_csv.exists():
                logger.warning(f"sources.csv not found for {synthesis_file}")
                continue
            
            # Read the synthesis result
            with open(synthesis_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Build mapping and replace
            synthesizer = EvidenceSynthesizer()
            paper_id_to_index = synthesizer.build_paper_id_to_index_map(str(sources_csv))
            
            if paper_id_to_index:
                modified_content = synthesizer.replace_paper_ids_with_indices(content, paper_id_to_index)
                
                # Save back
                with open(synthesis_file, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                logger.info(f"✓ Updated {synthesis_file.relative_to(base_path)}")
                processed_count += 1
            else:
                logger.warning(f"Could not build mapping for {synthesis_file}")
                
        except (ValueError, IndexError) as e:
            logger.error(f"Error processing {synthesis_file}: {e}")
            continue
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Processed {processed_count} synthesis result files")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    # Example usage
    run_evidence_synthesis()
