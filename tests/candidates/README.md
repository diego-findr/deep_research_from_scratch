# Candidate Profiles - Test Data

Perfiles de candidatos para pruebas del sistema de enriquecimiento.

## 📋 Candidatos Disponibles

### Noelia Antelo
- **Archivo**: `inputs/noelia.json`
- **Rol**: Managed Services - Technical Support Manager
- **Experiencia**: 16 años
- **Sector**: Redes, servicios gestionados, soporte técnico
- **Skills clave**: Liderazgo de equipo, configuración de red, resolución de problemas
- **Compañías**: Makenai Solutions, Indra

### Natalia
- **Archivo**: `inputs/natalia.json`
- **Estado**: Pendiente agregar descripción

### Sergio
- **Archivo**: `inputs/sergio.json`
- **Estado**: Pendiente agregar descripción

## 🚀 Uso

Enriquecer un perfil:
```bash
python src/profile_enrichment/example.py -i noelia
```

## 📊 Output Enriquecido

El output incluye:
- ✅ Análisis de contexto
- ✅ Inferencia de sector
- ✅ Extracción de skills (explícitos e implícitos)
- ✅ Análisis de competencias
- ✅ Inferencia de seniority
- ✅ **Roles ideales** con ponderación por recencia
- ✅ Normalización de términos
- ✅ Explainability completa

Ver ejemplos en `outputs/enriched_*.json`

