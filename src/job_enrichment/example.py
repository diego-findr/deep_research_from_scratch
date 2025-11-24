"""Example usage of the Job Enrichment System (Optimized v2.0).

This module demonstrates how to use the job enrichment system
to analyze and enrich job postings with the new optimized format.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

try:
    from job_enrichment.enrichment_agent import enrich_job_posting
except ImportError:
    import sys
    sys.path.insert(0, 'src')
    from job_enrichment.enrichment_agent import enrich_job_posting


def load_job_from_file(file_path: str) -> dict:
    """Load a job posting from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing the job posting data.
                  Can be a full path or just a filename (will look in tests/jobs/inputs/)
        
    Returns:
        dict: The job posting data
    """
    path = Path(file_path)
    
    # If it's just a name (no directory), look in tests/jobs/inputs/
    if not path.parent.name and path.suffix != '.json':
        path = Path('tests/jobs/inputs') / f"{file_path}.json"
    elif not path.parent.name:
        path = Path('tests/jobs/inputs') / file_path
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_example(input_file: str = None):
    """Run example job posting enrichment.
    
    Args:
        input_file: Optional path to a JSON file containing job posting data.
                   If not provided, uses the hardcoded example job.
    """
    # Load job from file or use hardcoded example
    if input_file:
        print(f"📂 Loading job posting from: {input_file}\n")
        raw_job = load_job_from_file(input_file)
        job_id = raw_job.get("id", "unknown")
        job_title = raw_job.get("job_title", "Unknown")
    else:
        print("📋 Using hardcoded example job\n")
        # Example job: Technical Support Manager in Construction
        raw_job = {
            "id": "example-001",
            "job_title": "Senior Full-Stack Developer",
            "company_name": "TechCorp",
            "company_description": "Leading software company specializing in cloud solutions",
            "remote": True,
            "remote_amount": 100,
            "description": "We are seeking a senior full-stack developer to join our team and build scalable web applications.",
            "min_salary_range": 70000,
            "max_salary_range": 90000,
            "responsibilities": [
                "Design and develop web applications using React and Node.js",
                "Collaborate with product team to define features",
                "Mentor junior developers",
                "Participate in code reviews",
            ],
            "experience_required": 5,
            "published_date": "2025-11-14",
            "locations": ["Remote"],
            "mandatory_skills": ["React", "Node.js", "TypeScript"],
            "optional_skills": ["AWS", "Docker"],
            "mandatory_languages": ["English"],
            "optional_languages": [],
        }
        job_id = "example-001"
        job_title = raw_job["job_title"]

    metadata = {
        "timestamp": datetime.now().isoformat(),
        "source": "database" if input_file else "example",
    }

    print(f"🔄 Enriching job posting: {job_title}...\n")

    # Enrich the job posting
    enriched = enrich_job_posting(
        raw_job_posting=raw_job,
        job_id=job_id,
        metadata=metadata,
    )

    print("\n✅ Enrichment completed\n")

    # Display key insights from Identity
    identity = enriched["identity"]
    print("📊 KEY INSIGHTS")
    print("=" * 70)
    print(f"Title: {identity['title']}")
    print(f"Company: {identity['company']}")
    print(f"Primary Sector: {identity['sector']}")
    print(f"Required Seniority: {identity['seniority_required']}")
    print(f"Years Experience: {identity['years_experience_required']}")

    # Display REQUIREMENTS (Optimized)
    requirements = enriched["requirements"]
    
    print("\n\n⚡ TOP CRITICAL SKILLS (Curated)")
    print("=" * 70)
    for skill in requirements.get("top_skills", []):
        score_bar = "█" * int(skill['criticality_score'] * 10)
        print(f"   {score_bar} {skill['name']} ({skill['criticality_score']})")
        print(f"      Reasoning: {skill['reasoning']}")

    print("\n\n🚫 NON-NEGOTIABLES (Deal Breakers)")
    print("=" * 70)
    if requirements.get("non_negotiables"):
        for nn in requirements["non_negotiables"]:
            print(f"   ❌ {nn['requirement']} ({nn['type']})")
            print(f"      Verify via: {nn['verification_method']}")
    else:
        print("   No explicit non-negotiables identified.")

    print("\n\n🚩 RED FLAGS")
    print("=" * 70)
    if requirements.get("red_flags"):
        for flag in requirements["red_flags"]:
            severity_icon = "🔴" if flag['severity'] == 'high' else "🟠"
            print(f"   {severity_icon} {flag['flag']} ({flag['severity']})")
    else:
        print("   No specific red flags identified.")

    print("\n\n💀 KILLER QUESTIONS")
    print("=" * 70)
    if requirements.get("killer_questions"):
        for kq in requirements["killer_questions"]:
            print(f"   ❓ {kq['question']}")
            print(f"      Expected: {kq['expected_answer']}")
    else:
        print("   No killer questions generated.")

    # Save enriched job posting
    # Create output directory if it doesn't exist
    output_dir = Path("tests/jobs/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename based on input
    if input_file:
        input_path = Path(input_file)
        output_filename = f"enriched_{input_path.stem}.json"
    else:
        output_filename = "enriched_job_example.json"
    
    output_path = output_dir / output_filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    print(f"\n\n💾 Enriched job posting saved to: {output_path}")

    return enriched


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Enrich a job posting using the Job Enrichment System",
        epilog="Example: python src/job_enrichment/example.py -i acciona_job"
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        help="Name or path to JSON file (e.g., 'acciona_job' will load tests/jobs/inputs/acciona_job.json)"
    )
    
    args = parser.parse_args()
    run_example(input_file=args.input)
