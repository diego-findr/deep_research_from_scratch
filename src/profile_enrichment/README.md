# Profile Enrichment System

Sistema de enriquecimiento semántico y desambiguación de perfiles profesionales sector-agnóstico.

## Descripción

Sistema basado en LangGraph que analiza perfiles profesionales (CVs) y los enriquece con:

- **Desambiguación semántica**: Resuelve términos polisemánticos como "Java" (lenguaje vs café), "automatización" (software vs industrial), "React" (framework vs verbo)
- **Inferencia de sector**: Determina el sector profesional principal con scoring de confianza
- **Extracción de skills**: Identifica habilidades explícitas e implícitas
- **Análisis de competencias**: Detecta soft skills, liderazgo, y capacidades funcionales
- **Normalización**: Crea mapas de sinónimos para mejor matching
- **Inferencia de seniority**: Evalúa el nivel profesional del candidato
- **Explainability**: Proporciona razonamiento y evidencia para cada inferencia

## Problema que Resuelve

findr recibe CVs de cualquier sector y sufre confusión con términos ambiguos:

- **Java**: ¿Lenguaje de programación o café?
- **automatización**: ¿Python/Selenium (software) o SCADA/PLC (industrial)?
- **React**: ¿Framework JavaScript o verbo?
- **Django**: ¿Framework Python o película?
- **SAP**: ¿Sistema ERP o savia de árbol?
- **Odoo**: ¿ERP Python o acrónimo sin sentido?

El sistema utiliza análisis contextual profundo para desambiguar correctamente según el sector profesional del candidato.

## Arquitectura

### Grafo LangGraph

```
START → analyze_context → infer_sector → disambiguate_terms → 
extract_skills → analyze_competencies → normalize_terms → 
infer_seniority → assemble_enriched_profile → END
```

### Nodos del Grafo

1. **analyze_context**: Analiza contexto del perfil extrayendo indicadores clave
2. **infer_sector**: Infiere sector profesional principal con scoring de confianza
3. **disambiguate_terms**: Resuelve términos ambiguos usando contexto sectorial
4. **extract_skills**: Extrae habilidades explícitas e implícitas
5. **analyze_competencies**: Identifica competencias blandas y de liderazgo
6. **normalize_terms**: Crea mapas de sinónimos y términos canónicos
7. **infer_seniority**: Determina nivel de seniority del candidato
8. **assemble_enriched_profile**: Ensambla perfil enriquecido final

## Instalación

```bash
# Instalar dependencias (desde raíz del proyecto)
uv sync

# O con pip
pip install -e .
```

## Uso

### Desde Python

```python
from profile_enrichment.enrichment_agent import enrich_profile

# Perfil de entrada
raw_profile = {
    "id": "uuid-123",
    "full_name": "Luis Hidalgo",
    "heading": "Técnico de automatización y sistemas de control industrial",
    "description": "Especialista en automatización de plantas...",
    "skills": [
        {"name": "automatización", "level": "Advanced"},
        {"name": "SCADA", "level": "Advanced"},
        {"name": "Python", "level": "Intermediate"}
    ],
    "experiences": [...]
}

# Enriquecer perfil
enriched = enrich_profile(
    raw_profile=raw_profile,
    candidate_id="ec142b18-befd-4f89-9f3d-98a7b53c3fr2",
    metadata={"source": "linkedin_scraper_v2"}
)

# Acceder a resultados
print(enriched["semantic_enrichment"]["key_insights"]["primary_sector"])
# Output: "industrial_automation"

print(enriched["semantic_enrichment"]["disambiguation_map"]["automatización"])
# Output: {
#   "meaning": "Industrial process automation using SCADA/PLC systems",
#   "domain": "industrial_control_systems",
#   "confidence": 0.95
# }
```

### Desde Notebook

Ver notebook completo en `notebooks/profile_enrichment/profile_enrichment.ipynb`

```python
from profile_enrichment.enrichment_agent import enrich_profile

enriched_profile = enrich_profile(raw_profile, candidate_id, metadata)
```

## Output Estructura

El perfil enriquecido mantiene los datos originales y añade una sección `semantic_enrichment`:

```json
{
  "candidato_id": "...",
  "timestamp": "...",
  "metadata": {...},
  "perfil_raw": {...},  // Datos originales preservados
  "semantic_enrichment": {
    "version": "1.0",
    "analysis_components": {
      "context_analysis": {...},
      "sector_inference": {...},
      "disambiguation": {...},
      "skills_extraction": {...},
      "competencies_analysis": {...},
      "normalization": {...},
      "seniority_inference": {...}
    },
    "key_insights": {
      "primary_sector": "industrial_automation",
      "sector_confidence": 0.95,
      "seniority_level": "senior",
      "years_experience": 6,
      "total_skills_identified": 18,
      "competencies_count": 12,
      "disambiguated_terms_count": 8
    },
    "structured_skills": {
      "explicit": [...],
      "implicit": [...],
      "clusters": {...}
    },
    "structured_competencies": [...],
    "disambiguation_map": {
      "automatización": {
        "meaning": "Industrial process automation",
        "domain": "industrial_control_systems",
        "confidence": 0.95
      },
      "Python": {
        "meaning": "Python programming language for industrial test automation",
        "domain": "software_testing",
        "confidence": 0.90
      }
    },
    "synonym_map": {...},
    "canonical_terms": {...}
  },
  "explainability": {
    "sector_reasoning": "...",
    "sector_evidence": [...],
    "seniority_reasoning": "...",
    "seniority_evidence": [...],
    "disambiguation_summary": "..."
  }
}
```

## Casos de Uso

### 1. Desambiguación de "automatización"

**Perfil Industrial:**
```json
{
  "heading": "Técnico de automatización industrial",
  "skills": ["SCADA", "PLC", "automatización"],
  "company": "Planta desalinizadora"
}
```
**Output:** `automatización` → "Industrial process automation with SCADA/PLC"

**Perfil Software:**
```json
{
  "heading": "QA Engineer",
  "skills": ["Selenium", "Python", "automatización"],
  "company": "Software startup"
}
```
**Output:** `automatización` → "Test automation for software applications"

### 2. Desambiguación de "Python"

**Perfil Data Science:**
```json
{
  "skills": ["Python", "TensorFlow", "Pandas"],
  "description": "Machine learning con Python..."
}
```
**Output:** `Python` → "Python programming language for data science and ML"

**Perfil Industrial (híbrido):**
```json
{
  "skills": ["SCADA", "PLC", "Python"],
  "description": "Validación de software SCADA con Python..."
}
```
**Output:** `Python` → "Python programming for industrial software validation"

### 3. Extracción de Skills Implícitos

**Input:**
```json
{
  "description": "Lideré un equipo de 5 desarrolladores para crear plataforma ecommerce con React y Node.js"
}
```

**Output:**
```json
{
  "implicit_skills": [
    {
      "name": "team_leadership",
      "category": "soft",
      "level": "advanced",
      "evidence": "Lideré un equipo de 5 desarrolladores",
      "confidence": 0.95
    },
    {
      "name": "fullstack_architecture",
      "category": "technical",
      "level": "advanced",
      "evidence": "plataforma ecommerce con React y Node.js",
      "confidence": 0.90
    }
  ]
}
```

## Características Avanzadas

### Scoring de Confianza

Cada inferencia incluye un score de confianza (0.0-1.0):

- **0.9-1.0**: Alta confianza, indicadores claros
- **0.7-0.9**: Confianza sólida, evidencia fuerte
- **0.5-0.7**: Moderada, señales mixtas
- **< 0.5**: Baja confianza, ambiguo

### Explainability

Cada decisión incluye:
- **Reasoning**: Explicación del razonamiento
- **Evidence**: Citas específicas del perfil
- **Confidence**: Score de confianza

### Normalización

Mapeo de variaciones a términos canónicos:
- `React.js`, `ReactJS`, `React JS` → `React`
- `Node`, `NodeJS`, `Node.js` → `Node.js`
- `Siemens S7-300`, `S7-1200` → `Siemens S7`

## Mejores Prácticas

### Para Mejor Desambiguación

1. **Incluir contexto de empresa**: Tipo de empresa ayuda a inferir sector
2. **Descripciones detalladas**: Más contexto = mejor desambiguación
3. **Mencionar tecnologías complementarias**: Co-ocurrencia ayuda a resolver ambigüedad

### Para Mejor Extracción de Skills

1. **Verbos de acción**: "Lideré", "Diseñé", "Optimicé" revelan skills implícitos
2. **Cuantificación**: "Equipo de 5 personas" ayuda a inferir liderazgo
3. **Duración y complejidad**: Indica nivel de proficiencia

## Modelos LLM Utilizados

- **Claude Sonnet 4**: Razonamiento complejo y análisis semántico
- **GPT-4**: Outputs estructurados con Pydantic

## Testing

```bash
# Ejecutar notebook de pruebas
jupyter notebook notebooks/profile_enrichment/profile_enrichment.ipynb
```

## Limitaciones

- Requiere llamadas a LLM (costo y latencia)
- Calidad depende de la cantidad de contexto en el perfil
- Términos muy oscuros o específicos pueden ser difíciles de desambiguar
- Multilingüe principalmente español/inglés

## Roadmap

- [ ] Caché de análisis para perfiles similares
- [ ] Soporte para más idiomas
- [ ] Base de conocimiento de sectores/taxonomías
- [ ] Integración con bases de datos de empresas
- [ ] API REST para producción
- [ ] Batch processing para múltiples perfiles

## Contribuir

Ver README principal del proyecto para guías de contribución.

## Licencia

Mismo que el proyecto principal.
