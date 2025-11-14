# Job Enrichment System

Sistema de enriquecimiento semántico para ofertas de trabajo (job postings) que extrae información implícita, infiere competencias requeridas y mejora las capacidades de matching.

## 🎯 Objetivo

Enriquecer ofertas de trabajo con análisis semántico profundo para mejorar el matching con candidatos, incluyendo:

- Inferencia de sector/industria
- Extracción de skills explícitos e implícitos
- Inferencia de nivel de seniority requerido
- Análisis de competencias necesarias
- Definición del perfil ideal del candidato
- Normalización de términos técnicos

## 📊 Flujo del Grafo

```
1. analyze_job_context       → Extrae indicadores clave del contexto
2. infer_job_sector           → Determina sector/industria principal
3. extract_job_skills         → Extrae skills explícitos e implícitos
4. infer_job_seniority        → Determina nivel de seniority requerido
5. analyze_job_competencies   → Identifica competencias necesarias
6. define_ideal_candidate     → Define perfil ideal del candidato
7. normalize_job_terms        → Crea mapas de sinónimos
8. assemble_enriched_job      → Construye output final enriquecido
```

## 🚀 Uso

### Básico

```python
from job_enrichment import enrich_job_posting

raw_job = {
    "id": "job-001",
    "job_title": "Gerente de Soporte Técnico",
    "company_name": "Acciona",
    "description": "...",
    "responsibilities": [...],
    "experience_required": 10,
    ...
}

enriched = enrich_job_posting(
    raw_job_posting=raw_job,
    job_id="job-001",
    metadata={"source": "job_board"}
)

# Acceder a insights
print(enriched["semantic_enrichment"]["key_insights"])
print(enriched["semantic_enrichment"]["ideal_candidate"])
```

### Desde línea de comandos

```bash
# Con archivo de entrada
python src/job_enrichment/example.py -i acciona_job

# Con ejemplo por defecto
python src/job_enrichment/example.py
```

## 📁 Estructura de Archivos

```
src/job_enrichment/
├── __init__.py              # Exports principales
├── state.py                 # Definiciones de estado y schemas Pydantic
├── prompts.py               # Prompts para cada nodo del grafo
├── enrichment_agent.py      # Implementación del grafo y agente principal
├── example.py               # Ejemplo de uso
└── README.md                # Esta documentación

tests/
├── inputs/
│   └── acciona_job.json     # Ejemplo de oferta de Acciona
└── outputs/
    └── enriched_acciona_job.json  # Resultado enriquecido
```

## 📋 Output Schema

El output enriquecido incluye:

```json
{
  "job_id": "...",
  "timestamp": "...",
  "raw_job_posting": { ... },
  "semantic_enrichment": {
    "version": "1.0",
    "key_insights": {
      "primary_sector": "construction",
      "required_seniority": "lead",
      "years_experience_required": 10,
      "total_skills_identified": 25,
      "leadership_level": "manager"
    },
    "structured_skills": {
      "explicit": [...],
      "implicit": [...]
    },
    "structured_competencies": [...],
    "ideal_candidate": {
      "background": "...",
      "must_have_experience": [...],
      "preferred_experience": [...],
      "career_trajectory": "...",
      "key_differentiators": [...],
      "potential_red_flags": [...]
    }
  },
  "explainability": {
    "sector_reasoning": "...",
    "seniority_reasoning": "...",
    "ideal_candidate_reasoning": "..."
  }
}
```

## 🔧 Componentes Clave

### 1. Análisis de Contexto
Extrae indicadores clave, señales de dominio, tecnologías mencionadas y patrones en las responsabilidades.

### 2. Inferencia de Sector
Clasifica la oferta en sectores/industrias específicas con score de confianza.

### 3. Extracción de Skills
Identifica tanto skills explícitos (mencionados directamente) como implícitos (inferidos de las responsabilidades).

### 4. Inferencia de Seniority
Determina el nivel de seniority requerido basándose en título, años de experiencia y alcance de responsabilidades.

### 5. Análisis de Competencias
Identifica competencias soft, funcionales, gerenciales y estratégicas requeridas.

### 6. Perfil de Candidato Ideal
Define el perfil ideal del candidato incluyendo:
- Background ideal
- Experiencia must-have vs preferred
- Trayectoria profesional típica
- Diferenciadores clave
- Red flags potenciales

### 7. Normalización
Crea mapas de sinónimos y términos canónicos para mejorar el matching.

## 🎓 Ejemplo: Oferta de Acciona

**Input**: Gerente de Soporte Técnico (Construcción) en Acciona

**Output enriquecido**:
- **Sector**: Construction / Infrastructure
- **Seniority**: Lead/Manager level
- **Skills implícitos**: Project leadership, strategic planning, cross-functional collaboration, international project management
- **Perfil ideal**: 10+ años en construcción de infraestructura vial, experiencia mixta campo/oficina, proyectos internacionales

## 🔄 Integración con Profile Enrichment

Este sistema se complementa con el **Profile Enrichment System** para realizar matching inteligente:

1. **Job Enrichment** → Define qué busca la empresa
2. **Profile Enrichment** → Define qué ofrece el candidato
3. **Matching Engine** → Compara ambos enriquecimientos

Los outputs de ambos sistemas son compatibles y utilizan esquemas similares para facilitar el matching semántico.

## 🧪 Testing

```bash
# Ejecutar con ejemplo de Acciona
python src/job_enrichment/example.py -i acciona_job

# Ver output
cat tests/outputs/enriched_acciona_job.json | jq .semantic_enrichment.key_insights
```

## 📝 Notas

- Usa GPT-4.1 para todos los análisis
- Structured outputs con Pydantic para garantizar consistencia
- Explainability integrada en cada decisión
- Compatible con sistema de matching semántico

