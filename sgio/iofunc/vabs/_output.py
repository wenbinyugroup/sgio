from __future__ import annotations

import logging

# import sgio._global as GLOBAL
import sgio.utils as sutl
import sgio.model as smdl

logger = logging.getLogger(__name__)




# Read homogenization output


def _readOutputH(file, model_type='BM1', **kwargs):
    """Read VABS homogenization output.
    """

    model = kwargs.get('model', None)

    if model_type.upper() == 'BM1' or model_type == 1:
        return _readEulerBernoulliBeamModel(file, model)
    elif model_type.upper() == 'BM2' or model_type == 2:
        return _readTimoshenkoBeamModel(file, model)



def _readEulerBernoulliBeamModel(file, model=None):
    """
    """
    if model is None:
        model = smdl.EulerBernoulliBeamModel()

    block = ''
    line = file.readline()

    while True:
        if not line:  # EOF
            break

        line = line.strip()

        if len(line) == 0:
            line = file.readline()
            continue
        elif line.startswith('--') or line.startswith('=='):
            line = file.readline()
            continue

        elif 'Geometric Center' in line:
            for _ in range(3): line = file.readline()
            model.xg2, model.xg3 = list(map(float, line.split()))
        elif 'Area =' in line:
            model.area = float(line.split()[-1])


        # Inertial properties
        # -------------------

        elif line == 'The 6X6 Mass Matrix':
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float
                )
            model.mass = _matrix
        elif '6X6 Mass Matrix at the Mass Center' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float
                )
            model.mass_mc = _matrix
        elif 'Mass Center of the Cross' in line:
            for _ in range(3): line = file.readline()
            model.xm2, model.xm3 = list(map(float, line.split()))
        elif 'Mass per unit span' in line:
            model.mu = float(line.split()[-1])
        elif 'inertia i11' in line:
            model.i11 = float(line.split()[-1])
        elif 'inertia i22' in line:
            model.i22 = float(line.split()[-1])
        elif 'inertia i33' in line:
            model.i33 = float(line.split()[-1])
        elif 'principal inertial axes rotated' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
            except ValueError:
                line = file.readline().split()
                tmp_id = line.index('degrees')
            model.phi_pia = float(line[tmp_id - 1])
        elif 'mass-weighted radius of gyration' in line:
            model.rg = float(line.split()[-1])


        # Structural properties
        # ---------------------

        elif 'Classical Stiffness Matrix' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=4, ncols=4, number_type=float
                )
            model.stff = _matrix
        elif 'Classical Compliance Matrix' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=4, ncols=4, number_type=float
                )
            model.cmpl = _matrix

        elif 'Tension Center of the Cross' in line:
            for _ in range(3): line = file.readline()
            model.xt2, model.xt3 = list(map(float, line.split()))
        elif 'extension stiffness EA' in line:
            model.ea = float(line.split()[-1])
        elif 'torsional stiffness GJ' in line:
            model.gj = float(line.split()[-1])
        elif 'Principal bending stiffness EI22' in line:
            model.ei22 = float(line.split()[-1])
        elif 'Principal bending stiffness EI33' in line:
            model.ei33 = float(line.split()[-1])
        elif 'principal bending axes rotated' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
            except ValueError:
                # If not find the value, read the next line
                line = file.readline().split()
                tmp_id = line.index('degrees')
            model.phi_pba = float(line[tmp_id - 1])

        line = file.readline()

    return model




def _readTimoshenkoBeamModel(file, model=None):
    """
    """

    if model is None:
        model = smdl.TimoshenkoBeamModel()

    block = ''
    line = file.readline()

    while True:
        if not line:  # EOF
            break

        line = line.strip()

        if len(line) == 0:
            line = file.readline()
            continue
        elif line.startswith('--') or line.startswith('=='):
            line = file.readline()
            continue

        elif 'Geometric Center' in line:
            for _ in range(3): line = file.readline()
            model.xg2, model.xg3 = list(map(float, line.split()))
        elif 'Area =' in line:
            model.area = float(line.split()[-1])


        # Inertial properties
        # -------------------

        elif line == 'The 6X6 Mass Matrix':
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float
                )
            model.mass = _matrix
        elif '6X6 Mass Matrix at the Mass Center' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6,
                number_type=float
                )
            model.mass_mc = _matrix
        elif 'Mass Center of the Cross' in line:
            for _ in range(3): line = file.readline()
            model.xm2, model.xm3 = list(map(float, line.split()))
        elif 'Mass per unit span' in line:
            model.mu = float(line.split()[-1])
        elif 'inertia i11' in line:
            model.i11 = float(line.split()[-1])
        elif 'inertia i22' in line:
            model.i22 = float(line.split()[-1])
        elif 'inertia i33' in line:
            model.i33 = float(line.split()[-1])
        elif 'principal inertial axes rotated' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
            except ValueError:
                line = file.readline().split()
                tmp_id = line.index('degrees')
            model.phi_pia = float(line[tmp_id - 1])
        elif 'mass-weighted radius of gyration' in line:
            model.rg = float(line.split()[-1])


        # Structural properties
        # ---------------------

        elif 'Classical Stiffness Matrix' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=4, ncols=4, number_type=float
                )
            model.stff_c = _matrix
        elif 'Classical Compliance Matrix' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=4, ncols=4, number_type=float
                )
            model.cmpl_c = _matrix

        elif 'Tension Center of the Cross' in line:
            for _ in range(3): line = file.readline()
            model.xt2, model.xt3 = list(map(float, line.split()))
        elif 'extension stiffness EA' in line:
            model.ea = float(line.split()[-1])
        elif 'torsional stiffness GJ' in line:
            model.gj = float(line.split()[-1])
        elif 'Principal bending stiffness EI22' in line:
            model.ei22 = float(line.split()[-1])
        elif 'Principal bending stiffness EI33' in line:
            model.ei33 = float(line.split()[-1])
        elif 'principal bending axes rotated' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
            except ValueError:
                line = file.readline().split()
                tmp_id = line.index('degrees')
            model.phi_pba = float(line[tmp_id - 1])

        elif 'Timoshenko Stiffness Matrix' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6, number_type=float
                )
            model.stff = _matrix
        elif 'Timoshenko Compliance Matrix' in line:
            for _ in range(3): line = file.readline()
            _matrix, line = sutl.readMatrix(
                file, line, nrows=6, ncols=6, number_type=float
                )
            model.cmpl = _matrix

        elif 'Shear Center' in line:
            for _ in range(3): line = file.readline()
            model.xs2, model.xs3 = list(map(float, line.split()))
        elif 'Principal shear stiffness GA22' in line:
            model.ga22 = float(line.split()[-1])
        elif 'Principal shear stiffness GA33' in line:
            model.ga33 = float(line.split()[-1])
        elif 'principal shear axes rotated' in line:
            line = line.split()
            try:
                tmp_id = line.index('degrees')
            except ValueError:
                line = file.readline().split()
                tmp_id = line.index('degrees')
            model.phi_psa = float(line[tmp_id - 1])

        line = file.readline()

    return model

# Read dehomogenization output


def _readOutputNodeDisplacement(file):
    """Read VABS output displacement on nodes.

    Parameters
    ----------
    file:
        File object of the output file.

    Returns
    -------
    dict[int, list[float]]:
        Averaged 3D strains in the beam coordinate system.
    """

    u = {}
    for i, line in enumerate(file):
        line = line.strip()
        if line == '':
            continue

        line = line.split()
        _nid = int(line[0])
        _ui = list(map(float, line[3:6]))

        u[_nid] = _ui

    return u




def _readOutputElementStrainStressCase(file, nelem):
    """Read VABS output averaged strains and stressed on elements.

    Parameters
    ----------
    file:
        File object of the output file.
    nelem: int
        Number of elements.

    Returns
    -------
    dict[int, list[float]]:
        Averaged 3D strains in the beam coordinate system.
    dict[int, list[float]]:
        Averaged 3D stressess in the beam coordinate system.
    dict[int, list[float]]:
        Averaged 3D strains in the material coordinate system.
    dict[int, list[float]]:
        Averaged 3D stressess in the material coordinate system.
    """

    e, s, em, sm = {}, {}, {}, {}
    i = 0
    while i < nelem:
        line = file.readline().strip()
        if line == '':
            continue

        line = line.split()
        _eid = int(line[0])
        _ei = list(map(float, line[1:7]))
        _si = list(map(float, line[7:13]))
        _emi = list(map(float, line[13:19]))
        _smi = list(map(float, line[19:]))

        e[_eid] = _ei
        s[_eid] = _si
        em[_eid] = _emi
        sm[_eid] = _smi

        i += 1

    return e, s, em, sm




# Read failure analysis output


def _readOutputFailureIndexCase(file, nelem):
    """Read VABS output initial failure indices and strength ratios for elements.

    Parameters
    ----------
    file:
        File object of the output file.

    Returns
    -------
    dict[int, list[float]]:
        Initial failure index and strength ratio for each element.
    list[int]:
        ID of elemnets having the lowest strength ratio.
    """

    fi = {}
    sr = {}
    eids_sr_min = []

    i = 0
    while i <= nelem:
        line = file.readline().strip()
        if line == '':
            continue

        # Read the initial failure indices and strength ratios
        if i < nelem:
            line = line.split()
            if len(line) == 3:
                fi[int(line[0])] = float(line[1])
                sr[int(line[0])] = float(line[2])

        # Read the last line of sectional strength ratio
        elif i == nelem:
            line = line.split()
            try:
                _eid = int(line[-1])
            except ValueError:
                line = file.readline().split()
                _eid = int(line[0])

            eids_sr_min.append(_eid)

        i += 1

    return fi, sr, eids_sr_min


