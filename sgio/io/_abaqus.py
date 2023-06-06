import logging
logger = logging.getLogger(__name__)

from sgio.core.sg import StructureGene
import sgio.meshio as smsh
import sgio.model as smdl


# ====================================================================
# Readers
# ====================================================================


# Read input
# ----------

def readInputBuffer(file, **kwargs):
    """
    """
    sg = StructureGene()
    sg.smdim = kwargs['smdim']

    # Read mesh
    sg.mesh, sections, materials = _readMesh(file)
    # sg.use_elem_local_orient = 1

    # Store materials
    mname2id = {}
    for _i, _m in enumerate(materials):
        _name = _m.get('name')
        mname2id[_name] = _i+1

        m = smdl.MaterialSection(_name)

        _mp = _m.get('property')

        m.temperature = _mp.get('temperature', 0)
        m.density = _mp.get('density', 1)

        # Elastic
        _type = _mp.get('type')
        cm = smdl.Cauchy()

        _values = _mp.get('elastic')
        if _type == 'isotropic':
            cm.isotropy = 0
            cm.e1, cm.nu12 = _values
        elif _type == 'engineering_constants':
            cm.isotropy = 1
            cm.e1, cm.e2, cm.e3 = _values[:3]
            cm.g12, cm.g13, cm.g23 = _values[6:]
            cm.nu12, cm.nu13, cm.nu23 = _values[3:6]

        m.constitutive = cm

        sg.materials[_i+1] = m

    print(mname2id)

    # Store sections as material-rotation combinations
    for _i, _section in enumerate(sections):
        _mname = _section.get('material')
        print(_mname)
        _mid = mname2id.get(_mname)
        sg.mocombos[_i+1] = [_mid, 0]

    print(sg.mocombos)

    return sg




def _readMesh(file):
    """
    """

    logger.debug('reading mesh...')

    mesh, sections, materials = smsh.read(file, 'abaqus')
    # print(mesh.cell_sets)
    print(sections)
    print(materials)

    # Organize sections and materials
    mesh.cell_data['property_id'] = []
    for _i, _cb in enumerate(mesh.cells):
        mesh.cell_data['property_id'].append([None,]*len(_cb.data))

    for _prop_id, _section in enumerate(sections):
        _elset = _section['elset']
        for _i, _cb in enumerate(mesh.cell_sets[_elset]):
            for _j in _cb:
                mesh.cell_data['property_id'][_i][_j] = _prop_id+1

    # print(mesh.cell_data['property_id'])

    return mesh, sections, materials
