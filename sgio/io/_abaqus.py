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
    sg.smdim = kwargs['smdim']

    # Read mesh
    mesh, sections, materials = _readMesh(file)
    # sg.mesh, sections, materials = _readMesh(file)
    # sg.use_elem_local_orient = 1

    sg.mesh = mesh


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

    mesh = smsh.read(file, 'abaqus')
    # print(mesh.cell_sets)
    # print(sections)
    # print(materials)


    # Read materials and sections
    sections = []
    materials = []

    line = file.readline()
    while True:
        if not line:  # EOF
            break

        # Comments
        if line.startswith("**"):
            line = file.readline()
            continue

        keyword = line.partition(",")[0].strip().replace("*", "").upper()

        if keyword.split()[-1] == "SECTION":
            # print(line)
            params_map = get_param_map(line, required_keys=['ELSET', 'MATERIAL'])
            _section = {
                'elset': params_map['ELSET'],
                'material': params_map['MATERIAL']
            }
            try:
                _section['orientation'] = params_map['ORIENTATION']
            except KeyError:
                pass
            line = file.readline()
            line = file.readline()
            sections.append(_section)

        elif keyword == "MATERIAL":
            params_map = get_param_map(line, required_keys=['NAME'])
            _material = _read_material(file)
            materials.append({
                'name': params_map['NAME'],
                'property': _material
            })
            line = file.readline()

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

    # return mesh
    return mesh, sections, materials




def _read_material(f):
    material = {}
    while True:
        line = f.readline()
        if not line:
            break
        if line.startswith("**"):
            continue
        if line.strip() == "":
            continue

        # print(line)
        keyword = line.partition(",")[0].strip().replace("*", "").upper()

        if keyword == 'DENSITY':
            line = f.readline()
            _density = float(line.strip().strip(',')[0])
            material['density'] = _density

        elif keyword == 'ELASTIC':
            _elastic = []
            params_map = get_param_map(line)
            # print(params_map)
            _type = params_map.get('TYPE', 'ISOTROPIC')
            if _type == 'ISOTROPIC':
                material['type'] = 'isotropic'
                line = f.readline()
                _elastic += list(map(float, line.split(',')))
            elif _type == 'ENGINEERING CONSTANTS':
                material['type'] = 'engineering_constants'
                line = f.readline()
                _elastic.append(float(line.strip().strip(',')))
            material['elastic'] = _elastic
            break

    # print(material)

    return material

