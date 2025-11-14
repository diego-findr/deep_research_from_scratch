"""Example usage of the Profile Enrichment System.

This module demonstrates how to use the profile enrichment system
to analyze and enrich professional profiles.
"""

import json
from datetime import datetime
from profile_enrichment.enrichment_agent import enrich_profile


def run_example():
    """Run example profile enrichment."""
    # Example profile: Industrial Automation Technician
    industrial_profile = {
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
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "source": "linkedin_scraper_v2",
        "sector_objetivo": "industrial|utilities",
    }

    print("🔄 Enriching industrial profile...\n")

    # Enrich the profile
    enriched = enrich_profile(
        raw_profile=industrial_profile,
        candidate_id=candidate_id,
        metadata=metadata,
    )

    print("✅ Enrichment completed\n")

    # Display key insights
    key_insights = enriched["semantic_enrichment"]["key_insights"]
    print("📊 KEY INSIGHTS")
    print("=" * 50)
    print(f"Primary Sector: {key_insights['primary_sector']}")
    print(f"Sector Confidence: {key_insights['sector_confidence']:.2f}")
    print(f"Seniority Level: {key_insights['seniority_level']}")
    print(f"Years Experience: {key_insights['years_experience']}")
    print(f"Total Skills: {key_insights['total_skills_identified']}")
    print(f"Competencies: {key_insights['competencies_count']}")
    print(f"Disambiguated Terms: {key_insights['disambiguated_terms_count']}")

    # Display disambiguation results
    disambiguation_map = enriched["semantic_enrichment"]["disambiguation_map"]
    print("\n\n🔍 DISAMBIGUATION")
    print("=" * 50)
    for term, details in list(disambiguation_map.items())[:3]:
        print(f"\n📌 Term: '{term}'")
        print(f"   Meaning: {details['meaning']}")
        print(f"   Domain: {details['domain']}")
        print(f"   Confidence: {details['confidence']:.2f}")

    # Save enriched profile
    output_path = "enriched_profile_example.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    print(f"\n\n💾 Enriched profile saved to: {output_path}")

    return enriched


if __name__ == "__main__":
    run_example()
