from __future__ import annotations

import logging
import pathlib
from itertools import count

import numpy as np
from meshio import Mesh, CellBlock
from meshio._files import is_buffer, open_file
# from meshio._exceptions import ReadError
from meshio.abaqus._abaqus import (
    abaqus_to_meshio_type,
    get_param_map,
    _read_nodes,
    # _read_cells,
    # _read_set,
    # merge,
    )

# import sgio._global as GLOBAL
# import sgio.iofunc._meshio as smsh
import sgio.model as smdl
# from sgio._global import pprint, pretty_string
from sgio.core.sg import StructureGene
# from sgio.core.mesh import SGMesh
# from sgio.meshio.abaqus._abaqus import get_param_map
from sgio.iofunc._meshio import (
    ReadError,
    num_nodes_per_cell,
)

logger = logging.getLogger(__name__)


abaqus_to_meshio_type.update({
    "WARP2D4": "quad",
    "WARPF2D4": "quad",
    "WARPF2D8": "quad8",
    "WARP2D3": "triangle",
    "WARPF2D3": "triangle",
    "WARPF2D6": "triangle6",
})
meshio_to_abaqus_type = {v: k for k, v in abaqus_to_meshio_type.items()}



# ====================================================================
# Readers
# ====================================================================


# Read input
# ----------

def read(filename, **kwargs):
    """Reads a Abaqus inp file."""
    if is_buffer(filename, 'r'):
        out = read_buffer(filename, **kwargs)
    else:
        with open_file(filename, "r") as f:
            out = read_buffer(f, **kwargs)
    return out



def read_buffer(file, **kwargs):
    """
    """
    sg = StructureGene()
    sg.sgdim = kwargs['sgdim']

    model = kwargs.get('model')
    if isinstance(model, int):
        smdim = kwargs.get('model')
        _submodel = model
    elif isinstance(model, str):
        if model.upper()[:2] == 'SD':
            smdim = 3
        elif model.upper()[:2] == 'PL':
            smdim = 2
        elif model.upper()[:2] == 'BM':
            smdim = 1
        _submodel = int(model[2]) - 1

    sg.smdim = smdim
    sg.model = _submodel

    # Read mesh
    mesh, sections, materials, mocombos = _readMesh(file)

    sg.mesh = mesh

    # Store materials
    mname2id = {}
    for _i, _m in enumerate(materials):
        _name = _m.get('name')
        mname2id[_name] = _i+1

        m = smdl.CauchyContinuumModel(_name)
        # m.name = _name

        _mp = _m.get('property')

        m.temperature = _mp.get('temperature', 0)

        # _prop = smdl.CauchyContinuumProperty()
        _density = _mp.get('density', 1)
        m.set('density', _density)

        # Elastic
        _type = _mp.get('type')
        # _prop.isotropy = _type

        _values = _mp.get('elastic')
        if _type == 'isotropic':
            m.set('isotropy', 0)
            m.set('elastic', _values)
        elif _type == 'engineering_constants':
            m.set('isotropy', 1)
            _e1, _e2, _e3 = _values[:3]
            _g12, _g13, _g23 = _values[6:9]
            _nu12, _nu13, _nu23 = _values[3:6]
            m.set(
                'elastic',
                [_e1, _e2, _e3, _g12, _g13, _g23, _nu12, _nu13, _nu23],
                input_type='engineering')

        sg.materials[_i+1] = m

    # print(mname2id)
    # print(sg.materials)

    for _k, _v in mocombos.items():
        _mname, _angle = _v
        _mid = mname2id.get(_mname)
        mocombos[_k] = [_mid, _angle]

    sg.mocombos = mocombos

    return sg




def _readMesh(file):
    """
    """

    logger.debug('reading mesh...')

    # mesh, sections, materials = smsh.read_sgmesh_buffer(file, 'abaqus', mesh_only=False)
    mesh, sections, materials = read_mesh_buffer(file, mesh_only=False)

    logger.debug('mesh.cell_sets:')
    logger.debug(mesh.cell_sets)
    logger.debug('sections:')
    logger.debug(sections)
    logger.debug('materials:')
    logger.debug(materials)

    # Organize sections and materials

    # Initialize the property_id array
    # with the same shape as the cells
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

        _prop_id = None  # the property id (material-angle pair)

        # check if the material-angle pair already exists
        for _k, _v in mocombos.items():
            if _v[0] == _mname and _v[1] == _angle:
                _prop_id = _k
                break

        if _prop_id is None:
            # new material-angle pair
            _prop_id = len(mocombos) + 1
            mocombos[_prop_id] = [_mname, _angle]

        for _i, _cb in enumerate(mesh.cell_sets[_elset]):
            for _j in _cb:
                mesh.cell_data['property_id'][_i][_j] = _prop_id


    # print(mesh.cell_data['property_id'])

    # return mesh
    return mesh, sections, materials, mocombos




def read_mesh_buffer(f, mesh_only:bool=True):
    # Initialize the optional data fields
    points = []
    cells = []
    cell_ids = []  # Map the real element id to the CellBlock index and row index
    point_sets = {}
    cell_sets = {}
    cell_sets_element = {}  # Handle cell sets defined in ELEMENT
    cell_sets_element_order = []  # Order of keys is not preserved in Python 3.5
    field_data = {}
    cell_data = {}
    point_data = {}
    point_ids = None

    in_part = False  # s.t.
    in_instance = False  # s.t.
    in_assembly = False  # s.t.
    in_step = False  # s.t.

    sections = []
    materials = []

    line = f.readline()
    while True:
        if not line:  # EOF
            break

        # Comments
        if line.startswith("**"):
            line = f.readline()
            continue

        keyword = line.partition(",")[0].strip().replace("*", "").upper()

        in_part = True if keyword == 'PART' else (False if keyword == 'END PART' else in_part)
        in_instance = True if keyword == 'INSTANCE' else (False if keyword == 'END INSTANCE' else in_instance)
        in_assembly = True if keyword == 'ASSEMBLY' else (False if keyword == 'END ASSEMBLY' else in_assembly)
        in_step = True if keyword == 'STEP' else (False if keyword == 'END STEP' else in_step)


        if keyword == "NODE" and in_part:
            points, point_ids, line = _read_nodes(f)

        elif keyword == "ELEMENT":
            if point_ids is None:
                raise ReadError("Expected NODE before ELEMENT")
            params_map = get_param_map(line, required_keys=["TYPE"])
            cell_type, cells_data, ids, sets, line = _read_cells(
                f, params_map, point_ids
            )

            # logger.info('cell_type:')
            # logger.info(cell_type)
            # logger.info('cells_data:')
            # logger.info(cells_data)
            # logger.info('ids:')
            # logger.info(ids)
            logger.debug('sets:')
            logger.debug(sets)

            # Check if the cell type is already in the cells list
            cbi = None
            cb = None  # [cell_type, cells_data]
            for _i, _cb in enumerate(cells):
                if _cb[0] == cell_type:
                    cbi = _i
                    cb = _cb
                    break

            if cbi is None:
                # new type
                # cb = CellBlock(cell_type, cells_data)
                cells.append([cell_type, cells_data])
                cell_ids.append(ids)
            else:
                # existing type
                cells[cbi][1] = np.concatenate([cells[cbi][1], cells_data])
                # update cell_ids
                _n = len(cell_ids[cbi])
                for _eid, _cid in ids.items():
                    cell_ids[cbi][_eid] = _n + _cid
                # cell_ids[cbi].update(ids)

            # cells.append(CellBlock(cell_type, cells_data))

            # cell_ids.append(ids)
            # print('\ncell_ids:')
            # print(cell_ids)
            # if sets:
            for _set_name, _set_eids in sets.items():
                # _set_name = list(sets.keys())[0]
                try:
                    cell_sets_element[_set_name] = np.concatenate([cell_sets_element[_set_name], _set_eids])
                    # get the index of the set name in the cell_sets_element keys
                    # _i = list(cell_sets_element.keys()).index(_set_name)
                except KeyError:
                    # cell_sets_element.update(sets)
                    cell_sets_element[_set_name] = _set_eids
                    cell_sets_element_order += [_set_name,]
            # print('\ncell_sets_element:')
            # print(cell_sets_element)

            # if not 'element_id' in cell_data.keys():
            #     cell_data['element_id'] = []
            # _element_id = [0,]*len(ids)
            # for _eid, _cid in ids.items():
            #     _element_id[_cid] = _eid
            # # print(_element_id)
            # cell_data['element_id'].append(_element_id)

        elif keyword == "NSET":
            params_map = get_param_map(line, required_keys=["NSET"])
            set_ids, _, line = _read_set(f, params_map)
            name = params_map["NSET"]
            point_sets[name] = np.array(
                [point_ids[point_id] for point_id in set_ids], dtype="int32"
            )

        elif keyword == "ELSET":
            params_map = get_param_map(line, required_keys=["ELSET"])
            set_ids, set_names, line = _read_set(f, params_map)
            name = params_map["ELSET"]
            cell_sets[name] = []
            if set_ids.size:
                for cell_ids_ in cell_ids:
                    cell_sets_ = np.array(
                        [
                            cell_ids_[set_id]
                            for set_id in set_ids
                            if set_id in cell_ids_
                        ],
                        dtype="int32",
                    )
                    cell_sets[name].append(cell_sets_)
            elif set_names:
                for set_name in set_names:
                    if set_name in cell_sets.keys():
                        cell_sets[name].append(cell_sets[set_name])
                    elif set_name in cell_sets_element.keys():
                        cell_sets[name].append(cell_sets_element[set_name])
                    else:
                        raise ReadError(f"Unknown cell set '{set_name}'")

        elif keyword == "DISTRIBUTION":
            _default = [1, 0, 0, 0, 1, 0, 0, 0, 0]
            if not 'property_ref_csys' in cell_data.keys():
                # Initialize the property_ref_csys array
                # cell_data['property_ref_csys'] and cell_ids should have the same shape
                cell_data['property_ref_csys'] = []
                for _i in range(len(cell_ids)):
                    cell_data['property_ref_csys'].append([_default,]*len(cell_ids[_i]))

            # logger.info('shape of cell_ids:')
            # logger.info('block index, number of elements')
            # for _i, _cb in enumerate(cell_ids):
            #     logger.info(f'{_i}, {len(_cb)}')

            # logger.info('shape of cell_data["property_ref_csys"]:')
            # logger.info('block index, number of elements')
            # for _i, _cb in enumerate(cell_data['property_ref_csys']):
            #     logger.info(f'{_i}, {len(_cb)}')

            # logger.info('cell_ids:')
            # logger.info(cell_ids)

            params_map = get_param_map(line)
            # print(params_map)
            # print(cell_ids)
            _dict_cell_data, line = _read_distribution(f, params_map)
            # _name = params_map['NAME']

            for _eid, _edata in _dict_cell_data.items():
                for _i, _block in enumerate(cell_ids):
                    try:
                        _j = _block[_eid]
                        break
                    except KeyError:
                        continue

                # logger.info(f'_i: {_i}, _j: {_j}')

                cell_data['property_ref_csys'][_i][_j] = _edata

        elif keyword.split()[-1] == "SECTION":
            """
            Keys in each section:
              - elset: required
              - material: required
              - orientation: optional
              - rotation_angle: optional
            """
            params_map = get_param_map(line, required_keys=['ELSET', ])
            _section = {
                'elset': params_map['ELSET'],
            }

            try:
                _section['orientation'] = params_map['ORIENTATION']
            except KeyError:
                pass

            if 'MATERIAL' in params_map.keys():
                # Homogeneous section
                _section['material'] = params_map['MATERIAL']
                _section['rotation_angle'] = 0
                line = f.readline()

            elif 'COMPOSITE' in params_map.keys():
                # Composite section
                line = f.readline()
                line = line.split(',')
                _material_name = line[2].strip()
                _section['material'] = _material_name
                _rotation = float(line[3].strip())
                _section['rotation_angle'] = _rotation

            sections.append(_section)
            line = f.readline()

        elif keyword == "MATERIAL":
            params_map = get_param_map(line, required_keys=['NAME'])
            _material = _read_material(f)
            materials.append({
                'name': params_map['NAME'],
                'property': _material
            })
            line = f.readline()

        elif keyword == "INCLUDE":
            # Splitting line to get external input file path (example: *INCLUDE,INPUT=wInclude_bulk.inp)
            ext_input_file = pathlib.Path(line.split("=")[-1].strip())
            if ext_input_file.exists() is False:
                cd = pathlib.Path(f.name).parent
                ext_input_file = cd / ext_input_file

            # Read contents from external input file into mesh object
            try:
                out = read(ext_input_file)
            except FileNotFoundError:
                print(f'warning: include file ({ext_input_file}) not found.')
                line = f.readline()
                continue

            # Merge contents of external file only if it is containing mesh data
            if len(out.points) > 0:
                points, cells = merge(
                    out,
                    points,
                    cells,
                    point_data,
                    cell_data,
                    field_data,
                    point_sets,
                    cell_sets,
                )

            line = f.readline()
        else:
            # There are just too many Abaqus keywords to explicitly skip them.
            line = f.readline()

    logger.debug('cells:')
    for _cb in cells:
        logger.debug(f'{_cb[0]}:')
        logger.debug(_cb[1])

    logger.debug('cell_ids:')
    logger.debug(cell_ids)

    cell_data['element_id'] = []
    for _cb in cell_ids:
        _element_id = [0,]*len(_cb)
        for _eid, _cid in _cb.items():
            _element_id[_cid] = _eid
        cell_data['element_id'].append(_element_id)
    logger.debug('cell_data["element_id"]:')
    logger.debug(cell_data['element_id'])

    logger.debug('cell_sets_element_order:')
    logger.debug(cell_sets_element_order)
    logger.debug('cell_sets_element:')
    logger.debug(cell_sets_element)

    # Parse cell sets defined in ELEMENT
    # for i, name in enumerate(cell_sets_element_order):
    #     # Not sure whether this case would ever happen
    #     if name in cell_sets.keys():
    #         cell_sets[name][i] = cell_sets_element[name]
    #     else:
    #         cell_sets[name] = []
    #         for ic in range(len(cells)):
    #             cell_sets[name].append(
    #                 cell_sets_element[name] if i == ic else np.array([], dtype="int32")
    #             )
    for _set_name, _set_elements in cell_sets_element.items():
        cell_sets[_set_name] = [[] for _i in range(len(cells))]
        for _eid in _set_elements:
            # get the cell block index and cell index
            for _cbi, _cb in enumerate(cell_ids):
                try:
                    _ci = _cb[_eid]
                    cell_sets[_set_name][_cbi].append(_ci)
                    break
                except KeyError:
                    continue

    logger.debug('cell_sets:')
    logger.debug(cell_sets)

    # for _key in cell_data.keys():
    #     print(f'\n\ncell_data["{_key}"]:')
    #     print(cell_data[_key][0])
    #     cell_data[_key] = np.asarray(cell_data[_key])
    # print(cell_data)

    for _i in range(len(cells)):
        cells[_i] = tuple(cells[_i])

    mesh = Mesh(
        points,
        cells,
        point_data=point_data,
        cell_data=cell_data,
        field_data=field_data,
        point_sets=point_sets,
        cell_sets=cell_sets,
    )

    if mesh_only:
        return mesh
    else:
        return mesh, sections, materials




def _read_cells(f, params_map, point_ids):
    """
    Read cell (element) data from an Abaqus input file.

    Parameters
    ----------
    f : file object
        File object to read from
    params_map : dict
        Dictionary containing element parameters including TYPE and ELSET
    point_ids : dict
        Dictionary mapping node IDs to their indices

    Returns
    -------
    tuple
        A tuple containing:
        - cell_type : str
            The meshio cell type
        - cells : numpy.ndarray
            Array of cell connectivity data
        - cell_ids : dict
            Dictionary mapping element IDs to their indices
        - cell_sets : dict
            Dictionary of element sets
        - line : str
            The last line read from the file

    Raises
    ------
    ReadError
        If the element type is not available or if the number of data items
        does not match the expected count for the element type
    """
    # Get element type from parameters and verify it's supported
    etype = params_map["TYPE"]
    if etype not in abaqus_to_meshio_type.keys():
        raise ReadError(f"Element type not available: {etype}")

    # Convert Abaqus element type to meshio cell type
    cell_type = abaqus_to_meshio_type[etype]
    # Calculate number of data items per element (element ID + node IDs)
    num_data = num_nodes_per_cell[cell_type] + 1

    # Read element data line by line until a new section starts
    idx = []
    while True:
        line = f.readline()
        if not line or line.startswith("*"):
            break
        line = line.strip()
        if line == "":
            continue
        # Split line by commas and convert to integers
        idx += [int(k) for k in filter(None, line.split(","))]

    # Verify the total number of data items matches the expected count
    if len(idx) % num_data != 0:
        raise ReadError("Expected number of data items does not match element type")

    # Reshape data into 2D array where each row represents an element
    idx = np.array(idx).reshape((-1, num_data))
    # Create mapping from element IDs to their indices
    cell_ids = dict(zip(idx[:, 0], count(0)))
    # Convert node IDs to their corresponding indices using point_ids mapping
    cells = np.array([[point_ids[node] for node in elem] for elem in idx[:, 1:]])

    # Create element sets if ELSET is specified in parameters
    cell_sets = (
        # {params_map["ELSET"]: np.arange(len(cells), dtype="int32")}
        {params_map["ELSET"]: idx[:, 0]}  # use the actual element IDs
        if "ELSET" in params_map.keys()
        else {}
    )

    return cell_type, cells, cell_ids, cell_sets, line




def _read_set(f, params_map):
    set_ids = []
    set_names = []
    while True:
        line = f.readline()
        if not line or line.startswith("*"):
            break
        if line.strip() == "":
            continue

        line = line.strip().strip(",").split(",")
        if line[0].isnumeric():
            set_ids += [int(k) for k in line]
        else:
            set_names.append(line[0])

    set_ids = np.array(set_ids, dtype="int32")
    if "GENERATE" in params_map:
        if len(set_ids) != 3:
            raise ReadError(set_ids)
        set_ids = np.arange(set_ids[0], set_ids[1] + 1, set_ids[2], dtype="int32")
    return set_ids, set_names, line





def _read_distribution(f, params_map):
    # cell_ids = []
    cell_data = {}
    count = 0
    while True:
        line = f.readline()
        if not line:
            break
        if line.startswith("**"):
            continue
        elif line.startswith("*"):
            break
        if line.strip() == "":
            continue

        count += 1
        if count == 1: continue  # First line, ref frame (global)

        line = line.strip().strip(",").split(",")
        # cell_ids.append(int(line[0]))
        # cell_data.append(list(map(float, line[1:])))
        cell_data[int(line[0])] = list(map(float, line[1:]+[0, 0, 0]))
        # cell_data[int(line[0])] = list(map(float, line[1:]))

    return cell_data, line




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
            _density = float(line.strip().split(',')[0])
            material['density'] = _density

        elif keyword == 'ELASTIC':
            _elastic = []
            params_map = get_param_map(line)
            # print(params_map)
            _type = params_map.get('TYPE', 'ISOTROPIC')
            if _type == 'ISOTROPIC':
                material['type'] = 'isotropic'
                line = f.readline()
                _elastic += list(map(float, line.strip().split(',')))
            elif _type == 'ENGINEERING CONSTANTS':
                material['type'] = 'engineering_constants'
                line = f.readline()
                for _v in line.strip().split(','):
                    if _v != '': _elastic.append(float(_v))
                # _elastic += list(map(float, line.strip().split(',')))
                # _elastic.append(float(_v))
                line = f.readline()
                for _v in line.strip().split(','):
                    if _v != '': _elastic.append(float(_v))
                # _elastic += list(map(float, line.strip().split(',')))
            material['elastic'] = _elastic
            break

    # print(material)

    return material




def merge(
    mesh, points, cells, point_data, cell_data, field_data, point_sets, cell_sets
):
    """
    Merge Mesh object into existing containers for points, cells, sets, etc..

    :param mesh:
    :param points:
    :param cells:
    :param point_data:
    :param cell_data:
    :param field_data:
    :param point_sets:
    :param cell_sets:
    :type mesh: Mesh
    """
    ext_points = np.array([p for p in mesh.points])

    if len(points) > 0:
        new_point_id = points.shape[0]
        # new_cell_id = len(cells) + 1
        points = np.concatenate([points, ext_points])
    else:
        # new_cell_id = 0
        new_point_id = 0
        points = ext_points

    cnt = 0
    for c in mesh.cells:
        new_data = np.array([d + new_point_id for d in c.data])
        cells.append(CellBlock(c.type, new_data))
        cnt += 1

    # The following aren't currently included in the abaqus parser, and are therefore
    # excluded?
    # point_data.update(mesh.point_data)
    # cell_data.update(mesh.cell_data)
    # field_data.update(mesh.field_data)

    # Update point and cell sets to account for change in cell and point ids
    for key, val in mesh.point_sets.items():
        point_sets[key] = [x + new_point_id for x in val]

    # Todo: Add support for merging cell sets
    # cellblockref = [[] for i in range(cnt-new_cell_id)]
    # for key, val in mesh.cell_sets.items():
    #     cell_sets[key] = cellblockref + [np.array([x for x in val[0]])]

    return points, cells

