from __future__ import annotations

"""
Domain taxonomies, ambiguous term heuristics, and static lookup tables used by
the semantic enrichment system.
"""

from typing import Any

AMBIGUOUS_TERMS: dict[str, list[dict[str, Any]]] = {
    "automatización": [
        {
            "concept": "industrial_process_automation",
            "domain": "industrial_automation",
            "keywords": [
                "scada",
                "plc",
                "hmi",
                "telecontrol",
                "siemens",
                "modbus",
                "sensor",
                "actuador",
            ],
            "negative_keywords": ["marketing", "crm"],
            "synonyms": [
                "industrial automation",
                "automatización industrial",
                "automatización de procesos",
            ],
        },
        {
            "concept": "software_test_automation",
            "domain": "software_quality",
            "keywords": ["selenium", "pytest", "qa", "testing", "script"],
            "negative_keywords": ["plc", "scada"],
            "synonyms": [
                "test automation",
                "automatización de pruebas",
                "qa automation",
            ],
        },
    ],
    "java": [
        {
            "concept": "java_programming_language",
            "domain": "software_engineering",
            "keywords": [
                "backend",
                "microservicios",
                "spring",
                "jvm",
                "aplicaciones",
            ],
            "negative_keywords": ["tostado", "grano", "cafetera", "aroma"],
            "synonyms": ["Java", "Java SE", "Java EE"],
        },
        {
            "concept": "coffee_java",
            "domain": "food_beverage",
            "keywords": ["taza", "café", "aroma", "barista"],
            "negative_keywords": ["codigo"],
            "synonyms": ["coffee", "café java"],
        },
    ],
    "python": [
        {
            "concept": "python_programming_language",
            "domain": "software_engineering",
            "keywords": [
                "script",
                "desarrollo",
                "flask",
                "django",
                "automatización",
                "datos",
            ],
            "negative_keywords": ["serpiente", "reptil", "zoológico"],
            "synonyms": ["Python"],
        }
    ],
    "react": [
        {
            "concept": "react_js_framework",
            "domain": "frontend_engineering",
            "keywords": [
                "frontend",
                "componentes",
                "javascript",
                "hooks",
                "next.js",
            ],
            "negative_keywords": ["reaccionar", "respuesta emocional"],
            "synonyms": ["React", "React.js", "ReactJS"],
        }
    ],
    "django": [
        {
            "concept": "django_framework",
            "domain": "software_engineering",
            "keywords": [
                "python",
                "backend",
                "orm",
                "servidor",
                "api",
            ],
            "negative_keywords": ["película", "tarantino"],
            "synonyms": ["Django"],
        }
    ],
    "sap": [
        {
            "concept": "sap_erp",
            "domain": "enterprise_systems",
            "keywords": [
                "erp",
                "abap",
                "finanzas",
                "logística",
                "hana",
                "s/4",
            ],
            "negative_keywords": ["árbol", "resina", "jugo"],
            "synonyms": ["SAP ERP", "SAP S/4HANA"],
        }
    ],
    "odoo": [
        {
            "concept": "odoo_erp",
            "domain": "enterprise_systems",
            "keywords": [
                "erp",
                "modulos",
                "inventario",
                "ventas",
                "crm",
            ],
            "negative_keywords": ["acrónimo"],
            "synonyms": ["Odoo", "OpenERP"],
        }
    ],
}

SECTOR_ONTOLOGY: dict[str, dict[str, Any]] = {
    "industrial_automation": {
        "weight": 1.0,
        "keywords": [
            "plc",
            "siemens",
            "scada",
            "telecontrol",
            "modbus",
            "hmi",
            "actuadores",
            "sensores",
            "desalinizadora",
            "plantas",
        ],
        "subdomains": ["water_treatment", "utilities", "manufacturing"],
    },
    "software_quality": {
        "weight": 0.6,
        "keywords": [
            "selenium",
            "pytest",
            "automatización de pruebas",
            "qa",
            "validación de software",
            "pipeline ci",
        ],
        "subdomains": ["quality_engineering", "devtestops"],
    },
    "enterprise_erp": {
        "weight": 0.5,
        "keywords": ["sap", "odoo", "erp", "abap", "cpq"],
        "subdomains": ["finance", "supply_chain"],
    },
    "software_engineering": {
        "weight": 0.5,
        "keywords": ["api", "microservicios", "backend", "fullstack"],
        "subdomains": ["cloud_native", "product_engineering"],
    },
}

SENIORITY_RULES: list[dict[str, Any]] = [
    {
        "label": "senior",
        "min_years": 8,
        "keywords": ["lider", "estrategia", "arquitectura", "mentoria"],
        "weight": 1.0,
    },
    {
        "label": "mid",
        "min_years": 4,
        "keywords": [
            "implementación",
            "validación",
            "diseño",
            "responsable",
        ],
        "weight": 0.8,
    },
    {
        "label": "junior",
        "min_years": 0,
        "keywords": ["aprendiz", "soporte", "asistente"],
        "weight": 0.5,
    },
]

IMPLICIT_COMPETENCY_PATTERNS: list[dict[str, Any]] = [
    {
        "keywords": ["integración de sensores", "actuadores"],
        "competency": "sensor_actuator_integration",
        "type": "functional",
        "level": "mid",
    },
    {
        "keywords": ["telecontrol", "supervisión remota"],
        "competency": "remote_operations",
        "type": "functional",
        "level": "mid",
    },
    {
        "keywords": ["optimización energética"],
        "competency": "energy_efficiency",
        "type": "functional",
        "level": "mid",
    },
    {
        "keywords": ["selenium", "python", "pruebas"],
        "competency": "python_test_automation",
        "type": "technical",
        "level": "mid",
    },
    {
        "keywords": ["validación de alarmas"],
        "competency": "alarm_management",
        "type": "functional",
        "level": "mid",
    },
    {
        "keywords": ["colaboré con equipos", "equipos de desarrollo"],
        "competency": "cross_functional_collaboration",
        "type": "soft",
        "level": "mid",
    },
    {
        "keywords": ["siemens", "s7-300", "s7-1200"],
        "competency": "siemens_plc_expertise",
        "type": "technical",
        "level": "advanced",
    },
]

SKILL_SYNONYMS: dict[str, list[str]] = {
    "python": ["python", "python3", "scripting python"],
    "selenium": ["selenium", "selenium web driver"],
    "scada": ["scada", "ics scada", "scada industrial"],
    "plc": ["plc", "controladores lógicos programables"],
    "telecontrol": ["telecontrol", "remote control", "remote operation"],
    "automatización": [
        "automatización",
        "automation",
        "automatización industrial",
    ],
}

TAXONOMY_FAMILIES: dict[str, dict[str, Any]] = {
    "industrial_control_stack": {
        "layers": [
            "field_devices",
            "plc_layer",
            "scada_layer",
            "mes_layer",
        ],
        "typical_tools": ["siemens_s7", "wincc", "ignition", "telemetry_rtus"],
    },
    "automation_tooling": {
        "layers": ["scripting", "validation", "monitoring"],
        "typical_tools": ["python", "selenium", "pytest"],
    },
}

