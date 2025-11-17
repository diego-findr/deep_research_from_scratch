"""
Prompt template for Sector Alignment Agent.
"""

SECTOR_ALIGNMENT_PROMPT = """You are a specialized Sector Alignment Agent evaluating candidate-job compatibility.

**Your task:**
Evaluate the alignment between the candidate's professional sector and the job's sector requirements.

**Candidate Sector Information:**
{candidate_sector_info}

**Job Sector Requirements:**
{job_sector_info}

**Evaluation Steps:**

1. **Primary Sector Match**: Compare the primary sectors directly
   - Are they identical or highly related?
   - Consider sector confidence levels

2. **Secondary Sector Overlap**: Check if secondary sectors provide compatibility
   - Does candidate's secondary sector match job's primary?
   - Is there overlap in secondary sectors?

3. **Transferability Analysis**: Assess if skills transfer between sectors
   - Are the sectors adjacent or complementary?
   - Is there evidence of cross-sector experience?

4. **Red Flags Detection**: Identify critical mismatches
   - Are sectors fundamentally incompatible (e.g., healthcare vs software)?
   - Is there a mismatch that would prevent successful performance?

5. **Scoring**: Calculate 0-100 score based on:
   - Perfect match (same primary): 90-100
   - Strong match (primary-secondary overlap): 75-89
   - Partial match (secondary overlap): 60-74
   - Weak match (transferable but different): 50-59
   - Mismatch: 0-49

**Output format (respond ONLY with valid JSON):**
{{
  "agent": "sector_alignment",
  "score": <0-100>,
  "alignment_level": "<perfect_match|strong_match|partial_match|mismatch>",
  "primary_sector_match": <true|false>,
  "secondary_sector_overlap": [<list of overlapping sectors>],
  "transferability_analysis": "<explanation of skill transferability>",
  "evidence": [
    "<evidence point 1>",
    "<evidence point 2>"
  ],
  "reasoning": "<step-by-step explanation of your evaluation>",
  "red_flags": [<list of red flags or empty array>],
  "confidence": <0.0-1.0>
}}

Think step by step and be precise. Respond ONLY with the JSON object, no additional text.
"""


def format_sector_prompt(candidate: dict, job_offer: dict) -> str:
    """
    Format the sector alignment prompt with candidate and job data.
    
    Args:
        candidate: Candidate profile dict
        job_offer: Job offer dict
        
    Returns:
        Formatted prompt string
    """
    # Extract sector information
    cand_sector = candidate.get("semantic_enrichment", {}).get("sector_inference", {})
    job_sector = job_offer.get("semantic_enrichment", {}).get("sector_inference", {})
    
    candidate_sector_info = f"""
Primary Sector: {cand_sector.get('primary_sector', 'unknown')}
Confidence: {cand_sector.get('confidence', 0.0)}
Secondary Sectors: {', '.join(cand_sector.get('secondary_sectors', [])) or 'none'}
Evidence: {', '.join(cand_sector.get('evidence', [])[:3]) or 'none'}
"""
    
    job_sector_info = f"""
Required Primary Sector: {job_sector.get('primary_sector', 'unknown')}
Confidence: {job_sector.get('confidence', 0.0)}
Secondary Sectors: {', '.join(job_sector.get('secondary_sectors', [])) or 'none'}
Evidence: {', '.join(job_sector.get('evidence', [])[:3]) or 'none'}
"""
    
    return SECTOR_ALIGNMENT_PROMPT.format(
        candidate_sector_info=candidate_sector_info.strip(),
        job_sector_info=job_sector_info.strip()
    )

