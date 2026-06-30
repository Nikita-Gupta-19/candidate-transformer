import argparse
import json
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.parsers.csv_parser import CSVParser
from src.parsers.resume_parser import ResumeParser
from src.merger.merger import CandidateMerger
from src.projection.projector import Projector
from src.validators.validators import validate_canonical_profile, validate_output_schema

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Eightfold Candidate Data Transformer")
    parser.add_argument("--csv", help="Path to recruiter CSV file")
    parser.add_argument("--resume", help="Path to candidate resume file (PDF/DOCX/TXT)")
    parser.add_argument("--config", help="Path to runtime configuration JSON", default=None)
    parser.add_argument("--output", help="Output JSON file path", default="output.json")
    
    args = parser.parse_args()
    
    profiles = []
    
    if args.csv:
        logger.info(f"Parsing CSV: {args.csv}")
        csv_parser = CSVParser(args.csv)
        profiles.extend(csv_parser.parse())
        
    if args.resume:
        logger.info(f"Parsing Resume: {args.resume}")
        resume_parser = ResumeParser(args.resume)
        profiles.extend(resume_parser.parse())
        
    if not profiles:
        logger.error("No input files provided or no profiles parsed. Use --csv and/or --resume.")
        sys.exit(1)
        
    # Merge
    logger.info("Merging profiles and resolving conflicts...")
    merger = CandidateMerger()
    merged_profiles = merger.merge_all(profiles)
    
    # Validate Canonical
    logger.info("Validating canonical profiles...")
    valid_profiles = [validate_canonical_profile(p) for p in merged_profiles]
    
    # Load Config
    config = {}
    if args.config:
        logger.info(f"Loading custom configuration from {args.config}")
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config {args.config}: {e}")
            sys.exit(1)
    else:
        logger.info("Using default output configuration.")
            
    # Project & Validate Output
    logger.info("Applying projection and validating output schema...")
    projector = Projector(config)
    final_outputs = []
    
    for p in valid_profiles:
        projected = projector.project(p)
        try:
            validate_output_schema(projected, config)
            # Remove null values if requested or keep clean
            final_outputs.append(projected)
        except ValueError as e:
            logger.warning(f"Profile {p.candidate_id} failed output validation: {e}. Dropping.")
            
    # Output
    try:
        with open(args.output, 'w') as f:
            json.dump(final_outputs, f, indent=2)
        logger.info(f"Successfully wrote {len(final_outputs)} canonical profiles to {args.output}")
    except Exception as e:
        logger.error(f"Failed to write output to {args.output}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
