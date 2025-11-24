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

    # Display key insights from Identity
    identity = enriched["identity"]
    print("📊 KEY INSIGHTS")
    print("=" * 50)
    print(f"Primary Sector: {identity['sector']}")
    print(f"Seniority Level: {identity['seniority']}")
    print(f"Years Experience: {identity['years_experience']}")
    print(f"Top Skills: {len(enriched.get('top_skills', []))}")
    print(f"Top Competencies: {len(enriched.get('top_competencies', []))}")
    
    matching = enriched["matching_intelligence"]
    print(f"\n🎯 Primary Ideal Role: {matching['ideal_role']['role_name']}")
    print(f"   Fit Score: {matching['ideal_role']['fit_score']:.2f}")

    # Display TOP SKILLS (optimized)
    print("\n\n⚡ TOP SKILLS (Most Relevant)")
    print("=" * 50)
    if enriched.get("top_skills"):
        domain_skills = [s for s in enriched["top_skills"] if s["type"] == "domain_specific"]
        transversal_skills = [s for s in enriched["top_skills"] if s["type"] == "transversal"]
        
        if domain_skills:
            print("\n🎯 Domain-Specific:")
            for skill in domain_skills[:5]:  # Show top 5
                level_emoji = "⭐" if skill["level"] in ["expert", "advanced"] else "📊"
                print(f"   {level_emoji} {skill['name']} ({skill['level']})")
        
        if transversal_skills:
            print("\n🔄 Transversal:")
            for skill in transversal_skills[:5]:  # Show top 5
                level_emoji = "⭐" if skill["level"] in ["expert", "advanced"] else "📊"
                print(f"   {level_emoji} {skill['name']} ({skill['level']})")

    # Display ideal roles
    print("\n\n🎯 IDEAL ROLES ANALYSIS")
    print("=" * 50)
    print(f"\n🏆 Primary Role: {matching['ideal_role']['role_name']}")
    print(f"   Fit Score: {matching['ideal_role']['fit_score']:.2f}")
    print(f"   Reasoning: {matching['ideal_role']['reasoning']}")
    
    trajectory = enriched["career_trajectory"]
    print(f"\n📈 Career Trajectory: {trajectory['summary']}")
    print(f"🎓 Recent Focus: {trajectory['recent_focus']}")
    
    # Display Education
    education = enriched["education"]
    print("\n\n🎓 EDUCATION")
    print("=" * 50)
    
    if education.get("level_summary"):
        print(f"\n📊 Level: {education['level_summary']}")
    
    if education.get("highest_degree"):
        hd = education["highest_degree"]
        print(f"\n🏆 Highest Degree: {hd.get('degree', 'N/A')}")
        if hd.get('field'):
            print(f"   Field: {hd['field']}")
        if hd.get('institution'):
            print(f"   Institution: {hd['institution']}")
        if hd.get('end_year'):
            print(f"   Year: {hd['end_year']}")
        if hd.get('relevance_to_career'):
            print(f"   Relevance: {hd['relevance_to_career']}")
    
    if education.get("all_education"):
        print(f"\n📚 All Education ({len(education['all_education'])} entries):")
        for edu in education["all_education"][:3]:  # Show first 3
            degree_str = edu.get('degree') or 'N/A'
            field_str = f" - {edu.get('field')}" if edu.get('field') else ""
            completed = "✓" if edu.get('is_completed') else "⏳"
            print(f"   {completed} {degree_str}{field_str}")
    
    if matching.get('alternative_roles'):
        print("\n🔄 Alternative Roles:")
        for i, role in enumerate(matching['alternative_roles'][:3], 1):
            print(f"   {i}. {role['role_name']} (fit: {role['fit_score']:.2f})")
    
    # Display Inferred Context (New)
    context = enriched["inferred_context"]
    print("\n\n🕵️ INFERRED CONTEXT")
    print("=" * 50)
    
    print("\n📜 Credentials:")
    for cred in context['credentials']:
        req = "REQUIRED" if cred['is_required_for_role'] else "Optional"
        print(f"   - {cred['credential_name']} ({cred['type']}) [{req}]")
        
    env = context['work_environment']
    print(f"\n🏢 Work Environment: {env['environment_type']}")
    print(f"   Culture: {', '.join(env['culture_fit_indicators'])}")
    print(f"   Physical: {env['physical_demands']}")

    # Display inferred languages
    languages = enriched["languages"]
    print("\n\n🗣️ INFERRED LANGUAGES")
    print("=" * 50)
    for lang in languages:
        print(f"\n📌 Language: {lang['language']}")
        print(f"   Proficiency: {lang['proficiency']}")
        print(f"   Source: {lang['source']}")
        print(f"   Evidence: {lang['evidence']}")
        print(f"   Confidence: {lang['confidence']:.2f}")

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
