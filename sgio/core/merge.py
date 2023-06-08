import copy
import numpy as np
from .sg import StructureGene
from sgio.meshio._mesh import CellBlock


def mergeSG(sg1:StructureGene, sg2:StructureGene) -> StructureGene:
    """
    """

    sg1c = copy.deepcopy(sg1)
    sg2c = copy.deepcopy(sg2)

    sg1_nnode = sg1c.nnodes
    sg1_nelem = sg1c.nelems
    sg1_nmate = sg1c.nmates
    sg1_nma_comb = sg1c.nma_combs

    sg2_mate_id2new = []
    sg2_macomb_id2new = []

    # Combine mesh
    # Nodes
    sg1c.mesh.points = np.concatenate((
        sg1c.mesh.points, sg2c.mesh.points
    ))

    # Elements
    sg1_cell_types = [cb.type for cb in sg1.mesh.cells]
    sg2_cell_types = [cb.type for cb in sg2.mesh.cells]
    print(sg1_cell_types)
    print(sg2_cell_types)
    # Increase the element node id for SG2 and add them to SG1
    for i, sg2type in enumerate(sg2_cell_types):
        _cb = copy.deepcopy(sg2.mesh.cells[i])
        _cb.data += sg1_nnode

        cell_type_found = -1
        for j, sg1type in enumerate(sg1_cell_types):
            if sg2type == sg1type:
                cell_type_found = j
                break

        print(cell_type_found)

        if cell_type_found >= 0:
            sg1.mesh.cells[cell_type_found].data = np.concatenate((
                sg1.mesh.cells[cell_type_found].data,
                _cb.data
            ))
        else:
            sg1.mesh.cells.append(_cb)
            sg1_cell_types.append(sg2type)

    # Merge materials

    return sg1c
