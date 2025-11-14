"""
Prompts for Job Enrichment System.

This module contains all prompts used in the job enrichment workflow.
"""

# ===== CONTEXT ANALYSIS PROMPT =====

JOB_CONTEXT_ANALYSIS_PROMPT = """You are an expert recruiter and talent analyst analyzing job postings.

Your task is to analyze a job posting and extract key contextual indicators that will guide downstream analysis.

<job_posting>
{job_data}
</job_posting>

<task>
Extract and identify:
1. **Key Indicators**: Company info, role level, department, key responsibilities
2. **Domain Signals**: Industry-specific terms, sector indicators, market context
3. **Technology Mentions**: All tools, platforms, technologies mentioned
4. **Responsibility Patterns**: Leadership indicators, technical depth, strategic scope
5. **Company Context**: Company size, industry, culture signals

Focus on signals that will help:
- Identify the sector/industry
- Determine required seniority level
- Extract implicit skill requirements
- Understand the role's scope and impact
</task>

<output_requirements>
Return structured JSON with:
- key_indicators: List of key extracted indicators
- domain_signals: List of domain/sector signals
- technology_mentions: List of all technologies mentioned
- responsibility_patterns: List of responsibility patterns
- company_context: String describing company context
</output_requirements>

Be thorough and extract ALL relevant signals."""


# ===== SECTOR INFERENCE PROMPT =====

JOB_SECTOR_INFERENCE_PROMPT = """You are an industry classification expert analyzing job postings.

Your task is to determine the primary sector/industry for a job posting based on the company, role, and responsibilities.

<job_posting>
{job_data}
</job_posting>

<context_analysis>
{context_analysis}
</context_analysis>

<task>
Determine:
1. Primary sector (e.g., 'construction', 'renewable_energy', 'software_development', 'finance')
2. Secondary/adjacent sectors
3. Confidence score for classification
4. Specific evidence supporting the classification
</task>

<sector_examples>
- construction: Infrastructure, buildings, civil engineering
- renewable_energy: Solar, wind, sustainable energy
- software_development: SaaS, web development, mobile apps
- finance: Banking, fintech, investment
- healthcare: Medical services, pharma, health tech
- manufacturing: Production, industrial processes
- retail: E-commerce, brick-and-mortar retail
- consulting: Professional services, advisory
</sector_examples>

<output_requirements>
Return structured JSON with:
- primary_sector: Main sector classification
- secondary_sectors: List of related sectors
- confidence: Float 0.0-1.0
- evidence: List of specific evidence
- reasoning: Explanation of classification
</output_requirements>

Be specific and evidence-based."""


# ===== SKILLS EXTRACTION PROMPT =====

JOB_SKILLS_EXTRACTION_PROMPT = """You are an expert skills analyst analyzing job postings.

Your task is to extract both explicit and implicit skill requirements from the job posting.

<job_posting>
{job_data}
</job_posting>

<context_analysis>
{context_analysis}
</context_analysis>

<task>
Extract:
1. **Explicit Skills**: Skills directly mentioned in the posting
2. **Implicit Skills**: Skills inferred from responsibilities and context
3. **Skill Clusters**: Related skills grouped by domain

For each skill, determine:
- Category: technical, soft, functional, domain_specific
- Importance: required, preferred, nice_to_have
- Source: explicit or implicit
- Evidence: Where/how this skill is indicated
</task>

<examples>
Example 1 - Construction Technical Support Manager:
Explicit Skills:
- "experiencia en ejecución de obras" → Construction execution (technical, required)
- "carreteras y puentes" → Road and bridge engineering (domain_specific, required)

Implicit Skills:
- "liderar alternativas de proyecto" → Project leadership (soft, required)
- "desarrollar planes de ejecución" → Strategic planning (functional, required)
- "colaborar en la definición del Plan" → Cross-functional collaboration (soft, required)
- "proyectos internacionales" → International project experience (domain_specific, preferred)

Example 2 - Software Developer:
Explicit: Python, React, AWS
Implicit: Problem-solving, debugging, code review, agile methodologies
</examples>

<critical_rules>
1. Don't just copy stated skills - infer implicit requirements
2. Consider what skills are ACTUALLY needed to perform the responsibilities
3. Differentiate between must-haves and nice-to-haves
4. Include soft skills inferred from leadership/collaboration requirements
5. Include domain knowledge requirements
</critical_rules>

<output_requirements>
Return structured JSON with:
- explicit_skills: List of JobSkill objects
- implicit_skills: List of JobSkill objects
- skill_clusters: List of skill groupings

Each JobSkill must have: name, category, importance, source, evidence
</output_requirements>

Be comprehensive and realistic."""


# ===== SENIORITY INFERENCE PROMPT =====

JOB_SENIORITY_INFERENCE_PROMPT = """You are an expert in organizational structure and role leveling.

Your task is to determine the required seniority level for a job posting.

<job_posting>
{job_data}
</job_posting>

<skills_extraction>
{skills_extraction}
</skills_extraction>

<task>
Determine the required seniority level based on:
1. Stated years of experience
2. Role title and level
3. Scope of responsibilities
4. Leadership requirements
5. Technical depth and breadth
6. Strategic vs tactical focus
</task>

<seniority_levels>
JUNIOR (0-2 years):
- Entry-level positions
- Learning and executing defined tasks
- Supervised work
- Limited decision-making authority

MID (2-5 years):
- Independent execution
- Moderate project complexity
- Some mentoring of juniors
- Tactical focus

SENIOR (5-8 years):
- Expert-level execution
- Leading projects/initiatives
- Mentoring others
- Strategic contributions
- High autonomy

LEAD (8-12 years):
- Leading teams or major initiatives
- Setting technical/functional direction
- Significant organizational impact
- Strategic planning
- People management

PRINCIPAL/EXPERT (12+ years):
- Domain expert
- Organizational leadership
- Industry influence
- Executive decision-making
- Strategic vision

EXECUTIVE (15+ years):
- C-level or VP
- Organizational strategy
- P&L responsibility
- Board-level decisions
</seniority_levels>

<indicators>
TITLE INDICATORS:
- "Junior", "Associate" → Junior
- "Engineer", "Analyst", "Specialist" → Mid to Senior
- "Senior", "Lead", "Principal" → Senior to Lead
- "Manager", "Director" → Lead to Executive
- "VP", "Chief", "Head of" → Executive

RESPONSIBILITY INDICATORS:
- "assist", "support", "learn" → Junior
- "develop", "implement", "execute" → Mid
- "lead", "design", "architect" → Senior
- "manage team", "establish direction" → Lead
- "strategic vision", "P&L responsibility" → Executive

EXPERIENCE INDICATORS:
- Years stated in requirements
- Complexity of prior experience needed
- Industry expertise depth
</indicators>

<output_requirements>
Return structured JSON with:
- required_seniority: Level string
- confidence: Float 0.0-1.0
- evidence: List of evidence
- years_experience_required: Integer
- reasoning: Explanation
</output_requirements>

Be realistic and evidence-based."""


# ===== COMPETENCIES ANALYSIS PROMPT =====

JOB_COMPETENCIES_ANALYSIS_PROMPT = """You are an organizational psychologist and competency framework expert.

Your task is to identify the core competencies required for success in this role.

<job_posting>
{job_data}
</job_posting>

<skills_extraction>
{skills_extraction}
</skills_extraction>

<task>
Identify:
1. **Required Competencies**: Core competencies needed (soft skills, managerial, strategic)
2. **Leadership Level**: Individual contributor vs people manager vs executive
3. **Autonomy Level**: How much independence is expected
4. **Collaboration Scope**: Team, cross-functional, organizational, external
</task>

<competency_categories>
SOFT COMPETENCIES:
- Communication, presentation, negotiation
- Problem-solving, critical thinking, analytical skills
- Adaptability, resilience, learning agility
- Attention to detail, organization, time management

FUNCTIONAL COMPETENCIES:
- Project management, process improvement
- Stakeholder management, client relations
- Risk management, compliance
- Budget management, resource allocation

MANAGERIAL COMPETENCIES:
- Team leadership, mentoring, coaching
- Performance management, talent development
- Conflict resolution, decision-making
- Strategic planning, vision setting

STRATEGIC COMPETENCIES:
- Business acumen, market awareness
- Innovation, change management
- Strategic thinking, long-term planning
- Organizational influence, executive presence
</competency_categories>

<output_requirements>
Return structured JSON with:
- required_competencies: List of JobCompetency objects
- leadership_level: String (individual_contributor, team_lead, manager, director, executive)
- autonomy_level: String (supervised, autonomous, independent_leader)
- collaboration_scope: String (team, cross_functional, organizational, external)

Each JobCompetency must have: competency, type, importance, evidence
</output_requirements>

Focus on competencies that truly differentiate success in this role."""


# ===== IDEAL CANDIDATE PROFILE PROMPT =====

JOB_IDEAL_CANDIDATE_PROMPT = """You are an expert executive recruiter creating ideal candidate profiles.

Your task is to define the ideal candidate profile for this job posting, considering the complete analysis.

<job_posting>
{job_data}
</job_posting>

<enrichment_context>
Sector: {sector}
Required Seniority: {seniority}
Years Experience: {years_experience}

Key Skills:
{key_skills}

Key Competencies:
{key_competencies}
</enrichment_context>

<task>
Define the IDEAL candidate by identifying:
1. **Ideal Background**: What professional background would be perfect?
2. **Must-Have Experience**: Non-negotiable experience requirements
3. **Preferred Experience**: Experience that would be a strong plus
4. **Career Trajectory**: Typical path that leads to readiness for this role
5. **Key Differentiators**: What makes a candidate truly exceptional for this role?
6. **Potential Red Flags**: What would indicate a poor fit?
</task>

<examples>
Example - Construction Technical Support Manager:
Ideal Background: 
- 10+ years in construction/infrastructure projects
- Mix of field execution and office-based planning
- Experience with bridges, roads, or similar infrastructure
- Track record of increasing responsibility

Must-Have Experience:
- Actual execution of road/bridge construction projects
- Technical support or engineering role in construction
- Project planning and execution strategy development

Preferred Experience:
- International project experience
- Design-build project exposure
- Subcontractor management
- Large-scale infrastructure projects (>€50M)

Career Trajectory:
- Started as: Site engineer or junior project engineer
- Progressed to: Project engineer → Senior project engineer → Technical lead
- Now ready for: Technical support manager role

Key Differentiators:
- Experience in both design and execution phases
- Track record of solving complex technical challenges
- Ability to work in multicultural/international teams
- Proven ability to develop innovative construction solutions

Potential Red Flags:
- Only theoretical/academic experience without field work
- No experience with infrastructure projects (only buildings)
- Lack of planning/strategy experience (only execution)
- No international exposure for international projects
</examples>

<critical_rules>
1. Be realistic - don't list unicorn requirements
2. Distinguish between must-haves and nice-to-haves
3. Consider career progression - what path leads here?
4. Think about transferable skills from adjacent domains
5. Identify deal-breakers vs growth areas
6. Consider cultural fit based on company description
</critical_rules>

<output_requirements>
Return structured JSON with:
- ideal_background: String description
- must_have_experience: List of strings
- preferred_experience: List of strings
- career_trajectory: String describing typical path
- key_differentiators: List of what makes candidates stand out
- potential_red_flags: List of concerns or mismatches
- reasoning: Overall explanation
</output_requirements>

Be specific and actionable for matching purposes."""


# ===== NORMALIZATION PROMPT =====

JOB_NORMALIZATION_PROMPT = """You are a terminology standardization expert for job matching systems.

Your task is to create normalized synonym maps and canonical term mappings for the job posting.

<job_posting>
{job_data}
</job_posting>

<skills_extraction>
{skills_extraction}
</skills_extraction>

<task>
Create:
1. **Synonym Maps**: Group equivalent terms (e.g., "JS", "JavaScript", "Javascript" → "JavaScript")
2. **Canonical Terms**: Map variations to standard terms
3. **Technology Taxonomy**: Group technologies by category

This enables better matching between job requirements and candidate profiles.
</task>

<examples>
Construction domain:
- "obras" = "construction work" = "construction projects"
- "carreteras" = "roads" = "highways" = "road infrastructure"
- "puentes" = "bridges"

Software domain:
- "React" = "ReactJS" = "React.js"
- "Python" = "python"
- "AWS" = "Amazon Web Services"
</examples>

<output_requirements>
Return structured JSON with:
- normalized_synonyms: List of {{term, synonyms}}
- canonical_terms: List of {{variation, canonical}}
- technology_taxonomy: List of {{category, technologies}}
</output_requirements>

Focus on terms that appear in the job posting."""

