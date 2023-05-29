import csv

import logging

from sgio.core.sg import StructureGene

import sgio.io._swiftcomp as _swiftcomp
import sgio.io._vabs as _vabs


logger = logging.getLogger(__name__)

def read(fn:str, file_format:str, format_version:str, smdim:int, sg:StructureGene=None):
    """Read SG input.

    Parameters
    ----------
    fn : str
        Name of the SG input file
    file_format : str
        Format of the SG input file
    smdim : int
        Dimension of the macro structural model
    """

    if file_format.lower() in ['vabs', 'sc', 'swiftcomp']:
        with open(fn, 'r') as file:
            if file_format.startswith('s'):
                sg = _swiftcomp.readInputBuffer(file, format_version, smdim)
            elif file_format.startswith('v'):
                sg = _vabs.readBuffer(file, file_format, format_version, smdim)

    else:
        if not sg:
            sg = StructureGene()
        sg.mesh = read(fn, file_format)

    return sg




def readOutput(fn:str, file_format:str, analysis=0, smdim:int=1, sg:StructureGene=None):
    # print('fn =', fn)
    # print('file_format =', file_format)
    # print('smdim =', smdim)
    # print('analysis =', analysis)
    with open(fn, 'r') as file:
        if file_format.startswith('s'):
            return _swiftcomp.readOutputBuffer(file, analysis, smdim, sg)

        elif file_format.startswith('v'):
            return _vabs.readOutput(file, analysis, sg)

    return




def write(
    sg:StructureGene, fn:str, file_format:str, analysis='h', sg_fmt:int=1,
    sfi:str='8d', sff:str='20.12e', version=None, mesh_only=False
    ):
    """Write analysis input

    Parameters
    ----------
    fn : str
        Name of the input file
    file_format : {'vabs' (or 'v'), 'swfitcomp' (or 'sc', 's')}
        file_format of the analysis
    analysis : {0, 1, 2, 3, '', 'h', 'dn', 'dl', 'd', 'l', 'fi'}, optional
        Analysis type, by default 'h'
    sg_fmt : {0, 1}, optional
        Format for the VABS input, by default 1

    Returns
    -------
    str
        Name of the input file
    """

    _file_format = file_format.lower()

    with open(fn, 'w', encoding='utf-8') as file:
        if mesh_only:
            sg.mesh.write(
                file, file_format, sgdim=sg.sgdim,
                int_fmt=sfi, float_fmt=sff)

        else:
            if _file_format.startswith('s'):
                _swiftcomp.writeBuffer(sg, file, file_format, analysis, sg_fmt, sfi, sff, version, mesh_only)

            elif _file_format.startswith('v'):
                _vabs.readOutput(file, analysis, sg)

    return fn




# def readVABSOut(fn_in, analysis=0, scrnout=True):
#     """Read VABS outputs.

#     Parameters
#     ----------
#     fn_in : str
#         VABS input file name.
#     analysis : {0, 1, 2, 3, '', 'h', 'dn', 'dl', 'd', 'l', 'fi'}
#         Analysis to be carried out.

#         * 0 or 'h' or '' - homogenization
#         * 1 or 'dn' - dehomogenization (nonlinear)
#         * 2 or 'dl' or 'd' or 'l' - dehomogenization (linear)
#         * 3 or 'fi' - initial failure indices and strength ratios
#     scrnout : bool, optional
#         Switch of printing solver messages, by default True.

#     Returns
#     -------
#     various
#         Different analyses return different types of results.
#     """
#     if analysis == 0 or analysis == 'h' or analysis == '':
#         # Read homogenization results
#         if not fn_in.lower()[-2:] == '.k':
#             fn_in = fn_in + '.K'
#         return readVABSOutHomo(fn_in, scrnout)
#     elif analysis == 1 or analysis == 2 or ('d' in analysis) or analysis == 'l':
#         pass
#     elif analysis == 3 or analysis == 'fi':
#         # return readVABSOutStrengthRatio(fn_in+'.fi')
#         return readSGOutFailureIndex(fn_in+'.fi', 'vabs')









# def readSCOut(fn_in, smdim, analysis=0, scrnout=True):
#     r"""Read SwiftComp outputs.

#     Parameters
#     ----------
#     fn_in : str
#         SwiftComp input file name.
#     smdim : int
#         Dimension of the macroscopic structural model.
#     analysis : {0, 2, 3, 4, 5, '', 'h', 'dl', 'd', 'l', 'fi', 'f', 'fe'}
#         Analysis to be carried out.

#         * 0 or 'h' or '' - homogenization
#         * 2 or 'dl' or 'd' or 'l' - dehomogenization (linear)
#         * 3 or 'fi' - initial failure indices and strength ratios
#         * 4 or 'f' - initial failure strength
#         * 5 or 'fe' - initial failure envelope
#     scrnout : bool, optional
#         Switch of printing solver messages., by default True

#     Returns
#     -------
#     various
#         Different analyses return different types of results.
#     """
#     # if not logger:
#     #     logger = mul.initLogger(__name__)

#     logger.info('reading sc output file (smdim={}, analysis={})...'.format(smdim, analysis))

#     if analysis == 0 or analysis == 'h' or analysis == '':
#         # Read homogenization results
#         if not fn_in.lower()[-2:] == '.k':
#             fn_in = fn_in + '.k'
#         return readSCOutHomo(fn_in, smdim, scrnout)

#     elif analysis == 1 or analysis == 2 or analysis == 'dl' or analysis == 'd' or analysis == 'l':
#         pass

#     elif (analysis.startswith('f')) or (analysis >= 3):
#         return readSCOutFailure(fn_in+'.fi', analysis)



















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
