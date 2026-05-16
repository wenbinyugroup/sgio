from __future__ import annotations

"""Deprecation helpers for legacy model compatibility APIs."""

import warnings

MODEL_DEPRECATION_ROADMAP: dict[str, dict[str, str]] = {
    "sgio.model.general": {
        "replacement": "sgio.model.protocols, sgio.model.state, or sgio.model.response",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "SectionResponse": {
        "replacement": "State, StateCase, and sgio.iofunc.common.response_writers",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "StructureResponseCase": {
        "replacement": "StateCase.case and StateCase.states",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "StructureResponseCases": {
        "replacement": "list[StateCase]",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "SectionResponse.writeSGInputGlbU": {
        "replacement": "sgio.iofunc.common.response_writers.write_section_response_displacement",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "SectionResponse.writeSGInputGlbC": {
        "replacement": "sgio.iofunc.common.response_writers.write_section_response_rotation",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "SectionResponse.writeSGInputGlbS": {
        "replacement": "sgio.iofunc.common.response_writers.write_section_response_load",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "CauchyContinuumModel.get": {
        "replacement": "direct attributes, get_matrix_component(), or get_thermal_expansion()",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "CauchyContinuumModel.set": {
        "replacement": "direct attributes, set_isotropy(), set_elastic(), or set_strength_constants()",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "CauchyContinuumModel.setElastic": {
        "replacement": "set_elastic()",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "CauchyContinuumModel.write_to_json": {
        "replacement": "sgio.iofunc.common.material_json.write_material_to_json()",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "read_material_from_json": {
        "replacement": "sgio.iofunc.common.material_json.read_material_from_json()",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "read_materials_from_json": {
        "replacement": "sgio.iofunc.common.material_json.read_materials_from_json()",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "EulerBernoulliBeamModel.get": {
        "replacement": "direct attributes or typed section query methods",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "EulerBernoulliBeamModel.set": {
        "replacement": "direct attributes",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "EulerBernoulliBeamModel.getAll": {
        "replacement": "direct attributes plus typed section query methods",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "TimoshenkoBeamModel.get": {
        "replacement": "direct attributes or typed section query methods",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "TimoshenkoBeamModel.set": {
        "replacement": "direct attributes",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "TimoshenkoBeamModel.getAll": {
        "replacement": "direct attributes plus typed section query methods",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "KirchhoffLovePlateShellModel.get": {
        "replacement": "typed section query methods",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
    "KirchhoffLovePlateShellModel.set": {
        "replacement": "direct attributes",
        "warn_since": "0.6",
        "remove_in": "0.8",
    },
}


def warn_model_deprecation(api_name: str) -> None:
    """Emit a standardized deprecation warning for one legacy API.

    Parameters
    ----------
    api_name : str
        Key in ``MODEL_DEPRECATION_ROADMAP`` describing the deprecated API.
    """

    entry = MODEL_DEPRECATION_ROADMAP.get(api_name, {})
    message = f"`{api_name}` is deprecated"
    remove_in = entry.get("remove_in")
    if remove_in:
        message += f" and will be removed in SGIO {remove_in}"
    message += "."
    replacement = entry.get("replacement")
    if replacement:
        message += f" Use `{replacement}` instead."
    warnings.warn(message, DeprecationWarning, stacklevel=2)
