
# Model Compatibility Migration Guide

The `sgio.model` refactor keeps a temporary compatibility layer so existing
projects do not break immediately, but new code should target the typed API.

## Preferred API

- Import `LocationType`, `Model`, and `getModelDim` from `sgio.model.protocols`
- Import `State` and `StateCase` from `sgio.model.state`
- Use `CauchyContinuumModel.set_isotropy()`, `set_elastic()`, and
  `set_strength_constants()` for solid-material updates
- Use direct scalar attributes such as `ea`, `gj`, `ei22`, and `ei33` for named
  beam properties
- Use `get_matrix_component()`, `get_thermal_expansion()`,
  `get_section_matrix()`, `get_section_matrix_component()`, `get_center()`, and
  `get_axis_angle()` for theory-bound quantities
- Use `sgio.iofunc.common.material_json` for material JSON codecs
- Use `sgio.iofunc.common.response_writers` for sectional-response writers

## Legacy To New Mapping

| Legacy API | Preferred replacement |
|---|---|
| `sgio.model.general` | `sgio.model.protocols`, `sgio.model.state`, `sgio.model.response` |
| `SectionResponse` | `State` + `StateCase` + `sgio.iofunc.common.response_writers` |
| `StructureResponseCase` | `StateCase.case` + `StateCase.states` |
| `StructureResponseCases` | `list[StateCase]` |
| `material.get('c11')` | `material.get_matrix_component(...)` |
| `material.get('alpha12')` | `material.get_thermal_expansion(...)` |
| `material.set('isotropy', ...)` | `material.set_isotropy(...)` |
| `material.set('elastic', ...)` | `material.set_elastic(...)` |
| `material.setElastic(...)` | `material.set_elastic(...)` |
| `material.write_to_json(...)` | `sgio.iofunc.common.material_json.write_material_to_json(...)` |
| `read_material_from_json(...)` | `sgio.iofunc.common.material_json.read_material_from_json(...)` |
| `read_materials_from_json(...)` | `sgio.iofunc.common.material_json.read_materials_from_json(...)` |
| `beam.get('stf11')` | `beam.get_section_matrix_component(...)` or direct named attributes |
| `shell.get('stf11gr')` | `shell.get_section_matrix_component(...)` |

## Deprecation Roadmap

The compatibility layer is governed as follows:

| API family | Warning begins | Planned removal |
|---|---:|---:|
| `sgio.model.general` compatibility shell | `0.6` | `0.8` |
| `SectionResponse*` legacy response containers | `0.6` | `0.8` |
| String-based `get()` / `set()` material and section queries | `0.6` | `0.8` |
| Model-level JSON and response-writer wrappers | `0.6` | `0.8` |

New functionality must go into the typed API only. The compatibility layer is
frozen and should not receive new feature work.
