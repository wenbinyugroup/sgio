"""Gmsh input mapper."""

from __future__ import annotations

from typing import Any, Mapping


def map_input_to_mesh(parsed: Mapping[str, Any]) -> Any:
    """Map parsed Gmsh input payload to the mesh IR object.

    Gmsh is a mesh-first adapter in the current architecture, so the mapper is
    intentionally thin and returns the parsed mesh unchanged.
    """
    return parsed["mesh"]
