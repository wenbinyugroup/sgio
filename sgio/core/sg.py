import copy
import logging

import numpy as np
import sgio._global as GLOBAL
from sgio.meshio._mesh import Mesh

# import math

# from numpy.typing import ArrayLike

# import sgio.core.solid as scs
# import sgio.utils.io as sui
# import sgio.utils.logger as mul
# import sgio.utils.version as suv

# import meshio
# import sgio.meshio as mpm


logger = logging.getLogger(GLOBAL.LOGGER_NAME)


class SGMacroModel():
    """Configuration of SG analysis, independent on the geometry.
    """
    def __init__(self, kwd='SD1'):
        self._kwd = kwd
        self._physics = 0
        self._geo_correct = False
        self._do_damping = 0
        self._is_temp_nonuniform = 0

    @property
    def smdim(self):
        if self._kwd[:2] == 'SD':
            return 3
        if self._kwd[:2] == 'PL':
            return 2
        if self._kwd[:2] == 'BM':
            return 1




class StructureGene():
    """A finite element level structure gene model in the theory of MSG.

    Parameters
    ----------
    name : str, optional
        Name of the SG.
    sgdim : int, optional
        Dimension of the SG.
    smdim : int, optional
        Dimension of the material/structural model.
        Beam (1), plate/shell (2), 3D continuum (3).
    spdim : int, optional
        Dimension of the space.
    """

    def __init__(
        self, name='', sgdim=None, smdim=None, spdim=None
        ):
        #: str: Name of the SG.
        self.name = name
        #: int: Dimension of the SG.
        self.sgdim = sgdim
        #: int: Dimension of the material/structural model.
        self.smdim = smdim
        #: int: Dimension of the space containing SG
        if not spdim:
            self.spdim = sgdim
        else:
            self.spdim = spdim

        # self.design = None

        #: int: Analysis configurations
        #:
        #: * 0 - homogenization (default)
        #: * 1 - dehomogenization/localization/recover
        #: * 2 - failure (SwiftComp only)
        self.analysis = 0

        self.fn_gmsh_msh = self.name + '.msh'  #: File name of the Gmsh mesh file

        #: int: Physics included in the analysis
        #:
        #: * 0 - elastic (default)
        #: * 1 - thermoelastic
        #: * 2 - conduction
        #: * 3 - piezoelectric/piezomagnetic
        #: * 4 - thermopiezoelectric/thermopiezomagnetic
        #: * 5 - piezoelectromagnetic
        #: * 6 - thermopiezoelectromagnetic
        self.physics = 0

        #: int: Macroscopic structural model
        #:
        #: * 0 - classical (default)
        #: * 1 - refined (e.g. generalized Timoshenko)
        #: * 2 - Vlasov model (beam only)
        #: * 3 - trapeze effect (beam only)
        self.model = 0
        self.geo_correct = False

        #: int: Flag of damping computation
        self.do_damping = 0

        #: int: Flag of transformation of elements
        # self.use_elem_local_orient = 0
        #: int: Flag of uniform temperature
        self.is_temp_nonuniform = 0

        self.force_flag = 0
        self.steer_flag = 0

        #: float: Initial twist (beam only)
        self.initial_twist = 0.0
        #: list of floats: Initial curvature
        self.initial_curvature = [0.0, 0.0]
        #: list of floats: Oblique (beam only)
        self.oblique = [1.0, 0.0]

        #: list of floats: Lame parameters for geometrically corrected shell model
        self.lame_params = [1.0, 1.0]


        # Material
        # ------------------------------------------------------------

        #: dict of {int, :obj:`msgpi.sg.MaterialProperty`}: Materials
        self.materials = {}

        #: dict of {int, list of (int, float)}: Material-orientation (deg) combinations
        #:
        #: `{cid: [mid, orientation], ...}`
        self.mocombos = {}


        # Mesh
        # ------------------------------------------------------------
        self.mesh : Mesh = None

        #: int: Flag of the type of elements (SC)
        self.ndim_degen_elem = 0
        #: int: Number of slave nodes
        self.num_slavenodes = 0


        #: float: Omega (see SwiftComp manual).
        self.omega = 1

        self.itf_pairs = []
        self.itf_nodes = []
        self.node_elements = []



    @property
    def nnodes(self):
        return len(self.mesh.points)

    @property
    def nelems(self):
        return sum([len(cell.data) for cell in self.mesh.cells])

    @property
    def nma_combs(self):
        return len(self.mocombos)

    @property
    def nmates(self):
        return len(self.materials)

    @property
    def use_elem_local_orient(self):
        if 'property_ref_csys' in self.mesh.cell_data.keys():
            return 1
        else:
            return 0


    def __repr__(self):
        lines = [
            '',
            '='*40,
            'SUMMARY OF THE SG',
            ''
            '-'*30,
            'ANALYSIS',
            'Structure gene: {}D -> model: {}D'.format(self.sgdim, self.smdim),
            'Physics: {}'.format(self.physics),
            '',
        ]

        if self.smdim != 3:
            lines += [
                'Model: {}'.format(self.model),
            ]
            lines.append('')

        lines += [
            '-'*30,
            'MESH',
            'Number of nodes: {}'.format(self.nnodes),
            'Number of elements: {}'.format(self.nelems),
            str(self.mesh),
            '',
        ]

        lines += [
            '-'*30,
            'MATERIALS',
            'Number of materials: {}'.format(self.nmates),
            '',
        ]

        lines += ['END OF SUMMARY', '='*40, '']

        return '\n'.join(lines)


    def copy(self):
        return copy.deepcopy(self)
    


    def translate(self, v):
        if self.mesh is None:
            raise ValueError('Mesh is not defined.')
        v = np.asarray(v)
        self.mesh.points += v


    def findMaterialByName(self, name):
        """Find material by name.

        Parameters
        ----------
        name : str
            Material name.

        Returns
        -------
        int
            Material id. 0 if not found.
        """
        # print(self.materials)
        for i, m in self.materials.items():
            if m.name == name:
                return i
        return 0


    def findComboByMaterialOrientation(self, name, angle):
        """Find material-orientation combination.

        Parameters
        ----------
        name : str
            Material name.
        angle : float
            Orientation angle.

        Returns
        -------
        int
            Combination id. 0 if not found.
        """
        # print(f'findComboByMaterialOrientation: {name}, {angle}')
        for i, mo in self.mocombos.items():
            # print(f'  {i}, {mo}')
            # print(f'  {self.materials[mo[0]].name}, {mo[1]}')
            if (self.materials[mo[0]].name == name) and (mo[1] == angle):
                # print(f'  found: {i}')
                return i
        # print('  not found')
        return 0


