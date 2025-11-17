# Job Postings - Test Data

Ofertas de trabajo para pruebas del sistema de enriquecimiento.

## 📋 Ofertas Disponibles

### Acciona - Gerente de Soporte Técnico (Construcción)
- **Archivo**: `inputs/acciona_job.json`
- **Empresa**: Acciona (Infraestructura sostenible y energía renovable)
- **Rol**: Gerente de Soporte Técnico
- **Sector**: Construcción / Infraestructura vial
- **Experiencia requerida**: 10 años
- **Ubicación**: Madrid, Spain
- **Seniority**: Lead/Manager
- **Responsabilidades clave**:
  - Soporte técnico en proyectos de carreteras y puentes
  - Desarrollo de planes de ejecución
  - Liderazgo de alternativas de proyecto
  - Gestión de subcontratación
  - Proyectos nacionales e internacionales

## 🚀 Uso

Enriquecer una oferta:
```bash
python src/job_enrichment/example.py -i acciona_job
```

## 📊 Output Enriquecido

El output incluye:
- ✅ Análisis de contexto del job posting
- ✅ Inferencia de sector/industria
- ✅ Extracción de skills requeridos (explícitos e implícitos)
- ✅ Inferencia de seniority requerido
- ✅ Análisis de competencias necesarias
- ✅ **Perfil de candidato ideal** (must-haves, preferreds, red flags)
- ✅ Normalización de términos técnicos
- ✅ Explainability completa

### Ejemplo de Perfil Ideal Generado (Acciona)

**Must-Have Experience:**
- 10+ años en ejecución de proyectos de infraestructura vial
- Experiencia en carreteras y puentes
- Desarrollo de planes de ejecución
- Gestión técnica de proyectos

**Preferred Experience:**
- Proyectos internacionales
- Gestión de subcontratación
- Experiencia en design-build
- Grandes proyectos de infraestructura

**Key Differentiators:**
- Capacidad de liderar desde el punto de vista constructivo
- Experiencia mixta campo/oficina
- Habilidad para desarrollar estrategias de ejecución innovadoras
- Trabajo en entornos multiculturales

Ver ejemplo completo en `outputs/enriched_acciona_job.json`

## 📝 Agregar Nueva Oferta

1. Crear archivo JSON en `inputs/`
2. Seguir el esquema del ejemplo
3. Ejecutar enriquecimiento
4. Revisar output en `outputs/`

