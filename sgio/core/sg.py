import copy
# import math
import logging

import numpy as np
# from numpy.typing import ArrayLike

# import sgio.core.solid as scs
import sgio.utils.io as sui
# import sgio.utils.logger as mul
import sgio.utils.version as suv

# import meshio
# import sgio.meshio as mpm

from sgio.meshio._mesh import Mesh


logger = logging.getLogger(__name__)


class StructureGene(object):
    r"""A finite element level structure gene model in the theory of MSG.

    Parameters
    ----------
    name : str
        Name of the SG.
    sgdim : int
        Dimension of the SG.
    smdim : int, default None
        Dimension of the material/structural model.
        Beam (1), plate/shell (2), 3D continuum (3).
    spdim : int, default None
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

        self.design = None

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
        self.do_dampling = 0

        #: int: Flag of transformation of elements
        self.use_elem_local_orient = 0
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

        #: dict of {int, list of floats}: Nodal coordinates
        #:
        #: * 3D SG: `{nid: [y1, y2, y3], ...}`
        #: * 2D SG: `{nid: [y2, y3], ...}`
        #: * 1D SG: `{nid: [y3], ...}`
        # self.nodes = {}
        #: dict of {int, list of ints}: Elemental connectivities
        #: 
        #: `{eid: [nid1, nid2, ...], ...}`, no zeros
        # self.elements = {}
        #: list of ints: Element ids
        # self.elementids = []
        #: list of ints: 1D element ids
        # self.elementids1d = []
        #: list of ints: 2D element ids
        # self.elementids2d = []
        #: list of ints: 3D element ids
        # self.elementids3d = []

        #: dict of {int, int}: Material/Combination id for each element.
        #:
        #: `{eid: mid/cid, ...}`
        self.elem_prop = {}
        #: dict of {int, int}: Element id for each material/combination.
        #:
        #: `{mid/cid: [eid, ...], ...}`
        self.prop_elem = {}

        #: dict of {int, list of lists of floats}: Element local orientations.
        #:
        #: `{eid: [[a1, a2, a3], [b1, b2, b3], [c1, c2, c3]], ...}`
        self.elem_orient = {}

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









    def write(
        self, fn, file_format:str, analysis='h', sg_fmt:int=1,
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


        # string format
        # sfi = '8d'
        # sff = '16.6e'

        _file_format = file_format.lower()

        if analysis.lower().startswith('h'):
            self.writeInput(fn, _file_format, sfi, sff, sg_fmt, version, mesh_only)

        elif (analysis.lower().startswith('d')) or (analysis.lower().startswith('l')) or (analysis.lower().startswith('f')):
            self.writeInputGlobal(fn+'.glb', _file_format, sfi, sff, analysis, version)

        return fn









    def writeInput(self, fn, file_format, sfi, sff, sg_fmt, version=None, mesh_only=False):
        """
        """

        logger.debug(f'writing sg input {fn}...')

        ssff = '{:' + sff + '}'
        if not version is None:
            self.version = suv.Version(version)

        logger.debug('format version: {}'.format(self.version))

        with open(fn, 'w') as file:
            if not mesh_only:
                self._writeHeader(file, file_format, sfi, sff, sg_fmt, version)

            self._writeMesh(file, file_format=file_format, sgdim=self.sgdim, int_fmt=sfi, float_fmt=sff)

            if not mesh_only:
                self._writeMOCombos(file, file_format, sfi, sff)

            if not mesh_only:
                self._writeMaterials(file, file_format, sfi, sff)

            if file_format.startswith('s'):
                file.write((ssff + '\n').format(self.omega))

        return









    def _writeMesh(self, file, file_format, sgdim, int_fmt, float_fmt):
        """
        """
        logger.debug('writing mesh...')

        self.mesh.write(file, file_format, sgdim=sgdim, int_fmt=int_fmt, float_fmt=float_fmt)

        return









    def _writeMOCombos(self, file, file_format, sfi, sff):
        ssfi = '{:' + sfi + '}'
        ssff = '{:' + sff + '}'
        count = 0
        for cid, combo in self.mocombos.items():
            count += 1
            file.write((ssfi + ssfi + ssff).format(cid, combo[0], combo[1]))
            if count == 1:
                file.write('  # combination id, material id, in-plane rotation angle')
            file.write('\n')
        file.write('\n')
        return









    def _writeMaterials(self, file, file_format, sfi, sff):
        """
        """

        logger.debug('writing materials...')

        counter = 0
        for mid, m in self.materials.items():

            # print('writing material {}'.format(mid))

            if m.stff:
                anisotropy = 2
            else:
                anisotropy = m.isotropy

            # print(m.stff)
            # print(anisotropy)

            if file_format.startswith('v'):
                sui.writeFormatIntegers(file, (mid, anisotropy), sfi, newline=False)
                if counter == 0:
                    file.write('  # materials')
                file.write('\n')
            elif file_format.startswith('s'):
                sui.writeFormatIntegers(file, (mid, anisotropy, 1), sfi, newline=False)
                if counter == 0:
                    file.write('  # materials')
                file.write('\n')
                sui.writeFormatFloats(file, (m.temperature, m.density), sff)

            # Write elastic properties
            if anisotropy == 0:
                # mpc = m.constants
                sui.writeFormatFloats(file, [m.e1, m.nu12], sff)

            elif anisotropy == 1:
                # mpc = m.constants
                sui.writeFormatFloats(file, [m.e1, m.e2, m.e3], sff)
                sui.writeFormatFloats(file, [m.g12, m.g13, m.g23], sff)
                sui.writeFormatFloats(file, [m.nu12, m.nu13, m.nu23], sff)


            elif anisotropy == 2:
                for i in range(6):
                    sui.writeFormatFloats(file, m.stff[i][i:], sff)
                    # for j in range(i, 6):
                    #     file.write(sff.format(m.stff[i][j]))
                    # file.write('\n')

            # print('self.physics =', self.physics)
            # print('m.cte =', m.cte)
            # print('m.specific_heat =', m.specific_heat)
            if self.physics in [1, 4, 6]:
                sui.writeFormatFloats(file, m.cte+[m.specific_heat,], sff)

            if file_format.lower().startswith('v'):
                sui.writeFormatFloats(file, (m.density,), sff)

            file.write('\n')
            
            counter += 1

        file.write('\n')
        return









    def _writeHeader(self, file, file_format, sfi, sff, sg_fmt, version=None):
        ssfi = '{:' + sfi + '}'

        # VABS
        if file_format.startswith('v'):
            # format_flag  nlayer
            sui.writeFormatIntegers(file, [sg_fmt, len(self.mocombos)])
            file.write('\n')

            # timoshenko_flag  damping_flag  thermal_flag
            model = 0
            trapeze = 0
            vlasov = 0
            if self.model == 1:
                model = 1
            elif self.model == 2:
                model = 1
                vlasov = 1
            elif self.model == 3:
                trapeze = 1
            physics = 0
            if self.physics == 1:
                physics = 3
            sui.writeFormatIntegers(
                file, [model, self.do_dampling, physics], sfi, newline=False)
            file.write('  # model_flag, damping_flag, thermal_flag\n\n')

            # curve_flag  oblique_flag  trapeze_flag  vlasov_flag
            line = [0, 0, trapeze, vlasov]
            if (self.initial_twist != 0.0) or (self.initial_curvature[0] != 0.0) or (self.initial_curvature[1] != 0.0):
                line[0] = 1
            if (self.oblique[0] != 1.0) or (self.oblique[1] != 0.0):
                line[1] = 1
            sui.writeFormatIntegers(file, line, sfi, newline=False)
            file.write('  # curve_flag, oblique_flag, trapeze_flag, vlasov_flag\n\n')

            # k1  k2  k3
            if line[0] == 1:
                sui.writeFormatFloats(
                    file,
                    [self.initial_twist, self.initial_curvature[0], self.initial_curvature[1]],
                    sff, newline=False
                )
                file.write('  # k11, k12, k13 (initial curvatures)\n\n')
            
            # oblique1  oblique2
            if line[1] == 1:
                sui.writeFormatFloats(file, self.oblique, sff, newline=False)
                file.write('  # cos11, cos21 (obliqueness)\n\n')
            
            # nnode  nelem  nmate
            sui.writeFormatIntegers(
                file, [self.nnodes, self.nelems, self.nmates], sfi, newline=False)
            file.write('  # nnode, nelem, nmate\n\n')


        # SwiftComp
        elif file_format.startswith('s'):
            # Extra inputs for dimensionally reducible structures
            if (self.smdim == 1) or (self.smdim == 2):
                # model (0: classical, 1: shear refined)
                file.write(ssfi.format(self.model))
                file.write('  # structural model (0: classical, 1: shear refined)')
                file.write('\n\n')

                if self.smdim == 1:  # beam
                    # initial twist/curvatures
                    # file.write((sff * 3 + '\n').format(0., 0., 0.))
                    sui.writeFormatFloats(
                        file,
                        [self.initial_twist, self.initial_curvature[0], self.initial_curvature[1]],
                        sff, newline=False
                    )
                    file.write('  # initial curvatures k11, k12, k13\n')
                    file.write('\n')
                    # oblique cross section
                    # file.write((sff * 2 + '\n').format(1., 0.))
                    sui.writeFormatFloats(file, self.oblique, sff)

                elif self.smdim == 2:  # shell
                    # initial twist/curvatures
                    # file.write((sff * 2 + '\n').format(
                    #     self.initial_curvature[0], self.initial_curvature[1]
                    # ))
                    sui.writeFormatFloats(file, self.initial_curvature, sff, newline=False)
                    file.write('  # initial curvatures k12, k21\n')
                    # if self.geo_correct:
                    # if self.initial_curvature[0] != 0 or self.initial_curvature[1] != 0:
                    if version > '2.1':
                        sui.writeFormatFloats(file, self.lame_params, sff, newline=False)
                        file.write('  # Lame parameters\n')
                file.write('\n')

            # Head
            nums = [
                self.physics, self.ndim_degen_elem, self.use_elem_local_orient,
                self.is_temp_nonuniform
            ]
            cmt = '  # analysis, elem_flag, trans_flag, temp_flag'
            if version > '2.1':
                nums += [self.force_flag, self.steer_flag]
                cmt = cmt + ', force_flag, steer_flag'
            sui.writeFormatIntegers(file, nums, sfi, newline=False)
            file.write(cmt)
            file.write('\n\n')
            # file.write((sfi * 6 + '\n').format(
            #     self.sgdim,
            #     len(self.nodes),
            #     len(self.elements),
            #     len(self.materials),
            #     self.num_slavenodes,
            #     len(self.mocombos)
            # ))
            sui.writeFormatIntegers(file, [
                self.sgdim,
                self.nnodes,
                self.nelems,
                self.nmates,
                self.num_slavenodes,
                len(self.mocombos)
            ], sfi, newline=False)
            file.write('  # nsg, nnode, nelem, nmate, nslave, nlayer')
            file.write('\n\n')

        return









    def _writeInputMaterialStrength(self, file, file_format, sfi, sff):
        for i, m in self.materials.items():
            # print(m.strength)
            # print(m.failure_criterion)
            # print(m.char_len)

            # file.write('{} {}'.format(m.failure_criterion, len(m.strength)))

            strength = []
            if m.type == 0:
                pass
            else:
                if m.failure_criterion == 1:
                    pass
                elif m.failure_criterion == 2:
                    pass
                elif m.failure_criterion == 3:
                    pass
                elif m.failure_criterion == 4:
                    # Tsai-Wu
                    strength = [
                        m.strength_constants['xt'], m.strength_constants['yt'], m.strength_constants['zt'],
                        m.strength_constants['xc'], m.strength_constants['yc'], m.strength_constants['zc'],
                        m.strength_constants['r'], m.strength_constants['t'], m.strength_constants['s'],
                    ]
                elif m.failure_criterion == 5:
                    pass

            sui.writeFormatIntegers(
                file,
                # (m.strength['criterion'], len(m.strength['constants'])),
                [m.failure_criterion, len(strength)],
                sfi
            )
            # file.write((sff+'\n').format(m.strength['chara_len']))
            sui.writeFormatFloats(file, [m.char_len,], sff)
            # sui.writeFormatFloats(file, m.strength['constants'], sff[2:-1])
            sui.writeFormatFloats(file, strength, sff)
        return









    def _writeInputDisplacements(self, file, file_format, sff):
        sui.writeFormatFloats(file, self.global_displacements, sff[2:-1])
        sui.writeFormatFloatsMatrix(file, self.global_rotations, sff[2:-1])









    def _writeInputLoads(self, file, file_format, sfi, sff):
        if file_format.startswith('v'):
            if self.model == 0:
                sui.writeFormatFloats(file, self.global_loads)
            else:
                sui.writeFormatFloats(file, [self.global_loads[i] for i in [0, 3, 4, 5]])
                sui.writeFormatFloats(file, [self.global_loads[i] for i in [1, 2]])
                file.write('\n')
                sui.writeFormatFloats(file, self.global_loads_dist[0])
                sui.writeFormatFloats(file, self.global_loads_dist[1])
                sui.writeFormatFloats(file, self.global_loads_dist[2])
                sui.writeFormatFloats(file, self.global_loads_dist[3])
        elif file_format.startswith('s'):
            # file.write((sfi+'\n').format(self.global_loads_type))
            for load_case in self.global_loads:
                sui.writeFormatFloats(file, load_case, sff)
        file.write('\n')
        return









    def writeInputGlobal(self, fn, file_format, sfi, sff, analysis, version=None):
        with open(fn, 'w') as file:
            if analysis.startswith('d') or analysis.lower().startswith('l'):
                self._writeInputDisplacements(file, file_format, sff)
            elif analysis.startswith('f'):
                self._writeInputMaterialStrength(file, file_format, sfi, sff)

            if file_format.startswith('s'):
                # file.write((sfi+'\n').format(self.global_loads_type))
                sui.writeFormatIntegers(file, [self.global_loads_type, ], sfi)

            if analysis != 'f':
                self._writeInputLoads(file, file_format, sfi, sff)

