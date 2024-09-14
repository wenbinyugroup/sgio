import copy

import numpy as np
from sgio.meshio._mesh import CellBlock, Mesh

from .sg import StructureGene


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

    # Combine materials
    # -----------------
    material_c = copy.deepcopy(sg1.materials)
    mid_map_sg2 = {}  # old: new
    for _mid_old, _m2 in sg2.materials.items():
        _mid_new = 0
        for _mid, _m1 in material_c.items():
            if _m2 == _m1:
                _mid_new = _mid
                break
        if _mid_new == 0:
            _mid_new = len(material_c) + 1
            material_c[_mid_new] = _m2
        mid_map_sg2[_mid_old] = _mid_new

    # for _mid, _m in material_c.items():
    #     print(f'\nmaterial {_mid}')
    #     print(_m)
    # print('\nmid_map_sg2')
    # print(mid_map_sg2)

    # Update SG2 mocombos
    # -------------------
    mocombo_sg2 = {}
    for _id, _combo in sg2.mocombos.items():
        _mid = mid_map_sg2[_combo[0]]
        _ori = _combo[1]
        mocombo_sg2[_id] = [_mid, _ori]
    # print('\nmocombo_sg2')
    # print(mocombo_sg2)

    # Combine mocombos
    # ----------------
    mocombo_c = copy.deepcopy(sg1.mocombos)
    cid_map_sg2 = {}  # old: new
    for _cid_old, _c2 in mocombo_sg2.items():
        _cid_new = 0
        for _cid, _c1 in mocombo_c.items():
            if _c2 == _c1:
                _cid_new = _cid
                break
        if _cid_new == 0:
            _cid_new = len(mocombo_c) + 1
            mocombo_c[_cid_new] = _c2
        cid_map_sg2[_cid_old] = _cid_new

    # print('\nmocombo_c')
    # print(mocombo_c)
    # print('\ncid_map_sg2')
    # print(cid_map_sg2)

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
    # prop_id_c = copy.deepcopy(sg1.mesh.cell_data.get('property_id'))
    prop_id_c = [_data.tolist() for _data in sg1.mesh.cell_data.get('property_id')]
    # prop_sys_c = copy.deepcopy(sg1.mesh.cell_data.get('property_ref_csys'))
    prop_sys_c = [_data.tolist() for _data in sg1.mesh.cell_data.get('property_ref_csys')]


    # Increase the element node id for SG2 and add them to the combined dictionary
    for _i, _cb2 in enumerate(sg2.mesh.cells):

        _pi2 = sg2.mesh.cell_data.get('property_id')[_i]
        _ps2 = sg2.mesh.cell_data.get('property_ref_csys')[_i]

        _cb2.data += sg1_nnode  # Increment the nodal id
        _cbj = -1

        for _j, _cb1 in enumerate(cells_c):
            if _cb2.type == _cb1.type:
                _cbj = _j
                break

        if _cbj == -1:
            cells_c.append(_cb2)
            prop_id_c.append(_pi2)
            prop_sys_c.append(_ps2)
        else:
            cells_c[_cbj].data = np.concatenate((cells_c[_cbj].data, _cb2.data))
            prop_id_c[_cbj].extend(_pi2)
            prop_sys_c[_cbj].extend(_ps2)

    cell_data_c['property_id'] = np.asarray(prop_id_c)
    cell_data_c['property_ref_csys'] = np.asarray(prop_sys_c)


    # Create combined mesh
    # --------------------
    mesh_c = Mesh(
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
