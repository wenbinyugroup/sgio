from __future__ import annotations

import copy
import logging

import numpy as np

from sgio.core.mesh import SGMesh
from sgio.core.sg import StructureGene

logger = logging.getLogger(__name__)


def combineSG(sg1:StructureGene, sg2:StructureGene) -> StructureGene:
    """
    """

    # Combine mesh
    # ============

    points_c = []
    cells_c = []  # list[CellBlock(type:str, node_ids:list)]
    point_data_c = {}
    cell_data_c = {}  # dict[name:str, list[data:Iterable]]

    # Combine nodes
    # -------------
    sg1_nnode = sg1.nnodes
    points_c = np.concatenate((
        sg1.mesh.points, sg2.mesh.points
    ))

    # Combine point data
    # ------------------
    for _name, _data in sg1.mesh.point_data.items():
        point_data_c[_name] = np.concatenate((_data, sg2.mesh.point_data[_name]))

    # Combine materials (now name-based)
    # -----------------------------------
    material_c = copy.deepcopy(sg1.materials)
    mat_name_map_sg2 = {}  # old_name: new_name
    
    for _mat_name_old, _m2 in sg2.materials.items():
        # Check if material already exists in combined set
        _mat_name_new = None
        for _mat_name, _m1 in material_c.items():
            if _m2 == _m1:
                _mat_name_new = _mat_name
                break
        
        if _mat_name_new is None:
            # Material not found - add it with its original name
            # If name conflicts, append suffix
            _mat_name_new = _mat_name_old
            if _mat_name_new in material_c:
                suffix = 2
                while f'{_mat_name_old}_{suffix}' in material_c:
                    suffix += 1
                _mat_name_new = f'{_mat_name_old}_{suffix}'
            material_c[_mat_name_new] = _m2
        
        mat_name_map_sg2[_mat_name_old] = _mat_name_new

    # Combine mocombos (now using material names)
    # --------------------------------------------
    mocombo_c = copy.deepcopy(sg1.mocombos)
    cid_map_sg2 = {}  # old_combo_id: new_combo_id
    
    for _cid_old, _combo in sg2.mocombos.items():
        _mat_name_old, _ori = _combo
        # Map to new material name
        _mat_name_new = mat_name_map_sg2[_mat_name_old]
        _combo_new = (_mat_name_new, _ori)
        
        # Check if this combo already exists
        _cid_new = None
        for _cid, _c1 in mocombo_c.items():
            if _combo_new == _c1:
                _cid_new = _cid
                break
        
        if _cid_new is None:
            _cid_new = len(mocombo_c) + 1
            mocombo_c[_cid_new] = _combo_new
        
        cid_map_sg2[_cid_old] = _cid_new

    # Update SG2 property_id
    cid_sg2 = sg2.mesh.cell_data.get('property_id')
    # print('\ncid_sg2')
    # print(cid_sg2)
    for _i in range(len(cid_sg2)):
        for _j in range(len(cid_sg2[_i])):
            cid_sg2[_i][_j] = cid_map_sg2[cid_sg2[_i][_j]]
    # print('\ncid_sg2 (updated)')
    # print(cid_sg2)


    # Combine elements
    # ----------------
    cells_c = copy.deepcopy(sg1.mesh.cells)
    for _name, _data in sg1.mesh.cell_data.items():
        cell_data_c[_name] = [_d.tolist() for _d in _data]
    # prop_id_c = copy.deepcopy(sg1.mesh.cell_data.get('property_id'))
    # prop_id_c = [_data.tolist() for _data in sg1.mesh.cell_data.get('property_id')]
    # prop_sys_c = copy.deepcopy(sg1.mesh.cell_data.get('property_ref_csys'))
    # prop_sys_c = [_data.tolist() for _data in sg1.mesh.cell_data.get('property_ref_csys')]


    # Increase the element node id for SG2 and add them to the combined dictionary
    for _i, _cb2 in enumerate(sg2.mesh.cells):

        # Increment the nodal id
        _cb2.data += sg1_nnode

        # Merge the cell data
        # _pi2 = sg2.mesh.cell_data.get('property_id')[_i].tolist()
        # _ps2 = sg2.mesh.cell_data.get('property_ref_csys')[_i].tolist()

        # Check if the cell block (element type) is already in the combined sg mesh
        _cbj = -1
        for _j, _cb1 in enumerate(cells_c):
            if _cb2.type == _cb1.type:
                _cbj = _j
                break

        # If the cell block is not in the combined sg mesh, add it
        if _cbj == -1:
            cells_c.append(_cb2)
            for _name, _data in sg2.mesh.cell_data.items():
                cell_data_c[_name].append(_data[_i].tolist())
            # prop_id_c.append(_pi2)
            # prop_sys_c.append(_ps2)

        # If the cell block is in the combined sg mesh, concatenate the data
        else:
            cells_c[_cbj].data = np.concatenate((cells_c[_cbj].data, _cb2.data))
            for _name, _data in sg2.mesh.cell_data.items():
                cell_data_c[_name][_cbj].extend(_data[_i].tolist())
            # prop_id_c[_cbj].extend(_pi2)
            # prop_sys_c[_cbj].extend(_ps2)

    # cell_data_c['property_id'] = np.asarray(prop_id_c)
    # cell_data_c['property_ref_csys'] = np.asarray(prop_sys_c)


    # Create combined mesh
    # --------------------
    mesh_c = SGMesh(
        points=points_c,
        cells=cells_c,
        point_data=point_data_c, 
        cell_data=cell_data_c
        )


    # Create combined SG
    # ==================

    sg_c = StructureGene()
    sg_c.mesh = mesh_c
    sg_c.materials = material_c
    sg_c.mocombos = mocombo_c

    return sg_c
