# Tests Directory

Este directorio contiene los datos de entrada y salida para los sistemas de enriquecimiento.

## 📁 Estructura

```
tests/
├── candidates/              # Datos de candidatos
│   ├── inputs/             # Perfiles de candidatos sin enriquecer
│   │   ├── noelia.json
│   │   ├── natalia.json
│   │   └── sergio.json
│   └── outputs/            # Perfiles enriquecidos
│       ├── enriched_noelia.json
│       ├── enriched_natalia.json
│       └── enriched_sergio.json
│
└── jobs/                    # Datos de ofertas de trabajo
    ├── inputs/             # Ofertas sin enriquecer
    │   └── acciona_job.json
    └── outputs/            # Ofertas enriquecidas
        └── enriched_acciona_job.json
```

## 🎯 Uso

### Para Candidatos

**Enriquecer un perfil:**
```bash
python src/profile_enrichment/example.py -i noelia
```

Esto:
- Lee: `tests/candidates/inputs/noelia.json`
- Enriquece el perfil con análisis semántico
- Guarda: `tests/candidates/outputs/enriched_noelia.json`

### Para Ofertas

**Enriquecer una oferta:**
```bash
python src/job_enrichment/example.py -i acciona_job
```

Esto:
- Lee: `tests/jobs/inputs/acciona_job.json`
- Enriquece la oferta con análisis semántico
- Guarda: `tests/jobs/outputs/enriched_acciona_job.json`

## 📝 Agregar Nuevos Datos

### Nuevo Candidato

1. Crear JSON en `tests/candidates/inputs/nombre.json`
2. Ejecutar: `python src/profile_enrichment/example.py -i nombre`
3. Resultado en: `tests/candidates/outputs/enriched_nombre.json`

### Nueva Oferta

1. Crear JSON en `tests/jobs/inputs/nombre_empresa.json`
2. Ejecutar: `python src/job_enrichment/example.py -i nombre_empresa`
3. Resultado en: `tests/jobs/outputs/enriched_nombre_empresa.json`

## 🔍 Esquemas de Datos

### Esquema de Candidato (Input)

```json
{
  "id": "uuid",
  "full_name": "Nombre Completo",
  "heading": "Título profesional",
  "description": "Descripción del perfil",
  "experience_years": 10,
  "skills": [
    {"name": "Skill", "level": "Advanced"}
  ],
  "experiences": [
    {
      "role": "Puesto",
      "description": "Descripción",
      "company": "Empresa",
      "start_date": "2020-01-01",
      "end_date": "2023-12-31"
    }
  ]
}
```

### Esquema de Oferta (Input)

```json
{
  "id": "uuid",
  "job_title": "Título del puesto",
  "company_name": "Nombre de la empresa",
  "company_description": "Descripción de la empresa",
  "description": "Descripción del puesto",
  "responsibilities": ["Responsabilidad 1", "Responsabilidad 2"],
  "experience_required": 10,
  "locations": ["Madrid, Spain"],
  "mandatory_skills": ["Skill 1"],
  "optional_skills": ["Skill 2"]
}
```

## 📊 Ejemplos Actuales

### Candidatos

- **Noelia Antelo**: Technical Support Manager con 16 años de experiencia en redes y servicios gestionados
- **Natalia**: [Agregar descripción]
- **Sergio**: [Agregar descripción]

### Ofertas

- **Acciona**: Gerente de Soporte Técnico en Construcción, sector de infraestructura vial

