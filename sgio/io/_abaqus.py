import logging
logger = logging.getLogger(__name__)

from sgio.core.sg import StructureGene
import sgio.meshio as smsh
import sgio.model as smdl

from sgio.meshio.abaqus._abaqus import get_param_map


# ====================================================================
# Readers
# ====================================================================


# Read input
# ----------

def readInputBuffer(file, **kwargs):
    """
    """
    sg = StructureGene()
    sg.sgdim = kwargs['sgdim']
    sg.smdim = kwargs['smdim']

    # Read mesh
    mesh, sections, materials, mocombos = _readMesh(file)
    # sg.mesh, sections, materials = _readMesh(file)
    # sg.use_elem_local_orient = 1

    sg.mesh = mesh


    # Store materials
    mname2id = {}
    for _i, _m in enumerate(materials):
        _name = _m.get('name')
        mname2id[_name] = _i+1

        # m = smdl.MaterialSection(_name)
        m = smdl.CauchyContinuumModel()
        m.name = _name

        _mp = _m.get('property')

        m.temperature = _mp.get('temperature', 0)
        m.density = _mp.get('density', 1)

        # Elastic
        _type = _mp.get('type')
        m.set('isotropy', _type)
        # cm = smdl.Cauchy()

        _values = _mp.get('elastic')
        if _type == 'isotropic':
            # m.isotropy = 0
            m.e1, m.nu12 = _values
        elif _type == 'engineering_constants':
            # m.isotropy = 1
            m.e1, m.e2, m.e3 = _values[:3]
            m.g12, m.g13, m.g23 = _values[6:]
            m.nu12, m.nu13, m.nu23 = _values[3:6]

        # m.constitutive = cm

        sg.materials[_i+1] = m

    # print(mname2id)

    for _k, _v in mocombos.items():
        _mname, _angle = _v
        _mid = mname2id.get(_mname)
        mocombos[_k] = [_mid, _angle]

    sg.mocombos = mocombos

    # Store sections as material-rotation combinations
    # for _i, _section in enumerate(sections):
    #     _mname = _section.get('material')
    #     _rotation = _section.get('rotation_angle', 0)
    #     # print(_mname)
    #     _mid = mname2id.get(_mname)
    #     sg.mocombos[_i+1] = [_mid, _rotation]

    # print(sg.mocombos)

    return sg




def _readMesh(file):
    """
    """

    logger.debug('reading mesh...')

    mesh, sections, materials = smsh.read(file, 'abaqus', mesh_only=False)
    # print(mesh.cell_sets)
    # print(sections)
    # print(materials)

    # Organize sections and materials
    mesh.cell_data['property_id'] = []
    for _i, _cb in enumerate(mesh.cells):
        mesh.cell_data['property_id'].append([None,]*len(_cb.data))

    # print(sections)

    mocombos = {}
    # _prop_id = 0
    for _i, _section in enumerate(sections):
        _elset = _section['elset']
        _mname = _section['material']
        _angle = _section['rotation_angle']

        _prop_id = None
        for _k, _v in mocombos.items():
            if _v[0] == _mname and _v[1] == _angle:
                _prop_id = _k
                break

        if _prop_id is None:
            _prop_id = len(mocombos) + 1
            mocombos[_prop_id] = [_mname, _angle]

        for _i, _cb in enumerate(mesh.cell_sets[_elset]):
            for _j in _cb:
                mesh.cell_data['property_id'][_i][_j] = _prop_id


    # print(mesh.cell_data['property_id'])

    # return mesh
    return mesh, sections, materials, mocombos




# def _read_material(f):
#     material = {}
#     while True:
#         line = f.readline()
#         if not line:
#             break
#         if line.startswith("**"):
#             continue
#         if line.strip() == "":
#             continue

#         # print(line)
#         keyword = line.partition(",")[0].strip().replace("*", "").upper()

#         if keyword == 'DENSITY':
#             line = f.readline()
#             _density = float(line.strip().strip(',')[0])
#             material['density'] = _density

#         elif keyword == 'ELASTIC':
#             _elastic = []
#             params_map = get_param_map(line)
#             # print(params_map)
#             _type = params_map.get('TYPE', 'ISOTROPIC')
#             if _type == 'ISOTROPIC':
#                 material['type'] = 'isotropic'
#                 line = f.readline()
#                 _elastic += list(map(float, line.split(',')))
#             elif _type == 'ENGINEERING CONSTANTS':
#                 material['type'] = 'engineering_constants'
#                 line = f.readline()
#                 _elastic.append(float(line.strip().strip(',')))
#             material['elastic'] = _elastic
#             break

#     # print(material)

#     return material

