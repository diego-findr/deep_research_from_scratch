"""Example usage of the Profile Enrichment System.

This module demonstrates how to use the profile enrichment system
to analyze and enrich professional profiles.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from profile_enrichment.enrichment_agent import enrich_profile


def load_profile_from_file(file_path: str) -> dict:
    """Load a profile from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing the profile data.
                  Can be a full path or just a filename (will look in tests/candidates/inputs/)
        
    Returns:
        dict: The profile data
    """
    path = Path(file_path)
    
    # If it's just a name (no directory), look in tests/candidates/inputs/
    if not path.parent.name and path.suffix != '.json':
        path = Path('tests/candidates/inputs') / f"{file_path}.json"
    elif not path.parent.name:
        path = Path('tests/candidates/inputs') / file_path
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_example(input_file: str = None):
    """Run example profile enrichment.
    
    Args:
        input_file: Optional path to a JSON file containing profile data.
                   If not provided, uses the hardcoded example profile.
    """
    # Load profile from file or use hardcoded example
    if input_file:
        print(f"📂 Loading profile from: {input_file}\n")
        raw_profile = load_profile_from_file(input_file)
        candidate_id = raw_profile.get("id", "unknown")
        profile_name = raw_profile.get("full_name", "Unknown")
    else:
        print("📋 Using hardcoded example profile\n")
        # Example profile: Industrial Automation Technician
        raw_profile = {
            "id": "uuid-auto2025",
            "full_name": "Luis Hidalgo",
            "heading": "Técnico de automatización y sistemas de control industrial",
            "description": (
                "Especialista en automatización de plantas desalinizadoras mediante SCADA, "
                "PLC (Siemens S7-300/1200), HMI y sistemas de telecontrol de procesos. "
                "Experiencia en integración de sensores y actuadores para optimización energética, "
                "validación de alarmas y control remoto. En proyectos recientes, también colaboré "
                "con equipos de desarrollo en pruebas automáticas con Python y selenium para la "
                "validación de software industrial."
            ),
            "experience_years": 6,
            "skills": [
                {"name": "automatización", "level": "Advanced"},
                {"name": "SCADA", "level": "Advanced"},
                {"name": "PLC", "level": "Advanced"},
                {"name": "Python", "level": "Intermediate"},
                {"name": "pruebas automáticas", "level": "Intermediate"},
                {"name": "telecontrol", "level": "Intermediate"},
            ],
            "experiences": [
                {
                    "role": "Técnico de Automatización",
                    "description": (
                        "Diseño y mantenimiento de sistemas de control PLC y SCADA en plantas "
                        "desalinizadoras, integración de sensores y HMI para supervisión remota."
                    ),
                    "company": "ICR Agua y Energía",
                },
                {
                    "role": "Ingeniero de Validación",
                    "description": (
                        "Colaboración con desarrolladores en automatización de pruebas con "
                        "Python y Selenium sobre entorno SCADA industrial."
                    ),
                    "company": "Tecnología Industrial Avanzada",
                },
            ],
        }
        candidate_id = "ec142b18-befd-4f89-9f3d-98a7b53c3fr2"
        profile_name = raw_profile["full_name"]

    metadata = {
        "timestamp": datetime.now().isoformat(),
        "source": "linkedin_scraper_v2" if not input_file else "database",
        "sector_objetivo": "industrial|utilities",
    }

    print(f"🔄 Enriching profile for: {profile_name}...\n")

    # Enrich the profile
    enriched = enrich_profile(
        raw_profile=raw_profile,
        candidate_id=candidate_id,
        metadata=metadata,
    )

    print("✅ Enrichment completed\n")

    # Display key insights
    # Display key insights
    print("📊 KEY INSIGHTS")
    print("=" * 50)
    
    # Access new structure fields
    filters = enriched.get("inferred_filters", {})
    metrics = enriched.get("pre_computed_metrics", {})
    stability = enriched.get("stability_analysis", {})
    decision = enriched.get("agent_decision_support", {})
    
    print(f"Primary Sector: {filters.get('primary_sector', 'Unknown')}")
    print(f"Total Experience: {metrics.get('total_experience_years', 0)} years")
    print(f"Management Exp: {metrics.get('management_experience_years', 0)} years")
    print(f"Is Manager: {metrics.get('is_manager', False)}")
    print(f"Trajectory: {stability.get('trajectory_trend', 'Unknown')}")
    print(f"Job Hopping Risk: {stability.get('job_hopping_risk', 'Unknown')}")
    
    print(f"\n🎯 Primary Ideal Role: {decision.get('ideal_role_match', ['Unknown'])[0]}")
    print(f"   Seniority Level: {decision.get('seniority_level', 'Unknown')}")

    # Display ideal roles
    print("\n\n🎯 IDEAL ROLES ANALYSIS")
    print("=" * 50)
    ideal_roles = decision.get("ideal_role_match", [])
    if ideal_roles:
        print(f"\n🏆 Primary Role: {ideal_roles[0]}")
        if len(ideal_roles) > 1:
            print("\n🔄 Alternative Roles:")
            for i, role in enumerate(ideal_roles[1:], 1):
                print(f"   {i}. {role}")
    
    # Display competency profile sample
    competencies = enriched.get("competency_profile", {})
    print("\n\n💪 COMPETENCY PROFILE (Sample)")
    print("=" * 50)
    
    hard_skills = competencies.get("technical_hard_skills", [])
    if hard_skills:
        print("\n🔧 Technical Hard Skills (Top 3):")
        for skill in hard_skills[:3]:
            print(f"   - {skill['name']} ({skill['level']})")
            
    soft_skills = competencies.get("soft_skills_and_leadership", [])
    if soft_skills:
        print("\n🧠 Soft Skills (Top 3):")
        for skill in soft_skills[:3]:
            print(f"   - {skill['name']}")

    # Save enriched profile
    # Create output directory if it doesn't exist
    output_dir = Path("tests/candidates/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename based on input
    if input_file:
        input_path = Path(input_file)
        output_filename = f"enriched_{input_path.stem}.json"
    else:
        output_filename = "enriched_profile_example.json"
    
    output_path = output_dir / output_filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    print(f"\n\n💾 Enriched profile saved to: {output_path}")

    return enriched


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Enrich a professional profile using the Profile Enrichment System",
        epilog="Example: python src/profile_enrichment/example.py -i noelia"
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        help="Name or path to JSON file (e.g., 'noelia' will load tests/candidates/inputs/noelia.json)"
    )
    
    args = parser.parse_args()
    run_example(input_file=args.input)
