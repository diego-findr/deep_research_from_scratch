import json
import os
from pathlib import Path

def main():
    # Define paths to existing test data
    base_dir = Path(".")
    candidate_path = base_dir / "tests/candidates/outputs/enriched_prl_valid_1.json"
    job_path = base_dir / "tests/jobs/outputs/enriched_acciona_prl.json"
    
    # Check if files exist
    if not candidate_path.exists():
        print(f"Error: Candidate file not found at {candidate_path}")
        # Try fallback
        candidate_path = base_dir / "tests/candidates/outputs/enriched_prl_valid_1.json"
        if not candidate_path.exists():
            print("No candidate files found.")
            return

    if not job_path.exists():
        print(f"Error: Job file not found at {job_path}")
        return

    print(f"Using candidate: {candidate_path}")
    print(f"Using job: {job_path}")

    # Load data
    try:
        with open(candidate_path, 'r', encoding='utf-8') as f:
            candidate = json.load(f)
        
        with open(job_path, 'r', encoding='utf-8') as f:
            job = json.load(f)
            
        # Create payload structure
        payload = {
            "enriched_candidate": candidate,
            "enriched_job": job,
            "max_debate_rounds": 2
        }
        
        # Save to payload.json
        output_path = base_dir / "payload.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            
        print(f"\n✅ Successfully created {output_path}")
        print("You can now use this file with curl.")
        
    except Exception as e:
        print(f"Error generating payload: {e}")

if __name__ == "__main__":
    main()
