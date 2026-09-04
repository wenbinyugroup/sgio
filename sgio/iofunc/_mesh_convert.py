"""Conversion between meshio :class:`Mesh` and sgio :class:`StructureGene`.

These helpers are used by :func:`sgio.iofunc.main.read` for the Gmsh path
(and elsewhere when a raw mesh needs to be wrapped into a SG).
"""
from __future__ import annotations

from typing import Iterable

import numpy as np

from sgio._exceptions import IncompleteModelDataError
from sgio.core import StructureGene
from sgio.core.mesh import CellBlock, SGMesh
from sgio.core.numbering import ensure_node_ids


def parse_model_type(model_type: str | int) -> tuple[int, int]:
    """Parse model-type spec into ``(smdim, submodel)``.

    String form is two-letter prefix + 1-digit suffix:

    * ``'SD'`` → smdim 3 (solid)
    * ``'PL'`` → smdim 2 (plate/shell)
    * ``'BM'`` → smdim 1 (beam)

    The suffix is converted to a 0-based submodel index (``'SD1'`` →
    submodel 0, ``'PL2'`` → submodel 1). Integer form returns
    ``(model_type, model_type)`` unchanged. Unknown input falls back to
    ``(3, 0)``.

    Parameters
    ----------
    model_type : str or int
        Model type specification.

    Returns
    -------
    tuple[int, int]
        ``(smdim, submodel)``.
    """
    if isinstance(model_type, int):
        return model_type, model_type

    if isinstance(model_type, str):
        prefix = model_type.upper()[:2]
        if prefix == 'SD':
            smdim = 3
        elif prefix == 'PL':
            smdim = 2
        elif prefix == 'BM':
            smdim = 1
        else:
            smdim = 3

        try:
            # Suffix '1' maps to submodel 0 (matches solver indexing).
            submodel = int(model_type[2]) - 1
        except (IndexError, ValueError):
            submodel = 0
        return smdim, submodel

    return 3, 0


def mesh_to_sg(
    mesh: SGMesh,
    sgdim: int = 3,
    model_type: str = 'SD1',
    section_names: Iterable[str] | None = None,
    section_ids: Iterable[int] | None = None,
) -> StructureGene:
    """Wrap a mesh into a StructureGene.

    Which elements belong to the structure gene is decided by the section data,
    not by element dimension: an element is an SG element when its physical
    group resolves to one of ``section_names``. Cell blocks whose group does not
    resolve -- an auxiliary ``boundary`` surface group, say -- are dropped, so
    they never reach the element table. Element topological dimension is never
    compared against ``sgdim``; 1D beam elements in a 3D strut lattice are
    legitimate SG elements.

    Parameters
    ----------
    mesh : SGMesh
        The mesh object to convert. Modified in place when cell blocks are
        dropped.
    sgdim : int
        Dimension of the structure gene geometry.
    model_type : str
        Type of the macro structural model.
    section_names : iterable of str, optional
        Names of the sections/materials known from the model data (for the Gmsh
        bundle these come from ``sections.json``). When ``None`` the mesh is
        wrapped without any sections -- the mesh-only path, used when a mesh is
        carried to a mesh writer rather than to a solver.
    section_ids : iterable of int, optional
        Section ids, used to resolve groups whose name is unavailable or does
        not match. Names take precedence, mirroring the bundle's own
        name-then-id matching.

    Returns
    -------
    StructureGene
        The structure gene object.

    Raises
    ------
    IncompleteModelDataError
        If ``section_names`` is given but no element in the mesh resolves to
        any of those sections.
    """
    sg = StructureGene()
    sg.sgdim = sgdim
    sg.smdim, sg.analysis_config.model = parse_model_type(model_type)

    if section_names is None and section_ids is None:
        known_names: set[str] | None = None
        known_ids: set[int] = set()
    else:
        known_names = set(section_names or ())
        known_ids = {int(section_id) for section_id in (section_ids or ())}
        _restrict_mesh_to_sections(mesh, known_names, known_ids)

    sg.mesh = mesh

    _ensure_mesh_data(mesh)
    _process_materials_from_mesh(sg, mesh, known_names, known_ids)

    return sg


def restore_sg_from_mesh_extras(sg: StructureGene, mesh) -> None:
    """Restore SG layer definitions and config from custom mesh attributes.

    Reads ``mesh.sg_layer_defs`` and ``mesh.sg_configs`` (attached by the Gmsh
    reader from ``$SGLayerDef`` / ``$SGConfig`` blocks) and repopulates the
    corresponding StructureGene fields.

    Parameters
    ----------
    sg : StructureGene
        Structure gene object to update.
    mesh : meshio.Mesh
        Mesh object that may carry ``sg_layer_defs`` and ``sg_configs``.
    """
    sg_layer_defs = getattr(mesh, 'sg_layer_defs', {})
    if sg_layer_defs:
        names_by_tag = _build_physical_name_map(mesh)
        # sg_layer_defs: {layer_id: (mat_id, angle)}
        # mocombos:      {property_id: (material_name, angle)}
        for layer_id, (mat_id, angle) in sg_layer_defs.items():
            mat_name = names_by_tag.get(int(mat_id))
            if mat_name is None:
                continue
            sg.mocombos[layer_id] = (mat_name, angle)

    sg_configs = getattr(mesh, 'sg_configs', {})
    if sg_configs:
        if 'sgdim' in sg_configs:
            sg.sgdim = int(sg_configs['sgdim'])
        if 'model' in sg_configs:
            sg.analysis_config.model = int(sg_configs['model'])
        if 'do_damping' in sg_configs:
            sg.analysis_config.do_damping = int(sg_configs['do_damping'])
        if 'thermal' in sg_configs:
            sg.analysis_config.physics = int(sg_configs['thermal'])


def _ensure_mesh_data(mesh: SGMesh) -> None:
    """Ensure required mesh data (node_id, element_id, property_id) exists.

    Parameters
    ----------
    mesh : Mesh
        Mesh object to update.
    """
    ensure_node_ids(mesh)

    if 'element_id' not in mesh.cell_data:
        element_id = []
        elem_idx = 0
        for cell_block in mesh.cells:
            block_ids = list(range(elem_idx + 1, elem_idx + 1 + len(cell_block.data)))
            element_id.append(np.array(block_ids, dtype=int))
            elem_idx += len(cell_block.data)
        mesh.cell_data['element_id'] = element_id

    if 'property_id' not in mesh.cell_data:
        if 'gmsh:physical' in mesh.cell_data:
            mesh.cell_data['property_id'] = [
                np.array(arr, dtype=int) for arr in mesh.cell_data['gmsh:physical']
            ]
        elif 'gmsh:geometrical' in mesh.cell_data:
            mesh.cell_data['property_id'] = [
                np.array(arr, dtype=int) for arr in mesh.cell_data['gmsh:geometrical']
            ]
        else:
            property_id = []
            for cell_block in mesh.cells:
                property_id.append(np.ones(len(cell_block.data), dtype=int))
            mesh.cell_data['property_id'] = property_id


def _resolves_to_section(
    tag: int,
    names_by_tag: dict[int, str],
    section_names: set[str],
    section_ids: set[int],
) -> bool:
    """Return whether one physical tag resolves to a declared section.

    Name matching takes precedence; the id fallback covers meshes whose
    ``$PhysicalNames`` are absent or do not line up with the section records.
    """
    name = names_by_tag.get(tag)
    if name is not None and name in section_names:
        return True
    return tag in section_ids


def _section_material_name(tag: int, names_by_tag: dict[int, str]) -> str:
    """Return the section identity for one physical tag.

    The physical name is the identity token when present; an id-matched group
    with no name gets a positional stand-in, which the bundle then overwrites
    with the material the section record actually names.
    """
    return names_by_tag.get(tag, f'section_{tag}')


def _restrict_mesh_to_sections(
    mesh: SGMesh,
    section_names: set[str],
    section_ids: set[int],
) -> None:
    """Drop cells whose physical group does not resolve to a section.

    Implements the ``element -> entity -> physical tag -> physical name ->
    section`` chain per element, not per cell block: a MSH 2.2 file (and any
    other format that merges same-typed elements from different physical
    groups into one block) can carry a resolving and a non-resolving physical
    group side by side in the same block. Elements whose physical group is
    absent from the section data are auxiliary markers rather than SG
    elements and are removed together with their per-cell data; a block left
    with zero surviving elements is dropped outright.

    Parameters
    ----------
    mesh : SGMesh
        Mesh to restrict, modified in place.
    section_names : set of str
        Names of the sections known from the model data.
    section_ids : set of int
        Section ids, used when a group cannot be matched by name.

    Raises
    ------
    IncompleteModelDataError
        If no element resolves to any declared section.
    """
    names_by_tag = _build_physical_name_map(mesh)
    tag_blocks = mesh.cell_data.get('property_id') or mesh.cell_data.get('gmsh:physical')

    masks: list[np.ndarray] = []
    for index, cell_block in enumerate(mesh.cells):
        n = len(cell_block.data)
        if tag_blocks is None or index >= len(tag_blocks):
            masks.append(np.zeros(n, dtype=bool))
            continue
        tags = np.asarray(tag_blocks[index]).astype(int)
        masks.append(np.array(
            [_resolves_to_section(int(tag), names_by_tag, section_names, section_ids)
             for tag in tags],
            dtype=bool,
        ))

    if not any(mask.any() for mask in masks):
        raise IncompleteModelDataError(
            "No mesh element resolves to a section. "
            f"Section names: {sorted(section_names)}; section ids: {sorted(section_ids)}. "
            f"Mesh physical groups: {_describe_physical_groups(mesh, names_by_tag, tag_blocks)}."
        )

    if all(mask.all() for mask in masks):
        return

    _mask_mesh_cells(mesh, masks)


def _mask_mesh_cells(mesh: SGMesh, masks: list[np.ndarray]) -> None:
    """Keep only the cells selected by ``masks``, one boolean array per block.

    A block whose mask is entirely ``False`` is dropped outright; a block
    that is partially kept has its connectivity and every per-cell data
    container boolean-indexed by its mask.

    ``cell_sets`` is left as-is for every surviving block: its entries are
    per-block local-index arrays (and, for the special
    ``gmsh:bounding_entities`` key, a single geometric-entity reference, not
    an index array at all), so remapping it through a partial mask needs
    per-key semantics this passthrough metadata does not carry, and it is not
    consumed by the SG pipeline.

    Parameters
    ----------
    mesh : SGMesh
        Mesh to mask, modified in place.
    masks : list of numpy.ndarray
        One boolean array per cell block in ``mesh.cells``, True for cells to
        keep.
    """
    kept = [index for index, mask in enumerate(masks) if mask.any()]

    mesh.cells = [
        mesh.cells[index] if masks[index].all() else
        CellBlock(mesh.cells[index].type, mesh.cells[index].data[masks[index]],
                  list(mesh.cells[index].tags))
        for index in kept
    ]
    for container in (mesh.cell_data, mesh.cell_point_data):
        for key, blocks in list(container.items()):
            container[key] = [
                blocks[index] if masks[index].all() else
                np.asarray(blocks[index])[masks[index]]
                for index in kept
            ]
    for key, blocks in list(mesh.cell_sets.items()):
        mesh.cell_sets[key] = [blocks[index] for index in kept]


def _describe_physical_groups(
    mesh: SGMesh,
    names_by_tag: dict[int, str],
    tag_blocks: list | None,
) -> str:
    """Render the mesh's physical groups as ``name (dim D, N elements)`` text.

    Falls back to the bare numeric tag (``'tag 3'``) when the mesh has no
    ``$PhysicalNames`` block, so a caller diagnosing "nothing resolved" still
    gets the actual physical tags present instead of an uninformative
    ``"none"``.
    """
    counts: dict[int, int] = {}
    if tag_blocks is not None:
        for index, cell_block in enumerate(mesh.cells):
            if index >= len(tag_blocks):
                continue
            for tag in tag_blocks[index]:
                counts[int(tag)] = counts.get(int(tag), 0) + 1

    if not names_by_tag and not counts:
        return "none"

    dims_by_tag = {
        int(values[0]): int(values[1]) for values in mesh.field_data.values() if len(values) > 1
    }
    all_tags = sorted(set(names_by_tag) | set(counts))
    return ", ".join(
        f"{names_by_tag.get(tag, f'tag {tag}')!r} (dim {dims_by_tag.get(tag, '?')}, "
        f"{counts.get(tag, 0)} elements)"
        for tag in all_tags
    )


def _process_materials_from_mesh(
    sg: StructureGene,
    mesh: SGMesh,
    section_names: set[str] | None,
    section_ids: set[int],
) -> None:
    """Create one section per resolved physical group.

    No material properties are invented here: the section records the material
    name taken from the physical group, and the caller supplies the material
    models. When ``section_names`` is ``None`` no sections are created at all.

    Parameters
    ----------
    sg : StructureGene
        Structure gene object to update.
    mesh : SGMesh
        Mesh whose physical groups drive the sections.
    section_names : set of str or None
        Names of the sections known from the model data. ``None`` selects the
        mesh-only path, where no sections are created.
    section_ids : set of int
        Section ids, used when a group cannot be matched by name.
    """
    if section_names is None:
        return

    names_by_tag = _build_physical_name_map(mesh)

    property_ids = set()
    for prop_block in mesh.cell_data.get('property_id', []):
        for prop_id in prop_block:
            if prop_id is not None:
                property_ids.add(int(prop_id))

    for prop_id in sorted(property_ids):
        if prop_id in sg.mocombos:
            continue
        if not _resolves_to_section(prop_id, names_by_tag, section_names, section_ids):
            continue
        sg.mocombos[prop_id] = (_section_material_name(prop_id, names_by_tag), 0.0)


def _build_physical_name_map(mesh: SGMesh) -> dict[int, str]:
    """Build a physical-tag to physical-name lookup from mesh field data.

    Deliberately unfiltered by topological dimension: element dimension is not
    what decides section membership.

    Parameters
    ----------
    mesh : SGMesh
        Mesh object containing field-data labels.

    Returns
    -------
    dict[int, str]
        Mapping from physical tag to physical name.
    """
    names_by_tag: dict[int, str] = {}
    for name, values in (getattr(mesh, 'field_data', None) or {}).items():
        names_by_tag[int(values[0])] = name
    return names_by_tag
