# Módulo `catastro_avaluo` — Especificación Técnica

**Fecha:** 2026-03-27  
**Odoo:** 19.0 Community  
**Depende de:** `catastro_predio`  
**Estado:** ✅ Implementado y funcional

---

## Propósito

Gestiona los **avalúos catastrales** de predios urbanos y rurales del municipio de Vallegrande, Bolivia. Cada predio puede tener un avalúo por gestión fiscal. El módulo implementa:

- Cálculo automático de valores (terreno + construcción)
- Flujo de estados con trazabilidad
- Tablas de valores unitarios configurables por zona/uso/gestión
- Recálculo masivo mediante wizard
- Datos demo para desarrollo y testing

---

## Modelos

### `catastro.avaluo`

Avalúo catastral de un predio para una gestión fiscal.

| Campo | Tipo | Descripción |
|---|---|---|
| `name` | Char | Secuencia automática `AVL/YYYY/NNNN` |
| `predio_id` | Many2one → `catastro.predio` | Predio evaluado (required) |
| `gestion` | Integer | Año fiscal (required) |
| `tabla_valor_id` | Many2one → `catastro.tabla.valor` | Tabla de referencia |
| `superficie_terreno` | Float | m² de terreno |
| `superficie_construida` | Float | m² construidos |
| `valor_unitario_terreno` | Float | Bs/m² de terreno (copiado de tabla) |
| `valor_unitario_construccion` | Float | Bs/m² de construcción (copiado de tabla) |
| `factor_estado` | Float | Factor corrector por estado del predio (0.5–1.0) |
| `valor_terreno` | Float | Computed: `sup × VU_terreno` |
| `valor_construccion` | Float | Computed: `sup × VU_construc × factor_estado` |
| `valor_catastral` | Float | Computed: `valor_terreno + valor_construccion` |
| `fecha_calculo` | Date | Fecha del cálculo |
| `observaciones` | Text | Notas del técnico |
| `state` | Selection | `borrador → calculado → aprobado → vigente → historico` |

**Constraint:** `UNIQUE(predio_id, gestion)` — un solo avalúo por predio/gestión.

**Flujo de estados:**
```
borrador → [Calcular] → calculado → [Aprobar] → aprobado → [Publicar] → vigente
vigente → [Nueva gestión] → historico   (automático al publicar el siguiente)
vigente → [Cancelar vigencia] → historico
```

**Método `action_vigente`:** Al publicar un avalúo, marca automáticamente como `historico` cualquier avalúo anterior `vigente` del mismo predio.

---

### `catastro.tabla.valor`

Tabla de valores unitarios por zona, uso de suelo y gestión. Fuente oficial para el cálculo de avalúos.

| Campo | Tipo | Descripción |
|---|---|---|
| `name` | Char | Computed: `Zona / Uso YYYY` |
| `zona` | Char | Zona catastral (ej. "Centro", "Área Rural") |
| `uso_suelo` | Selection | `residencial / comercial / industrial / agrícola / mixto` |
| `tipo_predio` | Selection | `urbano / rural` |
| `gestion` | Integer | Año fiscal |
| `valor_terreno` | Float | Bs/m² terreno |
| `valor_construccion` | Float | Bs/m² construcción |
| `active` | Boolean | Archivado nativo Odoo |
| `notas` | Text | Referencia a resolución municipal |

**Constraint:** `UNIQUE(zona, uso_suelo, tipo_predio, gestion)`

---

### Extensión de `catastro.predio`

Campos y métodos agregados por herencia (`_inherit`):

| Campo | Tipo | Descripción |
|---|---|---|
| `avaluo_ids` | One2many → `catastro.avaluo` | Todos los avalúos del predio |
| `avaluo_vigente_id` | Many2one | Pointer al avalúo en estado `vigente` |
| `valor_catastral` | Float related | Valor del avalúo vigente (read-only) |
| `avaluo_count` | Integer computed | Contador para smart button |

---

### Wizard `catastro.wizard.recalculo.masivo`

Recálculo masivo de avalúos con filtros configurables.

| Campo | Descripción |
|---|---|
| `zona` | Filtrar por zona catastral |
| `tipo_predio` | Filtrar por tipo (`urbano` / `rural` / `todos`) |
| `gestion` | Gestión a generar (año fiscal) |
| `tabla_valor_id` | Tabla de referencia a aplicar |
| `solo_sin_avaluo` | Solo predios sin avalúo existente en esa gestión |

**Lógica por predio del dominio filtrado:**
- Si ya existe avalúo `calculado` → `write()` (actualiza valores con nueva tabla)
- Si no existe → `create()` con estado `borrador`

---

## Estructura de Archivos

```
addons/catastro_avaluo/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── catastro_avaluo.py          # Modelo principal + flujo de estados
│   ├── catastro_tabla_valor.py     # Tabla de valores unitarios
│   └── catastro_predio.py          # Herencia de catastro.predio
├── wizard/
│   ├── __init__.py
│   ├── wizard_recalculo_masivo.py
│   └── wizard_recalculo_masivo_views.xml
├── views/
│   ├── catastro_avaluo_views.xml        # Form/list/kanban de avalúos
│   ├── catastro_tabla_valor_views.xml   # Form/list de tablas de valores
│   ├── catastro_predio_avaluo_views.xml # Smart button en ficha de predio
│   └── menu_views.xml                   # Menú "Avalúos" bajo Catastro
├── data/
│   └── ir_sequence_data.xml     # Secuencia AVL/YYYY/NNNN
├── demo/
│   ├── demo_tabla_valor.xml     # 20 tablas de valores (2024 + 2025, 4 zonas + rural)
│   └── demo_avaluos.xml         # 19 avalúos demo (urbanos + rurales, 2 gestiones)
└── security/
    └── ir.model.access.csv
```

---

## Datos Demo

### `demo_tabla_valor.xml` (20 registros)

| Zona | usos_suelo | Gestiones |
|------|-----------|-----------|
| Centro | residencial, comercial, mixto | 2024, 2025 |
| Norte | residencial, mixto | 2024, 2025 |
| Sur | residencial, comercial | 2024, 2025 |
| Periferia | residencial | 2024, 2025 |
| Área Rural | agrícola, industrial | 2024 |
| Área Rural | agrícola, mixto | 2025 |

### `demo_avaluos.xml` (19 registros)

| Estado | Cantidad | Detalle |
|--------|----------|---------|
| `historico` | 7 | Gestión 2024 (reemplazados por 2025) |
| `vigente` | 11 | Gestión 2025 activos |
| `calculado` | 1 | Pendiente aprobación (`predio_020754001`) |

Cubre predios urbanos en zonificación Centro/Norte/Sur/Periferia y predios rurales con superficies grandes y bajo valor unitario.

---

## Seguridad

| Modelo | Grupo | CRUD |
|---|---|---|
| `catastro.avaluo` | `catastro_predio.group_catastro_user` | R |
| `catastro.avaluo` | `catastro_predio.group_catastro_manager` | CRUD |
| `catastro.tabla.valor` | `catastro_predio.group_catastro_user` | R |
| `catastro.tabla.valor` | `catastro_predio.group_catastro_manager` | CRUD |
| `catastro.wizard.recalculo.masivo` | `catastro_predio.group_catastro_manager` | CRUD |
