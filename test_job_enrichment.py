#!/usr/bin/env python
"""Quick test script for job enrichment."""

import json
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from dotenv import load_dotenv
load_dotenv()

from job_enrichment.enrichment_agent import enrich_job_posting

# Load Acciona job
with open('tests/inputs/acciona_job.json', 'r', encoding='utf-8') as f:
    raw_job = json.load(f)

print("📂 Loaded Acciona job posting")
print(f"🔄 Enriching: {raw_job['job_title']}...\n")

# Enrich
metadata = {
    "timestamp": datetime.now().isoformat(),
    "source": "test",
}

try:
    enriched = enrich_job_posting(
        raw_job_posting=raw_job,
        job_id=raw_job["id"],
        metadata=metadata,
    )
    
    print("\n✅ SUCCESS! Enrichment completed\n")
    
    # Display key insights
    key_insights = enriched["semantic_enrichment"]["key_insights"]
    print("📊 KEY INSIGHTS:")
    print(f"  • Sector: {key_insights['primary_sector']}")
    print(f"  • Seniority: {key_insights['required_seniority']}")
    print(f"  • Years Required: {key_insights['years_experience_required']}")
    print(f"  • Skills: {key_insights['total_skills_identified']}")
    print(f"  • Leadership: {key_insights['leadership_level']}")
    
    # Save
    with open('tests/outputs/enriched_acciona_job.json', 'w', encoding='utf-8') as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: tests/outputs/enriched_acciona_job.json")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

