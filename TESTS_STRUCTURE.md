# Tests Structure - Project Organization

## ✅ Nueva Estructura Implementada

La carpeta `tests/` ha sido reorganizada para separar claramente candidatos de ofertas de trabajo:

```
tests/
├── README.md                       # Documentación general
│
├── candidates/                     # 👥 CANDIDATOS
│   ├── README.md                  # Documentación de candidatos
│   ├── inputs/                    # Perfiles sin enriquecer
│   │   ├── noelia.json
│   │   ├── natalia.json
│   │   └── sergio.json
│   └── outputs/                   # Perfiles enriquecidos
│       ├── enriched_noelia.json
│       ├── enriched_natalia.json
│       └── enriched_sergio.json
│
└── jobs/                          # 💼 OFERTAS DE TRABAJO
    ├── README.md                  # Documentación de ofertas
    ├── inputs/                    # Ofertas sin enriquecer
    │   └── acciona_job.json
    └── outputs/                   # Ofertas enriquecidas
        └── enriched_acciona_job.json
```

## 🎯 Beneficios

### 1. Organización Clara
- Separación lógica entre candidatos y ofertas
- Fácil localización de archivos de test
- Escalable para agregar más ejemplos

### 2. Convención Consistente
- Todos los inputs en carpetas `inputs/`
- Todos los outputs en carpetas `outputs/`
- Nomenclatura clara: `enriched_*.json`

### 3. Documentación Integrada
- README en cada nivel explicando el contenido
- Ejemplos de uso específicos por tipo
- Esquemas de datos documentados

## 🚀 Uso Actualizado

### Enriquecer Candidatos

```bash
# Noelia
python src/profile_enrichment/example.py -i noelia

# Natalia
python src/profile_enrichment/example.py -i natalia

# Sergio
python src/profile_enrichment/example.py -i sergio
```

**Input**: `tests/candidates/inputs/{nombre}.json`  
**Output**: `tests/candidates/outputs/enriched_{nombre}.json`

### Enriquecer Ofertas

```bash
# Acciona
python src/job_enrichment/example.py -i acciona_job
```

**Input**: `tests/jobs/inputs/{nombre}.json`  
**Output**: `tests/jobs/outputs/enriched_{nombre}.json`

## 📝 Agregar Nuevos Tests

### Nuevo Candidato

1. **Crear input**:
   ```bash
   # Crear archivo en tests/candidates/inputs/nuevo_candidato.json
   ```

2. **Ejecutar enriquecimiento**:
   ```bash
   python src/profile_enrichment/example.py -i nuevo_candidato
   ```

3. **Resultado**:
   - Se genera: `tests/candidates/outputs/enriched_nuevo_candidato.json`

### Nueva Oferta

1. **Crear input**:
   ```bash
   # Crear archivo en tests/jobs/inputs/nueva_empresa_job.json
   ```

2. **Ejecutar enriquecimiento**:
   ```bash
   python src/job_enrichment/example.py -i nueva_empresa_job
   ```

3. **Resultado**:
   - Se genera: `tests/jobs/outputs/enriched_nueva_empresa_job.json`

## 🔄 Cambios Realizados

### Scripts Actualizados

1. **`src/profile_enrichment/example.py`**:
   - Ahora busca en `tests/candidates/inputs/`
   - Guarda en `tests/candidates/outputs/`

2. **`src/job_enrichment/example.py`**:
   - Ahora busca en `tests/jobs/inputs/`
   - Guarda en `tests/jobs/outputs/`

### Archivos Movidos

**Candidatos**:
- ✅ `tests/inputs/noelia.json` → `tests/candidates/inputs/noelia.json`
- ✅ `tests/inputs/natalia.json` → `tests/candidates/inputs/natalia.json`
- ✅ `tests/inputs/sergio.json` → `tests/candidates/inputs/sergio.json`
- ✅ `tests/outputs/enriched_*.json` → `tests/candidates/outputs/enriched_*.json`

**Ofertas**:
- ✅ `tests/inputs/acciona_job.json` → `tests/jobs/inputs/acciona_job.json`
- ✅ `tests/outputs/enriched_acciona_job.json` → `tests/jobs/outputs/enriched_acciona_job.json`

### Carpetas Eliminadas

- ❌ `tests/inputs/` (antigua, ahora vacía)
- ❌ `tests/outputs/` (antigua, ahora vacía)

## 📚 Documentación Añadida

- ✅ `tests/README.md` - Overview general
- ✅ `tests/candidates/README.md` - Documentación de candidatos
- ✅ `tests/jobs/README.md` - Documentación de ofertas

## ✨ Resultado Final

- ✅ Estructura clara y organizada
- ✅ Fácil de escalar con nuevos ejemplos
- ✅ Documentación completa
- ✅ Scripts actualizados y funcionando
- ✅ Backward compatibility (rutas relativas funcionales)

## 🎓 Convenciones

### Nombres de Archivos

**Candidatos**:
- Input: `{nombre}.json` (e.g., `noelia.json`)
- Output: `enriched_{nombre}.json` (e.g., `enriched_noelia.json`)

**Ofertas**:
- Input: `{empresa}_job.json` (e.g., `acciona_job.json`)
- Output: `enriched_{empresa}_job.json` (e.g., `enriched_acciona_job.json`)

### Rutas Canónicas

```
tests/candidates/inputs/{nombre}.json           # Candidato raw
tests/candidates/outputs/enriched_{nombre}.json # Candidato enriquecido

tests/jobs/inputs/{empresa}_job.json            # Oferta raw
tests/jobs/outputs/enriched_{empresa}_job.json  # Oferta enriquecida
```

---

**Fecha de reorganización**: 2025-11-17  
**Autor**: Sistema de enriquecimiento automático

