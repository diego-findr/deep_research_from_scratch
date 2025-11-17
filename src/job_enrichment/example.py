"""Example usage of the Job Enrichment System.

This module demonstrates how to use the job enrichment system
to analyze and enrich job postings.
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

    # Display key insights
    key_insights = enriched["semantic_enrichment"]["key_insights"]
    print("📊 KEY INSIGHTS")
    print("=" * 70)
    print(f"Primary Sector: {key_insights['primary_sector']}")
    print(f"Sector Confidence: {key_insights['sector_confidence']:.2f}")
    print(f"Required Seniority: {key_insights['required_seniority']}")
    print(f"Years Experience Required: {key_insights['years_experience_required']}")
    print(f"Total Skills Identified: {key_insights['total_skills_identified']}")
    print(f"Required Competencies: {key_insights['required_competencies_count']}")
    print(f"Leadership Level: {key_insights['leadership_level']}")

    # Display ideal candidate profile
    ideal_candidate = enriched["semantic_enrichment"]["ideal_candidate"]
    print("\n\n🎯 IDEAL CANDIDATE PROFILE")
    print("=" * 70)
    print(f"\n📋 Background: {ideal_candidate['background']}")
    
    print(f"\n✅ Must-Have Experience:")
    for exp in ideal_candidate['must_have_experience']:
        print(f"   • {exp}")
    
    print(f"\n⭐ Preferred Experience:")
    for exp in ideal_candidate['preferred_experience'][:5]:
        print(f"   • {exp}")
    
    print(f"\n📈 Career Trajectory: {ideal_candidate['career_trajectory']}")
    
    print(f"\n🏆 Key Differentiators:")
    for diff in ideal_candidate['key_differentiators']:
        print(f"   • {diff}")

    # Display skills breakdown
    structured_skills = enriched["semantic_enrichment"]["structured_skills"]
    explicit_count = len(structured_skills["explicit"])
    implicit_count = len(structured_skills["implicit"])
    
    print(f"\n\n🛠️  SKILLS ANALYSIS")
    print("=" * 70)
    print(f"Explicit Skills: {explicit_count}")
    print(f"Implicit Skills: {implicit_count}")
    
    print("\n📌 Top Required Skills:")
    all_skills = structured_skills["explicit"] + structured_skills["implicit"]
    required_skills = [s for s in all_skills if s.get("importance") == "required"]
    for skill in required_skills[:8]:
        print(f"   • {skill['name']} ({skill['category']}, {skill['source']})")

    # Display competencies
    competencies = enriched["semantic_enrichment"]["structured_competencies"]
    required_comps = [c for c in competencies if c.get("importance") == "required"]
    
    print(f"\n\n💼 KEY COMPETENCIES")
    print("=" * 70)
    for comp in required_comps[:6]:
        print(f"   • {comp['competency']} ({comp['type']})")

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

