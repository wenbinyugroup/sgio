import os
import csv
import traceback
import math
import logging

# import numpy as np

import sgio.core.sg as mms
# import sgio.core.general as mmg
import sgio.core.beam as mmbm
import sgio.core.shell as mmps
import sgio.core.solid as mmsd
import sgio.utils.io as sui
# import sgio.utils.logger as mul

from sgio.core.sg import StructureGene
# from sgio.meshio import CellBlock, Mesh
# from sgio.meshio import read
import sgio.meshio as sm


logger = logging.getLogger(__name__)

def read(fn:str, file_format:str, format_version:str, smdim:int, sg:StructureGene=None):
    r"""Read SG input.

    Parameters
    ----------
    fn : str
        Name of the SG input file
    file_format : str
        Format of the SG input file
    smdim : int
        Dimension of the macro structural model
    """

    if file_format.lower().startswith('v') or file_format.lower().startswith('s'):
        with open(fn, 'r') as f:
            sg = readBuffer(f, file_format, format_version, smdim)

    else:
        if not sg:
            sg = StructureGene()
        sg.mesh = read(fn, file_format)

    return sg









def readBuffer(f, file_format:str, format_version:str, smdim:int):
    r"""
    """
    sg = StructureGene()
    sg.smdim = smdim

    # Read head
    configs = _readHeader(f, file_format, format_version, smdim)
    sg.sgdim = configs['sgdim']
    sg.physics = configs['physics']
    sg.do_dampling = configs.get('do_damping', 0)
    sg.use_elem_local_orient = configs.get('use_elem_local_orient', 0)
    sg.is_temp_nonuniform = configs.get('is_temp_nonuniform', 0)
    if smdim != 3:
        sg.model = configs['model']
        if smdim == 1:
            init_curvs = configs.get('curvature', [0.0, 0.0, 0.0])
            sg.initial_twist = init_curvs[0]
            sg.initial_curvature = init_curvs[1:]
        elif smdim == 2:
            sg.initial_curvature = configs.get('curvature', [0.0, 0.0])

    nnode = configs['num_nodes']
    nelem = configs['num_elements']

    # Read mesh
    sg.mesh = _readMesh(f, file_format, sg.sgdim, nnode, nelem, sg.use_elem_local_orient)

    # Read material in-plane angle combinations
    nma_comb = configs['num_mat_angle3_comb']
    sg.mocombos = _readMaterialRotationCombinations(f, nma_comb)

    # Read materials
    nmate = configs['num_materials']
    sg.materials = _readMaterials(f, file_format, nmate)

    return sg









def _readHeader(file, file_format:str, format_version:str, smdim:int):
    """
    """

    logger.debug('reading header...')

    configs = {}

    if file_format.lower().startswith('s'):
        if smdim == 1:
            line = sui.readNextNonEmptyLine(file)
            configs['model'] = int(line.split()[0])
            line = sui.readNextNonEmptyLine(file)
            configs['curvature'] = list(map(float, line.split()[:3]))
            line = sui.readNextNonEmptyLine(file)
            configs['oblique'] = list(map(float, line.split()[:2]))
        elif smdim == 2:
            line = sui.readNextNonEmptyLine(file)
            configs['model'] = int(line.split()[0])
            line = sui.readNextNonEmptyLine(file)
            configs['curvature'] = list(map(float, line.split()[:2]))
            if format_version >= '2.2':
                line = sui.readNextNonEmptyLine(file)
                configs['lame'] = list(map(float, line.split()[:2]))

        line = sui.readNextNonEmptyLine(file)
        line = line.split()
        configs['physics'] = int(line[0])
        configs['ndim_degen_elem'] = int(line[1])
        configs['use_elem_local_orient'] = int(line[2])
        configs['is_temp_nonuniform'] = int(line[3])
        if format_version >= '2.2':
            configs['force_flag'] = int(line[4])
            configs['steer_flag'] = int(line[5])

        line = sui.readNextNonEmptyLine(file)
        line = line.split()
        configs['sgdim'] = int(line[0])
        configs['num_nodes'] = int(line[1])
        configs['num_elements'] = int(line[2])
        configs['num_materials'] = int(line[3])
        configs['num_slavenodes'] = int(line[4])
        configs['num_mat_angle3_comb'] = int(line[5])

    elif file_format.lower().startswith('v'):
        configs['sgdim'] = 2

        line = sui.readNextNonEmptyLine(file)
        line = line.split()
        configs['format'] = int(line[0])
        configs['num_mat_angle3_comb'] = int(line[1])

        line = sui.readNextNonEmptyLine(file)
        line = line.split()
        configs['model'] = int(line[0])
        configs['do_damping'] = int(line[1])
        configs['physics'] = 1 if int(line[2]) > 0 else 0

        line = sui.readNextNonEmptyLine(file)
        line = line.split()
        configs['is_curve'] = int(line[0])
        configs['is_oblique'] = int(line[1])
        configs['model'] = 3 if line[2] == '1' else configs['model']  # trapeze
        configs['model'] = 2 if line[3] == '1' else configs['model']  # vlasov

        if configs['is_curve'] == 1:
            line = sui.readNextNonEmptyLine(file)
            line = line.split()
            configs['curvature'] = list(map(float, line[:3]))

        if configs['is_oblique'] == 1:
            line = sui.readNextNonEmptyLine(file)
            line = line.split()
            configs['oblique'] = list(map(float, line[:2]))

        line = sui.readNextNonEmptyLine(file)
        line = line.split()
        configs['num_nodes'] = int(line[0])
        configs['num_elements'] = int(line[1])
        configs['num_materials'] = int(line[2])

    return configs









# def _readSGInputHead(file, file_format:str, format_version:str, smdim:int):
#     """
#     """

#     logger.debug('reading header...')

#     configs = {}
#     if file_format.startswith('v'):
#         head = 3  # at least 3 lines in the head (flag) part
#         count = 0
#         configs['sgdim'] = 2
#         while True:
#             line = file.readline().strip()
#             if line == '':  continue

#             count += 1
#             line = line.split()
#             if count == 1:
#                 # format_flag  nlayer
#                 configs['format'] = int(line[0])
#                 configs['num_mat_angle3_comb'] = int(line[1])
#                 continue
#             elif count == 2:
#                 # timoshenko_flag  recover_flag  thermal_flag
#                 configs['model'] = int(line[0])
#                 configs['do_damping'] = int(line[1])
#                 configs['physics'] = 1 if int(line[2]) > 0 else 0
#                 continue
#             elif count == 3:
#                 # curve_flag  oblique_flag  trapeze_flag  vlasov_flag
#                 # line = list(map(int, line))
#                 # flag_curve = line[0]
#                 # flag_oblique = line[1]
#                 configs['is_curve'] = int(line[0])
#                 configs['is_oblique'] = int(line[1])
#                 configs['model'] = 3 if line[2] == '1' else configs['model']  # trapeze
#                 configs['model'] = 2 if line[3] == '1' else configs['model']  # vlasov
#                 # if line[2] == 1:
#                 #     sg.model = 3  # trapeze effect
#                 # if line[3] == 1:
#                 #     sg.model = 2  # Vlasov model
#                 if configs['is_curved'] == 1:
#                     head += 1  # extra line in the head
#                 if configs['is_oblique'] == 1:
#                     head += 1  # extra line in the head
#                 continue
#             elif configs['is_curve'] != 0 and count <= head:
#                 configs['curvature'] = list(map(float, line))  # k1, k2, k3
#                 continue
#             elif configs['is_oblique'] and count <= head:
#                 configs['oblique'] = list(map(float, line))  # cos11, cos21
#                 continue
#             elif count == (head + 1):
#                 # nnode  nelem  nmate
#                 # line = list(map(int, line))
#                 configs['num_nodes'] = int(line[0])
#                 configs['num_elements'] = int(line[1])
#                 configs['num_materials'] = int(line[2])
#                 break

#     elif file_format.startswith('s'):
#         head = 2  # at least 3 lines in the head (flag) part
#         if smdim == 1:
#             head += 3
#         elif smdim == 2:
#             head += 2
#         count = 0
#         while True:
#             line = file.readline().strip()
#             if line == '':  continue

#             count += 1
#             line = line.split()

#             if smdim == 1:
#                 if count == 1:  # model
#                     configs['model'] = int(line[0])
#                     continue
#                 elif count == 2:  # initial twist/curvatures
#                     line = list(map(float, line))
#                     configs['curvature'] = list(map(float, line))
#                     # sg.initial_twist = line[0]
#                     # sg.initial_curvature = [line[1], line[2]]
#                     continue
#                 elif count == 3:  # oblique
#                     # line = list(map(float, line))
#                     configs['oblique'] = list(map(float, line))
#                     continue
#             elif smdim == 2:
#                 if count == 1:  # model
#                     # line = list(map(int, line))
#                     configs['model'] = int(line[0])
#                     continue
#                 elif count == 2:
#                     # initial twist/curvature
#                     # line = list(map(float, line))
#                     configs['curvature'] = list(map(float, line))
#                     continue

#             if count == (head - 1):
#                 # analysis  elem_flag  trans_flag  temp_flag
#                 # line = list(map(int, line))
#                 configs['physics'] = int(line[0])
#                 configs['ndim_degen_elem'] = int(line[1])
#                 configs['use_elem_local_orient'] = int(line[2])
#                 configs['is_temp_nonuniform'] = line[3]
#                 continue
#             elif count == head:
#                 # nsg  nnode  nelem  nmate  nslave  nlayer
#                 line = list(map(int, line))
#                 # print('line =', line)
#                 configs['sgdim'] = int(line[0])
#                 configs['num_nodes'] = int(line[1])
#                 configs['num_elements'] = int(line[2])
#                 configs['num_materials'] = int(line[3])
#                 configs['num_slavenodes'] = int(line[4])
#                 configs['num_mat_angle3_comb'] = int(line[5])
#                 break

#     return configs









def _readMesh(file, file_format:str, sgdim:int, nnode:int, nelem:int, read_local_frame):
    """
    """

    logger.debug('reading mesh...')

    mesh = sm.read(
        file, file_format,
        sgdim=sgdim, nnode=nnode, nelem=nelem, read_local_frame=read_local_frame
    )

    return mesh









def _readMaterialRotationCombinations(file, ncomb):
    """
    """

    logger.debug('reading combinations of material and in-plane rotations...')

    combinations = {}

    counter = 0
    while counter < ncomb:
        line = file.readline().strip()
        while line == '':
            line = file.readline().strip()

        line = line.split()
        comb_id = int(line[0])
        mate_id = int(line[1])
        ip_ratation = float(line[2])

        combinations[comb_id] = [mate_id, ip_ratation]

        counter += 1

    return combinations









def _readMaterials(file, file_format:str, nmate:int):
    """
    """

    logger.debug('reading materials...')

    materials = {}

    counter = 0
    while counter < nmate:
        line = file.readline().strip()
        while line == '':
            line = file.readline().strip()

        line = line.split()

        # Read material id, isotropy
        if file_format.lower().startswith('s'):
            mate_id, isotropy, ntemp = list(map(int, line))
        elif file_format.lower().startswith('v'):
            mate_id, isotropy = list(map(int, line))
            ntemp = 1
            # material, line = _readMaterial(file, file_format, isotropy)

        material = _readMaterial(file, file_format, isotropy, ntemp)

        materials[mate_id] = material

        counter += 1

    return materials




def _readMaterial(file, file_format:str, isotropy:int, ntemp:int=1):
    """
    """

    mp = mmsd.MaterialProperty()
    mp.isotropy = isotropy

    temp_counter = 0
    while temp_counter < ntemp:

        if file_format.lower().startswith('s'):
            line = file.readline().strip()
            while line == '':
                line = file.readline().strip()
            line = line.split()
            temperature, density = list(map(float, line))
            mp.temperature = temperature

        # Read conductivity properties
        if file_format.lower().startswith('s'):
            pass

        # Read elastic properties
        elastic_props = _readElasticProperty(file, isotropy)
        mp.setElasticProperty(elastic_props, isotropy)

        if file_format.lower().startswith('v'):
            line = file.readline().strip()
            while line == '':
                line = file.readline().strip()
            density = float(line)

        mp.density = density

        # Read thermal properties

        temp_counter += 1

    return mp









def _readElasticProperty(file, isotropy:int):
    """
    """

    constants = []

    if isotropy == 0:
        nrow = 1
    elif isotropy == 1:
        nrow = 3
    elif isotropy == 2:
        nrow = 6

    for i in range(nrow):
        line = file.readline().strip()
        while line == '':
            line = file.readline().strip()
        constants.extend(list(map(float, line.split())))

    return constants



# def _readSGInputMesh(f, file_format:str, nnodes:int, nelems:int, smdim:int, sgdim:int=3):
#     r"""
#     """
#     # Initialize the optional data fields
#     points = []
#     cells = []
#     cell_ids = []
#     point_sets = {}
#     cell_sets = {}
#     cell_sets_element = {}  # Handle cell sets defined in ELEMENT
#     cell_sets_element_order = []  # Order of keys is not preserved in Python 3.5
#     field_data = {}
#     cell_data = {}
#     point_data = {}
#     point_ids = None

#     # while True:

#     #     if line == '':
#     #         line = f.readline()
#     #         continue

#     points, point_ids, line = _readSGInputNodes(f, nnodes, sgdim)

#     cells_dict, prop_ids, ids, line = _readSGInputElements(f, file_format, nelems, point_ids)
#     cell_type_to_id = {}
#     for _cell_type, _cell_points in cells_dict.items():
#         cells.append(CellBlock(_cell_type, _cell_points))
#         cell_type_to_id[_cell_type] = len(cells) - 1

#     if file_format.lower().startswith('s'):
#         _cd = []
#         for _cb in cells:
#             _ct = _cb.type
#             _cd.append(prop_ids[_ct])
#         # cell_data['property'] = np.array(_cd)
#         cell_data['gmsh:physical'] = np.array(_cd)

#     return Mesh(
#         points,
#         cells,
#         point_data=point_data,
#         cell_data=cell_data,
#         field_data=field_data,
#         point_sets=point_sets,
#         cell_sets=cell_sets,
#     )


# def _readSGInputNodes(f, nnodes:int, sgdim:int=3):
#     points = []
#     point_ids = {}
#     counter = 0
#     while counter < nnodes:
#         line = f.readline()
#         if line.strip() == "":
#             continue

#         line = line.strip().split()
#         point_id, coords = line[0], line[1:]
#         point_ids[int(point_id)] = counter
#         points.append([0.0,]*(3-sgdim)+[float(x) for x in coords])
#         counter += 1

#     return np.array(points, dtype=float), point_ids, line


# def _readSGInputElements(f, file_format:str, nelems:int, point_ids):
#     cells = {}
#     prop_ids = {}  # property id for each element; will update cell_data (swiftcomp)
#     cell_ids = {}
#     counter = 0
#     while counter < nelems:
#         line = f.readline()
#         if line.strip() == "":
#             continue

#         line = line.strip().split()
#         if file_format.lower().startswith('v'):
#             cell_id, node_ids = line[0], line[1:]
#         elif file_format.lower().startswith('s'):
#             cell_id, prop_id, node_ids = line[0], line[1], line[2:]

#         # Check element type
#         cell_type = ''
#         if len(node_ids) == 5:  # 1d elements
#             node_ids = [int(_i) for _i in node_ids if _i != '0']
#             if len(node_ids) == 2:
#                 cell_type = 'line'
#             else:
#                 cell_type = 'line{}'.format(len(node_ids))
#         elif len(node_ids) == 9:  # 2d elements
#             if node_ids[3] == '0':  # triangle
#                 node_ids = [int(_i) for _i in node_ids if _i != '0']
#                 cell_type = {3: 'triangle', 6: 'triangle6'}[len(node_ids)]
#             else:  # quadrilateral
#                 node_ids = [int(_i) for _i in node_ids if _i != '0']
#                 cell_type = {4: 'quad', 8: 'quad8', 9: 'quad9'}[len(node_ids)]
#         elif len(node_ids) == 20:  # 3d elements
#             if node_ids[4] == '0':  # tetrahedral
#                 node_ids = [int(_i) for _i in node_ids if _i != '0']
#                 cell_type = {4: 'tetra', 10: 'tetra10'}[len(node_ids)]
#             elif node_ids[6] == '0':  # wedge
#                 node_ids = [int(_i) for _i in node_ids if _i != '0']
#                 cell_type = {6: 'wedge', 15: 'tetra15'}[len(node_ids)]
#             else:  # hexahedron
#                 node_ids = [int(_i) for _i in node_ids if _i != '0']
#                 cell_type = {8: 'hexahedron', 20: 'hexahedron20'}[len(node_ids)]


#         if not cell_type in cells.keys():
#             cells[cell_type] = []
#             cell_ids[cell_type] = {}
#             prop_ids[cell_type] = []

#         cells[cell_type].append([point_ids[_i] for _i in node_ids])
#         cell_ids[cell_type][int(cell_id)] = len(cell_ids[cell_type]) - 1
#         if file_format.lower().startswith('s'):
#             prop_ids[cell_type].append(int(prop_id))

#         counter += 1

#     return cells, prop_ids, cell_ids, line









def readOutput(fn_in:str, solver:str, smdim:int, analysis=0):
    if solver.startswith('s'):
        return readSCOut(fn_in, smdim, analysis)
    elif solver.startswith('v'):
        return readVABSOut(fn_in, analysis)
    return



def readSGOutFailureIndex(fn, solver):
    r"""
    """
    # if not logger:
    #     logger = mul.initLogger(__name__)

    logger.info('reading sg failure indices and strengh ratios: {}...'.format(fn))

    lines = []
    load_case = 0
    sr_min = None
    with open(fn, 'r') as fobj:
        for i, line in enumerate(fobj):
            line = line.strip()
            if (line == ''):
                continue
            if line.startswith('Failure index'):
                continue

            if (line.startswith('The sectional strength ratio is')):
                line = line.split()
                tmp_id = line.index('existing')
                sr_min = float(line[tmp_id - 1])
                eid_sr_min = int(line[-1])
                # lines.pop()
                continue

            line = line.split()
            if len(line) == 3:
                lines.append(line)

    result = []
    # fis = []
    # srs = []
    for line in lines:
        # line = line.strip().split()
        result.append([int(line[0]), float(line[1]), float(line[2])])
        # fis.append(float(line[1]))
        # srs.append(float(line[2]))

    return result, sr_min, eid_sr_min









# def readVABSIn(fn_vabs_in):
#     """ Read data from the VABS input file.

#     Parameters
#     ----------
#     fn_vabs_in : str
#         File name of the VABS input file.

#     Returns
#     -------
#     msgpi.sg.StructureGene
#         Structure gene object
#     """

#     # if logger is None:
#     #     logger = mul.initLogger(__name__)

#     logger.info('reading VABS input: {0}...'.format(fn_vabs_in))

#     try:
#         fn_base, fn_extn = os.path.splitext(fn_vabs_in)
#         name = os.path.basename(fn_base)
#         sg = mms.StructureGene(name, 2, 1)

#         flag_curve = 0
#         flag_oblique = 0

#         count = 0
#         count_node = 1
#         count_element = 1
#         count_layertype = 1
#         count_material = 1
#         line_material = 0
#         head = 3  # at least 3 lines in the head (flag) part
#         with open(fn_vabs_in, 'r') as fin:
#             for li, line in enumerate(fin):
#                 line = line.strip()
#                 if line == '\n' or line == '':
#                     continue

#                 count += 1
#                 line = line.split()
#                 if count == 1:
#                     # format_flag  nlayer
#                     line = list(map(int, line))
#                     flag_format = line[0]
#                     num_layertypes = line[1]
#                     continue
#                 elif count == 2:
#                     # timoshenko_flag  recover_flag  thermal_flag
#                     line = list(map(int, line))
#                     sg.model = line[0]
#                     sg.damping = line[1]
#                     sg.physics = line[2]
#                     if sg.physics > 0:
#                         sg.physics == 1
#                     continue
#                 elif count == 3:
#                     # curve_flag  oblique_flag  trapeze_flag  vlasov_flag
#                     line = list(map(int, line))
#                     flag_curve = line[0]
#                     flag_oblique = line[1]
#                     if line[2] == 1:
#                         sg.model = 3  # trapeze effect
#                     if line[3] == 1:
#                         sg.model = 2  # Vlasov model
#                     if flag_curve == 1:
#                         head += 1  # extra line in the head
#                     if flag_oblique == 1:
#                         head += 1  # extra line in the head
#                     continue
#                 elif flag_curve != 0 and count <= head:
#                     pass
#                 elif flag_oblique != 0 and count <= head:
#                     pass
#                 elif count == (head + 1):
#                     # nnode  nelem  nmate
#                     line = list(map(int, line))
#                     num_nodes = line[0]
#                     num_elements = line[1]
#                     num_materials = line[2]
#                     continue
#                 elif count_node <= num_nodes:
#                     # Read nodal coordinates
#                     sg.nodes[int(line[0])] = [
#                         float(line[1]), float(line[2])]
#                     count_node += 1
#                     continue
#                 elif count_element <= num_elements:
#                     # Read element connectivities
#                     eid = int(line[0])
#                     sg.elementids.append(eid)
#                     temp = [int(i) for i in line[1:] if i != '0']
#                     sg.elements[eid] = temp
#                     sg.elementids2d.append(eid)
#                     count_element += 1
#                     continue
#                 elif count_element <= (2 * num_elements):
#                     sg.trans_element = 1
#                     # Read element theta1
#                     if flag_format == 1:
#                         # new format
#                         eid = int(line[0])
#                         lyrtp = int(line[1])
#                         theta1 = float(line[2])
#                     else:
#                         # old format
#                         eid = int(line[0])
#                         mid = int(line[1])
#                         theta3 = float(line[2])
#                         theta1 = float(line[3])
#                         lyrtp = 0
#                         for k, v in sg.mocombos.items():
#                             if (mid == v[0]) and (theta3 == v[1]):
#                                 lyrtp = k
#                                 break
#                         if lyrtp == 0:
#                             lyrtp = len(sg.mocombos) + 1
#                             sg.mocombos[lyrtp] = [mid, theta3]

#                     if lyrtp not in sg.prop_elem.keys():
#                         sg.prop_elem[lyrtp] = []
#                     sg.prop_elem[lyrtp].append(eid)
#                     sg.elem_prop[eid] = lyrtp
#                     # self.elem_angle[eid] = theta1
#                     sg.elem_orient[eid] = [
#                         [1.0, 0.0, 0.0],
#                         [0.0, 1.0, 0.0],
#                         [0.0, 0.0, 0.0]
#                     ]
#                     sg.elem_orient[eid][1][1] = math.cos(math.radians(theta1))
#                     sg.elem_orient[eid][1][2] = math.sin(math.radians(theta1))
#                     count_element += 1
#                     continue
#                 elif (flag_format == 1) and (count_layertype <= num_layertypes):
#                     # Read layer types
#                     ltid = int(line[0])
#                     mid = int(line[1])
#                     theta3 = float(line[2])
#                     # print('theta3 =', theta3)
#                     sg.mocombos[ltid] = [mid, theta3]
#                     count_layertype += 1
#                     continue
#                 elif count_material <= num_materials:
#                     # Read materials
#                     if line_material == 0:
#                         mid = int(line[0])
#                         # mtype = int(line[1])
#                         mp = mmsd.MaterialProperty()
#                         mp.anisotropy = int(line[1])
#                         # sg.materials[mid].eff_props[3]['type'] = mtype
#                         line_material += 1
#                         continue

#                     if mp.anisotropy == 0:
#                         # isotropic
#                         if line_material == 1:
#                             e = float(line[0])
#                             nu = float(line[1])
#                             consts = [e, nu]
#                             # sg.materials[mid].eff_props[3]['constants']['e'] = e
#                             # sg.materials[mid].eff_props[3]['constants']['nu'] = nu
#                             line_material = 99
#                             continue
#                     elif mp.anisotropy == 1:
#                         # print('line =', line)
#                         # print('line_material =', line_material)
#                         # orthotropic
#                         # consts = []
#                         if line_material == 1:
#                             # pe = []
#                             e = list(map(float, line))
#                             consts = e
#                             # sg.materials[mid].eff_props[3]['constants']['e1'] = e[0]
#                             # sg.materials[mid].eff_props[3]['constants']['e2'] = e[1]
#                             # sg.materials[mid].eff_props[3]['constants']['e3'] = e[2]
#                             # for ei in e:
#                             #     pe.append(ei)
#                             # sg.materials[mid].property_elastic += e
#                             line_material += 1
#                             continue
#                         elif line_material == 2:
#                             g = list(map(float, line))
#                             consts.append(g[0])
#                             consts.append(g[1])
#                             consts.append(g[2])
#                             # sg.materials[mid].eff_props[3]['constants']['g12'] = g[0]
#                             # sg.materials[mid].eff_props[3]['constants']['g13'] = g[1]
#                             # sg.materials[mid].eff_props[3]['constants']['g23'] = g[2]
#                             # for gi in g:
#                             #     pe.append(gi)
#                             # self.materials[mid].property_elastic += g
#                             line_material += 1
#                             continue
#                         elif line_material == 3:
#                             nu = list(map(float, line))
#                             consts.append(nu[0])
#                             consts.append(nu[1])
#                             consts.append(nu[2])
#                             # sg.materials[mid].eff_props[3]['constants']['nu12'] = nu[0]
#                             # sg.materials[mid].eff_props[3]['constants']['nu13'] = nu[1]
#                             # sg.materials[mid].eff_props[3]['constants']['nu23'] = nu[2]
#                             # for nui in nu:
#                             #     pe.append(nui)
#                             # sg.materials[mid].property_elastic.append(pe)
#                             line_material = 99
#                             continue
#                     elif mp.anisotropy == 2:
#                         # anisotropic
#                         continue

#                     if line_material == 99:
#                         mp.density = float(line[0])
#                         # print(consts)
#                         mp.assignConstants(consts)
#                         # sg.materials[mid].eff_props[3]['density'] = dens
#                         # self.mate_propt[mid].append(dens)
#                         # mp.summary()
#                         sg.materials[mid] = mp
#                         line_material = 0
#                         count_material += 1  # next material
#                         continue
#                     continue
#     except:
#         # e = sys.exc_info()[0]
#         e = traceback.format_exc()
#         print(e)

#     return sg




def readVABSOutHomo(fn, scrnout=True):
    """Read VABS homogenization results

    Parameters
    ----------
    fn : str
        VABS output file name (e.g. example.sg.k).
    scrnout : bool, default True
        Switch of printing cmd output.

    Returns
    -------
    msgpi.sg.MaterialSection
        Material/sectional properties.
    """
    # sm = mms.MaterialSection(smdim = 1)
    bp = mmbm.BeamProperty()

    linesRead = []
    keywordsIndex = {}


    with open(fn, 'r') as fin:
        ln = -1
        lines = fin.readlines()
        for i, line in enumerate(lines):

            line = line.strip()

            if len(line) > 0:
                linesRead.append(line)
                ln += 1
            else:
                continue

            if '=====' in line:
                continue

            line = line.lower()
            # line = line.replace('-', ' ')

            if 'geometric center' in line:
                keywordsIndex['gc'] = ln
            elif 'area =' in line:
                bp.area = float(line.split()[-1])


            # Inertial properties
            # -------------------

            elif '6x6 mass matrix at the mass center' in line:
                keywordsIndex['mass_mc'] = ln
            elif '6x6 mass matrix' in line:
                keywordsIndex['mass'] = ln
            elif 'mass center of the cross section' in line or 'mass center of the cross-section' in line:
                keywordsIndex['mc'] = ln
            elif 'mass per unit span' in line:
                bp.mu = float(line.split()[-1])
            elif 'inertia i11' in line:
                bp.i11 = float(line.split()[-1])
            elif 'inertia i22' in line:
                bp.i22 = float(line.split()[-1])
            elif 'inertia i33' in line:
                bp.i33 = float(line.split()[-1])
            elif 'principal inertial axes rotated' in line:
                line = line.split()
                try:
                    tmp_id = line.index('degrees')
                except ValueError:
                    line = lines[i+1].split()
                    tmp_id = line.index('degrees')
                bp.phi_pia = float(line[tmp_id - 1])
            elif 'mass-weighted radius of gyration' in line:
                bp.rg = float(line.split()[-1])


            # Structural properties
            # ---------------------

            elif 'classical stiffness matrix' in line:
                keywordsIndex['csm'] = ln
            elif 'classical compliance matrix' in line:
                keywordsIndex['cfm'] = ln

            elif 'tension center' in line:
                keywordsIndex['tc'] = ln
            elif 'extension stiffness ea' in line:
                bp.ea = float(line.split()[-1])
            elif 'torsional stiffness gj' in line:
                bp.gj = float(line.split()[-1])
            elif 'principal bending stiffness ei22' in line:
                bp.ei22 = float(line.split()[-1])
            elif 'principal bending stiffness ei33' in line:
                bp.ei33 = float(line.split()[-1])
            elif 'principal bending axes rotated' in line:
                line = line.split()
                try:
                    tmp_id = line.index('degrees')
                except ValueError:
                    line = lines[i+1].split()
                    tmp_id = line.index('degrees')
                bp.phi_pba = float(line[tmp_id - 1])

            elif 'timoshenko stiffness matrix' in line:
                keywordsIndex['tsm'] = ln
            elif 'timoshenko compliance matrix' in line:
                keywordsIndex['tfm'] = ln

            elif 'shear center' in line:
                keywordsIndex['sc'] = ln
            elif 'principal shear stiffness ga22' in line:
                bp.ga22 = float(line.split()[-1])
            elif 'principal shear stiffness ga33' in line:
                bp.ga33 = float(line.split()[-1])
            elif 'principal shear axes rotated' in line:
                line = line.split()
                try:
                    tmp_id = line.index('degrees')
                except ValueError:
                    line = lines[i+1].split()
                    tmp_id = line.index('degrees')
                bp.phi_psa = float(line[tmp_id - 1])

            # elif 'Vlasov Stiffness Matrix' in line:
            #     keywordsIndex['vsm'] = ln
            # elif 'Vlasov Flexibility Matrix' in line:
            #     keywordsIndex['vfm'] = ln
            
            # elif 'Trapeze Effects' in line:
            #     keywordsIndex['te'] = ln
            # elif 'Ag1--Ag1--Ag1--Ag1' in line:
            #     keywordsIndex['te_ag'] = ln
            # elif 'Bk1--Bk1--Bk1--Bk1' in line:
            #     keywordsIndex['te_bk'] = ln
            # elif 'Ck2--Ck2--Ck2--Ck2' in line:
            #     keywordsIndex['te_ck'] = ln
            # elif 'Dk3--Dk3--Dk3--Dk3' in line:
            #     keywordsIndex['te_dk'] = ln


    ln = keywordsIndex['mass']
    bp.mass = sui.textToMatrix(linesRead[ln + 2:ln + 8])

    if 'mass_mc' in keywordsIndex.keys():
        ln = keywordsIndex['mass_mc']
        bp.mass_cs = sui.textToMatrix(linesRead[ln + 2:ln + 8])

    #check whether the analysis is Vlasov or timoshenko
    #Read stiffness matrix and compliance matrix
    if 'vsm' in keywordsIndex.keys():
        pass
        # try:
        #     ln = keywordsIndex['vsm']
        #     sm.stiffness_refined = utl.textToMatrix(linesRead[ln + 3:ln + 8])
        #     #old dic to save valsov stiffness matrix
        #     # sm.eff_props[1]['stiffness']['refined'] = utl.textToMatrix(linesRead[ln + 3:ln + 8])
        # except KeyError:
        #     if scrnout:
        #         print('No Vlasov stiffness matrix found.')
        #     else:
        #         pass
        # try:
        #     ln = keywordsIndex['vfm']
        #     sm.compliance_refined = utl.textToMatrix(linesRead[ln + 3:ln + 8])
        #     #old dic to save valsov compliance matrix
        #     # sm.eff_props[1]['compliance']['refined'] = utl.textToMatrix(linesRead[ln + 3:ln + 8])            
        # except KeyError:
        #     if scrnout:
        #         print('No Vlasov flexibility matrix found.')
        #     else:
        #         pass
        #check whether trapeze effect analysis is on and read the correponding matrix
        # if 'te' in keywordsIndex.keys():
        #     try:
        #         ln = keywordsIndex['te_ag']
        #         sm.trapeze_effect['ag'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Ag1--Ag1--Ag1--Ag1 matrix found.')
        #         else:
        #             pass
        #     try:
        #         ln = keywordsIndex['te_bk']
        #         sm.trapeze_effect['bk'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Bk1--Bk1--Bk1--Bk1 matrix found.')
        #         else:
        #             pass
        #     try:
        #         ln = keywordsIndex['te_ck']
        #         sm.trapeze_effect['ck'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Ck2--Ck2--Ck2--Ck2 matrix found.')
        #         else:
        #             pass    
        #     try:
        #         ln = keywordsIndex['te_dk']
        #         sm.trapeze_effect['dk'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Dk3--Dk3--Dk3--Dk3 matrix found.')
        #         else:
        #             pass                   
    else:
        try:
            ln = keywordsIndex['csm']
            bp.stff = sui.textToMatrix(linesRead[ln + 2:ln + 6])
            #old dic method to save classical stiffness
            # sm.eff_props[1]['stiffness']['classical'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        except KeyError:
            if scrnout:
                print('No classical stiffness matrix found.')
            else:
                pass

        try:
            ln = keywordsIndex['cfm']
            bp.cmpl = sui.textToMatrix(linesRead[ln + 2:ln + 6])
            #old dic method to save classical compliance
            # sm.eff_props[1]['compliance']['classical'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        except KeyError:
            if scrnout:
                print('No classical compliance matrix found.')
            else:
                pass

        try:
            ln = keywordsIndex['tsm']
            bp.stff_t = sui.textToMatrix(linesRead[ln + 2:ln + 8])
            #old dic method to save refined stiffness matrix
            # sm.eff_props[1]['stiffness']['refined'] = utl.textToMatrix(linesRead[ln + 3:ln + 9])
        except KeyError:
            if scrnout:
                print('No Timoshenko stiffness matrix found.')
            else:
                pass
        try:
            ln = keywordsIndex['tfm']
            bp.cmpl_t = sui.textToMatrix(linesRead[ln + 2:ln + 8])
            #old dic method to save refined compliance matrix
            # sm.eff_props[1]['compliance']['refined'] = utl.textToMatrix(linesRead[ln + 3:ln + 9])
        except KeyError:
            if scrnout:
                print('No Timoshenko compliance matrix found.')
            else:
                pass

        if 'tc' in keywordsIndex.keys():
            ln = keywordsIndex['tc']
            bp.xt2, bp.xt3 = list(map(float, linesRead[ln + 2].split()))
        if 'sc' in keywordsIndex.keys():
            ln = keywordsIndex['sc']
            bp.xs2, bp.xs3 = list(map(float, linesRead[ln + 2].split()))
        if 'mc' in keywordsIndex.keys():
            ln = keywordsIndex['mc']
            bp.xm2, bp.xm3 = list(map(float, linesRead[ln + 2].split()))
        if 'gc' in keywordsIndex.keys():
            ln = keywordsIndex['gc']
            bp.xg2, bp.xg3 = list(map(float, linesRead[ln + 2].split()))

        #check whether trapeze effect analysis is on and read the correponding matrix
        # if 'te' in keywordsIndex.keys():
        #     try:
        #         ln = keywordsIndex['te_ag']
        #         sm.trapeze_effect['ag'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Ag1--Ag1--Ag1--Ag1 matrix found.')
        #         else:
        #             pass
        #     try:
        #         ln = keywordsIndex['te_bk']
        #         sm.trapeze_effect['bk'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Bk1--Bk1--Bk1--Bk1 matrix found.')
        #         else:
        #             pass
        #     try:
        #         ln = keywordsIndex['te_ck']
        #         sm.trapeze_effect['ck'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Ck2--Ck2--Ck2--Ck2 matrix found.')
        #         else:
        #             pass    
        #     try:
        #         ln = keywordsIndex['te_dk']
        #         sm.trapeze_effect['dk'] = utl.textToMatrix(linesRead[ln + 3:ln + 7])
        #     except KeyError:
        #         if scrnout:
        #             print('No Dk3--Dk3--Dk3--Dk3 matrix found.')
        #         else:
        #             pass              

    return bp




def readVABSOutStrengthRatio(fn_in):
    lines = []
    sr_min = None
    with open(fn_in, 'r') as fin:
        for i, line in enumerate(fin.readlines()):
            line = line.strip()
            if (line == ''):
                continue
            if line.startswith('Failure index'):
                continue
            # lines.append(line)
            # initial failure indices and strength ratios
            if (line.startswith('The sectional strength ratio is')):
                line = line.split()
                tmp_id = line.index('existing')
                sr_min = float(line[tmp_id - 1])
                # lines.pop()
                continue
            line = line.split()
            if len(line) == 3:
                lines.append(line)

    # print(lines)
    # initial failure indices and strength ratios
    fis = []
    srs = []
    for line in lines:
        # line = line.strip().split()
        # results.append([int(line[0]), float(line[1]), float(line[2])])
        fis.append(float(line[1]))
        srs.append(float(line[2]))
    return fis, srs, sr_min




def readVABSOut(fn_in, analysis=0, scrnout=True):
    """Read VABS outputs.

    Parameters
    ----------
    fn_in : str
        VABS input file name.
    analysis : {0, 1, 2, 3, '', 'h', 'dn', 'dl', 'd', 'l', 'fi'}
        Analysis to be carried out.

        * 0 or 'h' or '' - homogenization
        * 1 or 'dn' - dehomogenization (nonlinear)
        * 2 or 'dl' or 'd' or 'l' - dehomogenization (linear)
        * 3 or 'fi' - initial failure indices and strength ratios
    scrnout : bool, optional
        Switch of printing solver messages, by default True.

    Returns
    -------
    various
        Different analyses return different types of results.
    """
    if analysis == 0 or analysis == 'h' or analysis == '':
        # Read homogenization results
        if not fn_in.lower()[-2:] == '.k':
            fn_in = fn_in + '.K'
        return readVABSOutHomo(fn_in, scrnout)
    elif analysis == 1 or analysis == 2 or ('d' in analysis) or analysis == 'l':
        pass
    elif analysis == 3 or analysis == 'fi':
        # return readVABSOutStrengthRatio(fn_in+'.fi')
        return readSGOutFailureIndex(fn_in+'.fi', 'vabs')




# def readSCIn(fn_sg, smdim):
#     """ Read data from the SwiftComp input file

#     :param fn_sg: File name of the SwiftComp input file
#     :type fn_sg: string
#     """

#     # if logger is None:
#     #     logger = mul.initLogger(__name__)

#     fn_base, fn_extn = os.path.splitext(fn_sg)
#     name = os.path.basename(fn_base)
#     sg = mms.StructureGene(name, 3, smdim)

#     count = 0
#     count_node = 1
#     count_element = 1
#     count_layertype = 1
#     count_material = 1
#     line_material = 0
#     extra_head = 0
#     if smdim == 1:
#         extra_head = 3
#     elif smdim == 2:
#         extra_head = 2
#     head = 2  # at least 3 lines in the head (flag) part
#     with open(fn_sg, 'r') as fin:
#         for li, line in enumerate(fin):
#             line = line.strip()
#             if line == '\n' or line == '':
#                 continue

#             count += 1
#             line = line.split()
#             if count <= (extra_head + head):
#                 # Read head
#                 if count == 1:
#                     logger.debug('- reading head...')

#                 if smdim == 1:
#                     if count == 1:
#                         # model
#                         line = list(map(int, line))
#                         sg.model = line[0]
#                     elif count == 2:
#                         # initial twist/curvatures
#                         line = list(map(float, line))
#                         sg.initial_twist = line[0]
#                         sg.initial_curvature = [line[1], line[2]]
#                     elif count == 3:
#                         # oblique
#                         line = list(map(float, line))
#                         sg.oblique = line
#                 elif smdim == 2:
#                     if count == 1:
#                         # model
#                         line = list(map(int, line))
#                         sg.model = line[0]
#                     elif count == 2:
#                         # initial twist/curvature
#                         line = list(map(float, line))
#                         sg.initial_curvature = line

#                 if count == (extra_head + head - 1):
#                     # analysis  elem_flag  trans_flag  temp_flag
#                     line = list(map(int, line))
#                     sg.analysis = line[0]
#                     sg.degen_element = line[1]
#                     sg.trans_element = line[2]
#                     sg.nonuniform_temperature = line[3]
#                 elif count == (extra_head + head):
#                     # nsg  nnode  nelem  nmate  nslave  nlayer
#                     line = list(map(int, line))
#                     # print('line =', line)
#                     sg.sgdim = line[0]
#                     num_nodes = line[1]
#                     num_elements = line[2]
#                     num_materials = line[3]
#                     num_slavenodes = line[4]
#                     sg.num_slavenodes = num_slavenodes
#                     num_layertypes = line[5]
#                 continue
#             elif count_node <= num_nodes:
#                 # Read nodal coordinates
#                 if count_node == 1:
#                     logger.debug('- reading nodal coordinates...')
#                 sg.nodes[int(line[0])] = list(map(float, line[1:]))
#                 count_node += 1
#                 continue
#             elif count_element <= num_elements:
#                 # Read element material/layer connectivities
#                 if count_element == 1:
#                     logger.debug('- reading elemental connectivities...')
#                 line = list(map(int, line))
#                 eid = line[0]
#                 lyrtp = line[1]

#                 sg.elementids.append(eid)
#                 sg.elements[eid] = [i for i in line[2:] if i != 0]
#                 sg.elementids2d.append(eid)

#                 if lyrtp not in sg.prop_elem.keys():
#                     sg.prop_elem[lyrtp] = []
#                 sg.prop_elem[lyrtp].append(eid)
#                 sg.elem_prop[eid] = lyrtp

#                 count_element += 1
#                 continue
#             elif (sg.trans_element != 0) and (count_element <= (2 * num_elements)):
#                 # Read element orientation (a b c)
#                 if count_element == (num_elements + 1):
#                     logger.debug('- reading elemental orientations...')
#                 eid = int(line[0])
#                 a = list(map(float, line[1:4]))
#                 b = list(map(float, line[4:7]))
#                 c = list(map(float, line[7:10]))
#                 sg.elem_orient[eid] = [a, b, c]

#                 count_element += 1
#                 continue
#             elif count_layertype <= num_layertypes:
#                 # Read layer types
#                 if count_layertype == 1:
#                     logger.debug('- reading layer types...')
#                 ltid = int(line[0])
#                 mid = int(line[1])
#                 theta3 = float(line[2])
#                 sg.mocombos[ltid] = [mid, theta3]
#                 count_layertype += 1
#                 continue
#             elif count_material <= num_materials:
#                 # Read materials
#                 if count_material == 1:
#                     logger.debug('- reading materials...')
#                 if line_material == 0:
#                     line = list(map(int, line))
#                     mid = line[0]
#                     mtype = line[1]
#                     num_temp = line[2]
#                     mp = mmsd.MaterialProperty()
#                     # sg.materials[mid].eff_props[3]['type'] = mtype
#                     mp.anisotropy = mtype
#                     line_material += 1
#                     continue
#                 elif line_material == 1:
#                     # line = list(map(float, line))
#                     # sg.materials[mid].eff_props[3]['density'] = float(line[1])
#                     mp.density = float(line[1])
#                     line_material += 1
#                     continue

#                 if mtype == 0:
#                     # isotropic
#                     if line_material == 2:
#                         e = float(line[0])
#                         nu = float(line[1])
#                         consts = [e, nu]
#                         # sg.materials[mid].eff_props[3]['constants']['e'] = e
#                         # sg.materials[mid].eff_props[3]['constants']['nu'] = nu
#                         line_material = 99
#                         continue
#                 elif mtype == 1:
#                     # orthotropic
#                     if line_material == 2:
#                         # pe = []
#                         e = list(map(float, line))
#                         consts = e
#                         # sg.materials[mid].eff_props[3]['constants']['e1'] = e[0]
#                         # sg.materials[mid].eff_props[3]['constants']['e2'] = e[1]
#                         # sg.materials[mid].eff_props[3]['constants']['e3'] = e[2]
#                         # for ei in e:
#                         #     pe.append(ei)
#                         # sg.materials[mid].property_elastic += e
#                         line_material += 1
#                         continue
#                     elif line_material == 3:
#                         g = list(map(float, line))
#                         consts.append(g[0])
#                         consts.append(g[1])
#                         consts.append(g[2])
#                         # sg.materials[mid].eff_props[3]['constants']['g12'] = g[0]
#                         # sg.materials[mid].eff_props[3]['constants']['g13'] = g[1]
#                         # sg.materials[mid].eff_props[3]['constants']['g23'] = g[2]
#                         # for gi in g:
#                         #     pe.append(gi)
#                         # self.materials[mid].property_elastic += g
#                         line_material += 1
#                         continue
#                     elif line_material == 4:
#                         nu = list(map(float, line))
#                         consts.append(nu[0])
#                         consts.append(nu[1])
#                         consts.append(nu[2])
#                         # sg.materials[mid].eff_props[3]['constants']['nu12'] = nu[0]
#                         # sg.materials[mid].eff_props[3]['constants']['nu13'] = nu[1]
#                         # sg.materials[mid].eff_props[3]['constants']['nu23'] = nu[2]
#                         # for nui in nu:
#                         #     pe.append(nui)
#                         # sg.materials[mid].property_elastic.append(pe)
#                         line_material = 99
#                         continue
#                 elif mtype == 2:
#                     # anisotropic
#                     continue

#                 if line_material == 99:
#                     mp.assignConstants(consts)
#                     sg.materials[mid] = mp
#                     line_material = 0
#                     count_material += 1  # next material
#                     continue
#                 continue
#             else:
#                 # omega
#                 sg.omega = float(line[0])

#     return sg




def readSCOutBeamProperty(fn, scrnout=True):
    """Read SwiftComp homogenization results

    Parameters
    ----------
    fn : str
        SwiftComp output file name (e.g. example.sg.k).
    scrnout : bool, default True
        Switch of printing cmd output.

    Returns
    -------
    msgpi.sg.BeamProperty
        Material/sectional properties.
    """
    # if logger is None:
    #     logger = mul.initLogger(__name__)

    # sm = mms.MaterialSection(smdim = 1)
    bp = mmbm.BeamProperty()

    linesRead = []
    keywordsIndex = {}


    with open(fn, 'r') as fin:
        ln = -1
        for line in fin:

            line = line.strip()

            if len(line) > 0:
                linesRead.append(line)
                ln += 1
            else:
                continue

            if '-----' in line:
                continue


            # Inertial properties
            # -------------------

            elif 'Effective Mass Matrix' in line:
                keywordsIndex['mass'] = ln
            elif 'Mass Center Location' in line:
                keywordsIndex['mc'] = ln
            elif 'Mass per unit span' in line:
                bp.mu = float(line.split()[-1])
            elif 'i11' in line:
                bp.i11 = float(line.split()[-1])
            elif 'i22' in line:
                bp.i22 = float(line.split()[-1])
            elif 'i33' in line:
                bp.i33 = float(line.split()[-1])
            elif 'principal inertial axes rotated' in line:
                line = line.split()
                tmp_id = line.index('degrees')
                bp.phi_pia = float(line[tmp_id - 1])
            elif 'Mass-Weighted Radius of Gyration' in line:
                bp.rg = float(line.split()[-1])


            # Structural properties
            # ---------------------

            elif 'Effective Stiffness Matrix' in line:
                keywordsIndex['csm'] = ln
            elif 'Effective Compliance Matrix' in line:
                keywordsIndex['cfm'] = ln

            elif 'Tension Center Location' in line:
                keywordsIndex['tc'] = ln
            elif 'extension stiffness EA' in line:
                bp.ea = float(line.split()[-1])
            elif 'torsional stiffness GJ' in line:
                bp.gj = float(line.split()[-1])
            elif 'Principal bending stiffness EI22' in line:
                bp.ei22 = float(line.split()[-1])
            elif 'Principal bending stiffness EI33' in line:
                bp.ei33 = float(line.split()[-1])
            elif 'principal bending axes rotated' in line:
                line = line.split()
                tmp_id = line.index('degrees')
                bp.phi_pba = float(line[tmp_id - 1])

            elif 'Timoshenko Stiffness Matrix' in line:
                keywordsIndex['tsm'] = ln
            elif 'Timoshenko Compliance Matrix' in line:
                keywordsIndex['tfm'] = ln

            elif 'Shear Center Location' in line:
                keywordsIndex['sc'] = ln
            elif 'Principal shear stiffness GA22' in line:
                bp.ga22 = float(line.split()[-1])
            elif 'Principal shear stiffness GA33' in line:
                bp.ga33 = float(line.split()[-1])
            elif 'principal shear axes rotated' in line:
                line = line.split()
                tmp_id = line.index('degrees')
                bp.phi_psa = float(line[tmp_id - 1])


    ln = keywordsIndex['mass']
    bp.mass = sui.textToMatrix(linesRead[ln + 2:ln + 8])

    #check whether the analysis is Vlasov or timoshenko
    #Read stiffness matrix and compliance matrix
    if 'vsm' in keywordsIndex.keys():
        pass

    else:
        try:
            ln = keywordsIndex['csm']
            bp.stff = sui.textToMatrix(linesRead[ln + 2:ln + 6])
        except KeyError:
            if scrnout:
                print('No classical stiffness matrix found.')
            else:
                pass

        try:
            ln = keywordsIndex['cfm']
            bp.cmpl = sui.textToMatrix(linesRead[ln + 2:ln + 6])
        except KeyError:
            if scrnout:
                print('No classical flexibility matrix found.')
            else:
                pass

        try:
            ln = keywordsIndex['tsm']
            bp.stff_t = sui.textToMatrix(linesRead[ln + 2:ln + 8])
        except KeyError:
            if scrnout:
                print('No Timoshenko stiffness matrix found.')
            else:
                pass
        try:
            ln = keywordsIndex['tfm']
            bp.cmpl_t = sui.textToMatrix(linesRead[ln + 2:ln + 8])
        except KeyError:
            if scrnout:
                print('No Timoshenko flexibility matrix found.')
            else:
                pass          

        if 'tc' in keywordsIndex.keys():
            ln = keywordsIndex['tc']
            bp.xt2, bp.xt3 = list(map(float, linesRead[ln + 2].split()))
        if 'sc' in keywordsIndex.keys():
            ln = keywordsIndex['sc']
            bp.xs2, bp.xs3 = list(map(float, linesRead[ln + 2].split()))
        if 'mc' in keywordsIndex.keys():
            ln = keywordsIndex['mc']
            bp.xm2, bp.xm3 = list(map(float, linesRead[ln + 2].split()))


    return bp




def readSCOutShellProperty(fn, scrnout=True):
    # if logger is None:
    #     logger = mul.initLogger(__name__)

    # sm = mms.MaterialSection(smdim = 1)
    sp = mmps.ShellProperty()

    linesRead = []
    keywordsIndex = {}

    with open(fn, 'r') as fin:
        ln = -1
        prop_plane = None
        for line in fin:

            line = line.strip()

            if len(line) > 0:
                linesRead.append(line)
                ln += 1
            else:
                continue

            if '-----' in line:
                continue

            # Inertial properties
            # -------------------

            elif 'Effective Mass Matrix' in line:
                keywordsIndex['mass'] = ln
            elif 'Mass Center Location' in line:
                sp.xm3 = float(line.split()[-1])
            elif 'i11' in line:
                sp.i11 = float(line.split()[-1])
                sp.i22 = sp.i11


            # Structural properties
            # ---------------------

            elif 'Effective Stiffness Matrix' in line:
                keywordsIndex['stff'] = ln
            elif 'Effective Compliance Matrix' in line:
                keywordsIndex['cmpl'] = ln

            elif 'Geometric Correction to the Stiffness Matrix' in line:
                keywordsIndex['geo_to_stff'] = ln
            elif 'Total Stiffness Matrix after Geometric Correction' in line:
                keywordsIndex['stff_geo'] = ln

            elif 'In-Plane' in line:
                prop_plane = 'in'
            elif 'Flexural' in line:
                prop_plane = 'out'

            elif 'E1' in line:
                if prop_plane == 'in':
                    sp.e1_i = float(line.split('=')[-1])
                elif prop_plane == 'out':
                    sp.e1_o = float(line.split('=')[-1])
            elif 'E2' in line:
                if prop_plane == 'in':
                    sp.e2_i = float(line.split('=')[-1])
                elif prop_plane == 'out':
                    sp.e2_o = float(line.split('=')[-1])
            elif 'G12' in line:
                if prop_plane == 'in':
                    sp.g12_i = float(line.split('=')[-1])
                elif prop_plane == 'out':
                    sp.g12_o = float(line.split('=')[-1])
            elif 'nu12' in line:
                if prop_plane == 'in':
                    sp.nu12_i = float(line.split('=')[-1])
                elif prop_plane == 'out':
                    sp.nu12_o = float(line.split('=')[-1])
            elif 'eta121' in line:
                if prop_plane == 'in':
                    sp.eta121_i = float(line.split('=')[-1])
                elif prop_plane == 'out':
                    sp.eta121_o = float(line.split('=')[-1])
            elif 'eta122' in line:
                if prop_plane == 'in':
                    sp.eta122_i = float(line.split('=')[-1])
                elif prop_plane == 'out':
                    sp.eta122_o = float(line.split('=')[-1])

            # Thermal properties
            # ---------------------

            elif 'N11T' in line:
                sp.n11_t = float(line.split('=')[-1])
            elif 'N22T' in line:
                sp.n22_t = float(line.split('=')[-1])
            elif 'N12T' in line:
                sp.n12_t = float(line.split('=')[-1])
            elif 'M11T' in line:
                sp.m11_t = float(line.split('=')[-1])
            elif 'M22T' in line:
                sp.m22_t = float(line.split('=')[-1])
            elif 'M12T' in line:
                sp.m12_t = float(line.split('=')[-1])

    try:
        ln = keywordsIndex['mass']
        sp.mass = sui.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        if scrnout:
            print('No mass matrix found.')
        else:
            pass

    try:
        ln = keywordsIndex['stff']
        sp.stff = sui.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        if scrnout:
            print('No classical stiffness matrix found.')
        else:
            pass

    try:
        ln = keywordsIndex['cmpl']
        sp.cmpl = sui.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        if scrnout:
            print('No classical flexibility matrix found.')
        else:
            pass

    try:
        ln = keywordsIndex['geo_to_stff']
        sp.geo_correction_stff = sui.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        if scrnout:
            print('No geometric correction matrix found.')
        else:
            pass

    try:
        ln = keywordsIndex['stff_geo']
        sp.stff_geo = sui.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        if scrnout:
            print('No geometric corrected stiffness matrix found.')
        else:
            pass


    return sp









def readSCOutMaterialProperty(fn, scrnout=True):
    r"""
    """
    # if logger is None:
    #     logger = mul.initLogger(__name__)

    mp = mmsd.MaterialProperty()

    linesRead = []
    keywordsIndex = {}

    with open(fn, 'r') as fin:
        ln = -1

        for line in fin:

            line = line.strip()

            if len(line) > 0:
                linesRead.append(line)
                ln += 1
            else:
                continue

            if '-----' in line:
                continue

            if 'The Effective Stiffness Matrix' in line:
                keywordsIndex['stff'] = ln
            if 'The Effective Compliance Matrix' in line:
                keywordsIndex['cmpl'] = ln
            if 'The Engineering Constants' in line:
                keywordsIndex['const'] = ln
            if 'Effective Density' in line:
                keywordsIndex['density'] = ln

            # Thermal properties
            # ---------------------

            elif 'alpha11' in line:
                _a11 = float(line.split('=')[-1])
            elif 'alpha22' in line:
                _a22 = float(line.split('=')[-1])
            elif 'alpha33' in line:
                _a33 = float(line.split('=')[-1])
            elif '2alpha23' in line:
                _2a23 = float(line.split('=')[-1])
            elif '2alpha13' in line:
                _2a13 = float(line.split('=')[-1])
            elif '2alpha12' in line:
                _2a12 = float(line.split('=')[-1])
                mp.cte = [_a11, _a22, _a33, _2a23, _2a13, _2a12]

            elif 'Dthetatheta' in line:
                mp.d_thetatheta = float(line.split('=')[-1])
            elif 'Feff' in line:
                mp.f_eff = float(line.split('=')[-1])
                _t1 = 0
                _tm = 1
                _t = _t1 + _tm
                mp.specific_heat = mp.d_thetatheta - _t * mp.f_eff

    try:
        ln = keywordsIndex['stff']
        mp.stff = sui.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        if scrnout:
            print('No classical stiffness matrix found.')
        else:
            pass

    try:
        ln = keywordsIndex['cmpl']
        mp.cmpl = sui.textToMatrix(linesRead[ln + 2:ln + 8])
    except KeyError:
        if scrnout:
            print('No classical flexibility matrix found.')
        else:
            pass

    try:
        ln = keywordsIndex['const']
        for line in linesRead[ln + 2:ln + 11]:
            line = line.strip()
            line = line.split('=')
            label = line[0].strip().lower()
            value = float(line[-1].strip())
            mp.constants[label] = value
    except KeyError:
        print('No engineering constants found.')

    line = linesRead[keywordsIndex['density']]
    line = line.strip().split('=')
    mp.density = float(line[-1].strip())


    return mp









def readSCOutHomo(fn, smdim, scrnout=True):
    """Read SwiftComp homogenization results.

    :param fn: SwiftComp output file (e.g. example.sg.k)
    :type fn: string

    :param smdim: Dimension of the structural model
    :type smdim: int
    """
    # if logger is None:
    #     logger = mul.initLogger(__name__)

    if smdim == 1:
        out = readSCOutBeamProperty(fn, scrnout)
    elif smdim == 2:
        out = readSCOutShellProperty(fn, scrnout)
    elif smdim == 3:
        out = readSCOutMaterialProperty(fn, scrnout)


    return out









def readSCOutFailure(fn_sc_out_fi, failure_analysis):
    r"""
    """
    # if not logger:
    #     logger = mul.initLogger(__name__)

    logger.info('reading sc failure analysis ({}) output file: {}...'.format(failure_analysis, fn_sc_out_fi))

    lines = []
    kw_index = {}
    results = []
    with open(fn_sc_out_fi, 'r') as fin:
        for i, line in enumerate(fin):
            lines.append(line)
            if failure_analysis == 'f':
                # initial failue strength
                if 'Initial Failure Strengths' in line:
                    kw_index['Initial Failure Strengths'] = i
            elif failure_analysis == 'fe':
                # initial failure envelope
                pass
            elif failure_analysis == 'fi':
                # initial failure indices and strength ratios
                pass

    if failure_analysis == 'f':
        # initial failure strength
        try:
            index = kw_index['Initial Failure Strengths']
            for line in lines[index + 2:index + 8]:
                line = line.strip().split()
                results.append(list(map(float, line[:2])))
        except KeyError:
            print('No initial failure strength found.')

    elif failure_analysis == 'fe':
        # initial failure envelope
        for line in lines:
            line = line.strip().split()
            results.append([int(line[0]), float(line[1]), float(line[2])])

    elif failure_analysis == 'fi':
        # initial failure indices and strength ratios
        eids = []
        fis = []
        srs = []
        for line in lines:
            line = line.strip().split()
            # results.append([int(line[0]), float(line[1]), float(line[2])])
            eids.append(float(line[0]))
            fis.append(float(line[1]))
            srs.append(float(line[2]))
        return eids, fis, srs

    return results



















def readSCOut(fn_in, smdim, analysis=0, scrnout=True):
    r"""Read SwiftComp outputs.

    Parameters
    ----------
    fn_in : str
        SwiftComp input file name.
    smdim : int
        Dimension of the macroscopic structural model.
    analysis : {0, 2, 3, 4, 5, '', 'h', 'dl', 'd', 'l', 'fi', 'f', 'fe'}
        Analysis to be carried out.

        * 0 or 'h' or '' - homogenization
        * 2 or 'dl' or 'd' or 'l' - dehomogenization (linear)
        * 3 or 'fi' - initial failure indices and strength ratios
        * 4 or 'f' - initial failure strength
        * 5 or 'fe' - initial failure envelope
    scrnout : bool, optional
        Switch of printing solver messages., by default True

    Returns
    -------
    various
        Different analyses return different types of results.
    """
    # if not logger:
    #     logger = mul.initLogger(__name__)

    logger.info('reading sc output file (smdim={}, analysis={})...'.format(smdim, analysis))

    if analysis == 0 or analysis == 'h' or analysis == '':
        # Read homogenization results
        if not fn_in.lower()[-2:] == '.k':
            fn_in = fn_in + '.k'
        return readSCOutHomo(fn_in, smdim, scrnout)

    elif analysis == 1 or analysis == 2 or analysis == 'dl' or analysis == 'd' or analysis == 'l':
        pass

    elif (analysis.startswith('f')) or (analysis >= 3):
        return readSCOutFailure(fn_in+'.fi', analysis)



















# ====================================================================

def readSGInterfacePairs(fn):
    r"""
    """

    # if logger is None:
    #     logger = mul.initLogger(__name__)

    logger.info('reading sg interface paris: {0}...'.format(fn))

    itf_pairs = []

    with open(fn, 'r') as fobj:
        for li, line in enumerate(fobj):
            line = line.strip()
            if line == '\n' or line == '':
                continue

            line = line.split()

            _pair = [
                int(line[1]), int(line[2]),
                float(line[3]), float(line[4]),
                float(line[5]), float(line[6])
            ]

            itf_pairs.append(_pair)

    return itf_pairs









def readSGInterfaceNodes(fn):
    r"""
    """

    # if logger is None:
    #     logger = mul.initLogger(__name__)

    logger.info('reading sg interface nodes: {0}...'.format(fn))

    itf_nodes = []

    with open(fn, 'r') as fobj:
        for li, line in enumerate(fobj):
            line = line.strip()
            if line == '\n' or line == '':
                continue

            line = line.split()

            _nodes = []
            for nid in line[1:]:
                _nodes.append(int(nid))

            itf_nodes.append(_nodes)

    return itf_nodes









def readSGNodeElements(fn):
    r"""
    """

    # if logger is None:
    #     logger = mul.initLogger(__name__)

    logger.info('reading sg node elements: {0}...'.format(fn))

    node_elements = []

    with open(fn, 'r') as fobj:
        for li, line in enumerate(fobj):
            line = line.strip()
            if line == '\n' or line == '':
                continue

            line = line.split()

            _elements = []
            for eid in line[1:]:
                _elements.append(int(eid))

            node_elements.append(_elements)

    return node_elements



















# ====================================================================

def readLoadCsv(fn, delimiter=',', nhead=1, encoding='utf-8-sig'):
    r"""
    load = {
        'flight_condition_1': {
            'fx': {
                'a': [],
                'r': [],
                'v': []
            },
            'fy': [],
            'fz': [],
            'mx', [],
            'my', [],
            'mz', []
        },
        'flight_condition_2': {},
        ...
    }
    """

    load = {}
    azimuth = []

    with open(fn, 'r', encoding=encoding) as file:
        cr = csv.reader(file, delimiter=delimiter)

        for i, row in enumerate(cr):
            row = [s.strip() for s in row]
            if row[0] == '':
                continue

            if i < nhead:
                continue
                # # Read head
                # for label in row:
                #     if label.lower().startswith('rotor'):
                #         nid = int(label.split('NODE')[1])
                #         load['node_id'].append(nid)

            else:
                condition = str(row[0])
                if not condition in load.keys():
                    load[condition] = {
                        'fx': {'a': [], 'r': [], 'v': []},
                        'fy': {'a': [], 'r': [], 'v': []},
                        'fz': {'a': [], 'r': [], 'v': []},
                        'mx': {'a': [], 'r': [], 'v': []},
                        'my': {'a': [], 'r': [], 'v': []},
                        'mz': {'a': [], 'r': [], 'v': []}
                    }

                a, r, fx, fy, fz, mx, my, mz = list(map(float, row[1:]))
                v = {
                    'fx': fx, 'fy': fy, 'fz': fz,
                    'mx': mx, 'my': my, 'mz': mz
                }

                azimuth.append(a)

                for component in ['fx', 'fy', 'fz', 'mx', 'my', 'mz']:
                    load[condition][component]['a'].append(a)
                    load[condition][component]['r'].append(r)
                    load[condition][component]['v'].append(v[component])

    azimuth = list(set(azimuth))

    return load, azimuth
