import copy
# import math
import logging

import numpy as np
# from numpy.typing import ArrayLike

# import sgio.core.solid as scs
# import sgio.utils.io as sui
# import sgio.utils.logger as mul
# import sgio.utils.version as suv

# import meshio
# import sgio.meshio as mpm

from sgio.meshio._mesh import Mesh


logger = logging.getLogger(__name__)


class StructureGene(object):
    r"""A finite element level structure gene model in the theory of MSG.

    Parameters
    ----------
    name
        Name of the SG.
    sgdim
        Dimension of the SG.
    smdim
        Dimension of the material/structural model.
        Beam (1), plate/shell (2), 3D continuum (3).
    spdim
        Dimension of the space.
    """

    def __init__(self, name:str='', sgdim:int=None, smdim:int=None, spdim:int=None):
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

        #: dict of {int, int}: Material/Combination id for each element.
        #:
        #: `{eid: mid/cid, ...}`
        # self.elem_prop = {}
        #: dict of {int, int}: Element id for each material/combination.
        #:
        #: `{mid/cid: [eid, ...], ...}`
        # self.prop_elem = {}

        #: dict of {int, list of lists of floats}: Element local orientations.
        #:
        #: `{eid: [[a1, a2, a3], [b1, b2, b3], [c1, c2, c3]], ...}`
        # self.elem_orient = {}

        #: float: Omega (see SwiftComp manual).
        self.omega = 1

        self.itf_pairs = []
        self.itf_nodes = []
        self.node_elements = []


        # Global response
        # ------------------------------------------------------------

        #: list of floats: Global displacements.
        #:
        #: `[u1, u2, u3]`
        self.global_displacements = []
        #: list of lists floats: Global rotation matrix.
        #:
        #: `[[C11, C12, C13], [C21, C22, C23], [C31, C32, C33]]`
        self.global_rotations = []
        #: int: Global load type.
        #:
        #: * 0 - generalized stresses
        #: * 1 - generalized strains
        self.global_loads_type = 0

        self.global_loads = []
        """list of list of floats: Global loads

        ============================ ========================================== ============================================
        Model                        Generalized stresses                       Generalized strains
        ============================ ========================================== ============================================
        Continuum                    `[s11, s22, s33, s23, s13, s12]`           `[e11, e22, e33, e23, e13, e12]`
        Kirchhoff-Love plate/shell   `[N11, N22, N12, M11, M22, M12]`           `[e11, e22, 2e12, k11, k22, 2k12]`
        Reissner-Mindlin plate/shell `[N11, N22, N12, M11, M22, M12, N13, N23]` `[e11, e22, 2e12, k11, k22, 2k12, g13, g23]`
        Euler-Bernoulli beam         `[F1, M1, M2, M3]`                         `[e11, k11, k12, k13]`
        Timoshenko beam              `[F1, F2, F3, M1, M2, M3]`                 `[e11, g12, g13, k11, k12, k13]`
        ============================ ========================================== ============================================
        """

        #: list of lists of floats:
        #: Distributed loads for Timoshenko beam model (VABS only)
        self.global_loads_dist = []

        # if logger:
        #     self.logger = logger
        # else:
        #     self.logger = mul.initLogger(__name__)


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
        v = np.asarray(v)
        self.mesh.points += v
        return


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
        for i, mo in self.mocombos.items():
            if (self.materials[mo[0]].name == name) and (mo[1] == angle):
                return i
        return 0









    # def write(
    #     self, fn, file_format:str, analysis='h', sg_fmt:int=1,
    #     sfi:str='8d', sff:str='20.12e', version=None, mesh_only=False
    #     ):
    #     """Write analysis input

    #     Parameters
    #     ----------
    #     fn : str
    #         Name of the input file
    #     file_format : {'vabs' (or 'v'), 'swfitcomp' (or 'sc', 's')}
    #         file_format of the analysis
    #     analysis : {0, 1, 2, 3, '', 'h', 'dn', 'dl', 'd', 'l', 'fi'}, optional
    #         Analysis type, by default 'h'
    #     sg_fmt : {0, 1}, optional
    #         Format for the VABS input, by default 1

    #     Returns
    #     -------
    #     str
    #         Name of the input file
    #     """


    #     # string format
    #     # sfi = '8d'
    #     # sff = '16.6e'

    #     _file_format = file_format.lower()

    #     if analysis.lower().startswith('h'):
    #         self.writeInput(fn, _file_format, sfi, sff, sg_fmt, version, mesh_only)

    #     elif (analysis.lower().startswith('d')) or (analysis.lower().startswith('l')) or (analysis.lower().startswith('f')):
    #         self.writeInputGlobal(fn+'.glb', _file_format, sfi, sff, analysis, version)

    #     return fn


