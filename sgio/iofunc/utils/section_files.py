"""Shared helpers for locating section files and inferring section metadata."""

from __future__ import annotations

from pathlib import Path

from sgio.core import StructureGene

DEFAULT_SECTION_EXTENSIONS = {
    "gmsh": [".msh"],
    "vabs": [".sg", ".dat"],
    "sc": [".sg"],
    "swiftcomp": [".sg"],
    "abaqus": [".inp"],
    "nastran": [".bdf", ".nas"],
}


def get_candidate_extensions(
    file_extension: str | None,
    input_format: str,
) -> list[str]:
    """Return candidate extensions for one input format."""
    if file_extension is not None:
        return [file_extension]
    return DEFAULT_SECTION_EXTENSIONS.get(input_format, [])


def resolve_section_path(
    section_name: str,
    section_dir: str | Path,
    file_extension: str | None,
    input_format: str,
) -> Path:
    """Resolve a section name to a section file."""
    root = Path(section_dir)
    candidates = [root / section_name]

    if not Path(section_name).suffix:
        for extension in get_candidate_extensions(file_extension, input_format):
            candidates.append(root / f"{section_name}{extension}")

    existing = [path for path in candidates if path.exists()]
    if len(existing) == 1:
        return existing[0]
    if len(existing) > 1:
        names = ", ".join(path.name for path in existing)
        raise FileNotFoundError(
            f"Multiple section files match '{section_name}' in {root}: {names}"
        )

    matches: list[Path] = []
    for extension in get_candidate_extensions(file_extension, input_format):
        matches.extend(sorted(root.glob(f"{section_name}*{extension}")))

    unique_matches = list(dict.fromkeys(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    if not unique_matches:
        raise FileNotFoundError(
            f"Section file not found for '{section_name}' in {root}"
        )

    names = ", ".join(path.name for path in unique_matches)
    raise FileNotFoundError(
        f"Multiple section files match '{section_name}' in {root}: {names}"
    )


def infer_section_dimension(sg: StructureGene) -> int:
    """Infer section dimension from a structure gene."""
    if sg.sgdim is not None:
        return int(sg.sgdim)
    if sg.mesh is not None and sg.mesh.cells:
        return int(sg.mesh.cells[0].dim)
    return 2
