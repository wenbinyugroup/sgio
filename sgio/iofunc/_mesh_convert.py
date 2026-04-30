"""Conversion between meshio :class:`Mesh` and sgio :class:`StructureGene`.

These helpers are used by :func:`sgio.iofunc.main.read` for the Gmsh path
(and elsewhere when a raw mesh needs to be wrapped into a SG).
"""
from __future__ import annotations

import numpy as np
from meshio import Mesh

import sgio.model.solid as smdl
from sgio.core import StructureGene
from sgio.core.numbering import ensure_node_ids


DEFAULT_MATERIAL_PROPERTIES = {
    'elastic': [200e9, 0.3],  # Default steel-like properties
    'isotropy': 0
}


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


def mesh_to_sg(mesh: Mesh, sgdim: int = 3, model_type: str = 'SD1') -> StructureGene:
    """Convert a meshio Mesh object to a StructureGene object.

    Parameters
    ----------
    mesh : meshio.Mesh
        The mesh object to convert.
    sgdim : int
        Dimension of the structure gene geometry.
    model_type : str
        Type of the macro structural model.

    Returns
    -------
    StructureGene
        The structure gene object.
    """
    sg = StructureGene()
    sg.sgdim = sgdim
    sg.smdim, sg.model = parse_model_type(model_type)
    sg.mesh = mesh

    _ensure_mesh_data(mesh)
    _process_materials_from_mesh(sg, mesh, sgdim)

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
        # sg_layer_defs: {layer_id: (mat_id, angle)}
        # mocombos:      {property_id: (material_name, angle)}
        for layer_id, (mat_id, angle) in sg_layer_defs.items():
            mat_name = sg.get_material_name_by_id(mat_id)
            if mat_name is None:
                mat_name = f'Material_{mat_id}'
                sg.add_material_name_id_pair(mat_name, mat_id)
            sg.mocombos[layer_id] = (mat_name, angle)

    sg_configs = getattr(mesh, 'sg_configs', {})
    if sg_configs:
        if 'sgdim' in sg_configs:
            sg.sgdim = int(sg_configs['sgdim'])
        if 'model' in sg_configs:
            sg.model = int(sg_configs['model'])
        if 'do_damping' in sg_configs:
            sg.do_damping = int(sg_configs['do_damping'])
        if 'thermal' in sg_configs:
            sg.physics = int(sg_configs['thermal'])


def _ensure_mesh_data(mesh: Mesh) -> None:
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


def _process_materials_from_mesh(sg: StructureGene, mesh: Mesh, sgdim: int) -> None:
    """Process materials from mesh field_data and cell_data.

    Parameters
    ----------
    sg : StructureGene
        Structure gene object to update.
    mesh : Mesh
        Mesh object containing material information.
    sgdim : int
        Structure gene dimension.
    """
    if hasattr(mesh, 'field_data') and mesh.field_data:
        for name, (phys_id, dim) in mesh.field_data.items():
            if dim == sgdim:
                sg.add_material_name_id_pair(name, phys_id)

    if 'property_id' in mesh.cell_data:
        property_ids = set()
        for prop_block in mesh.cell_data['property_id']:
            for prop_id in prop_block:
                if prop_id is not None:
                    property_ids.add(int(prop_id))

        for prop_id in property_ids:
            if prop_id not in sg.mocombos:
                mat_name = _get_or_create_material_name(sg, prop_id)
                _ensure_material_exists(sg, mat_name)
                sg.mocombos[prop_id] = (mat_name, 0.0)


def _get_or_create_material_name(sg: StructureGene, prop_id: int) -> str:
    """Get material name by property ID or create a default name.

    Parameters
    ----------
    sg : StructureGene
        Structure gene object.
    prop_id : int
        Property ID.

    Returns
    -------
    str
        Material name.
    """
    mat_name = sg.get_material_name_by_id(prop_id)
    if mat_name is None:
        mat_name = f'Material_{prop_id}'
        sg.add_material_name_id_pair(mat_name, prop_id)
    return mat_name


def _ensure_material_exists(sg: StructureGene, mat_name: str) -> None:
    """Ensure material exists in structure gene, create with defaults if needed.

    Parameters
    ----------
    sg : StructureGene
        Structure gene object.
    mat_name : str
        Material name to ensure exists.
    """
    if mat_name not in sg.materials:
        mat = smdl.CauchyContinuumModel(name=mat_name)
        mat.set('isotropy', 0)
        mat.set('elastic', DEFAULT_MATERIAL_PROPERTIES['elastic'])
        sg.materials[mat_name] = mat
