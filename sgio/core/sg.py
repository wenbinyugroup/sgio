import copy
import math
import logging

# import numpy as np
import sgio.utils.io as mui
# import sgio.utils.logger as mul
import sgio.utils.version as muv

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
    def nmates(self):
        return len(self.materials)


    def __repr__(self):
        lines = [
            '',
            'SUMMARY OF THE SG',
            '=================',
            ''
            'Analysis',
            '--------',
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
            'Mesh',
            '----',
            'Number of nodes: {}'.format(self.nnodes),
            'Number of elements: {}'.format(self.nelems),
            str(self.mesh),
            '',
        ]

        lines += [
            'Materials',
            '---------',
            'Number of materials: {}'.format(self.nmates),
            '',
        ]

        lines += ['END OF SUMMARY', '']
        # print('')
        # print('SUMMARY OF THE SG')
        # print('')
        # print('Name: {0}'.format(self.name))
        # print('')
        # print('Structure gene dimension: {0}'.format(self.sgdim))
        # print('Structure model dimension: {0}'.format(self.smdim))
        # print('')
        # print('Mesh')
        # print(self.mesh)
        # print('Number of nodes: {0}'.format(len(self.nodes)))
        # print('Number of elements: {0}'.format(len(self.elements)))
        # print('')
        # print('Number of materials: {0}'.format(len(self.materials)))
        # for mid, mp in self.materials.items():
        #     print('material:', mid)
        #     mp.summary()
        #     print('')
        # print('')
        # print('Number of material-orientation combinations: {0}'.format(len(self.mocombos)))
        # print('')

        return '\n'.join(lines)









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









    def writeGmshNodes(self, fo, nid_begin=1, loc=[0, 0, 0]):
        for i in range(len(self.nodes)):
            nid = i + 1
            ncoords = copy.deepcopy(self.nodes[nid])
            fo.write('{0:8d}'.format(i+nid_begin))
            # if self.sgdim == 2:
            if self.spdim == 2:
                ncoords.insert(0, 0.0)
                ncoords = [ncoords[i] + loc[i] for i in range(3)]
            mui.writeFormatFloats(fo, ncoords)









    def writeGmshElements(self, fo, nid_begin=1, eid_begin=1):
        for i in range(len(self.elements)):
            eid = i + 1
            econnct = copy.deepcopy(self.elements[eid])
            if self.sgdim == 2:
                elem_type = 2
                if len(econnct) == 4:
                    elem_type = 3
                line = [i+eid_begin, elem_type, 2, self.elem_prop[eid], self.elem_prop[eid]]
                econnct = [nid + nid_begin - 1 for nid in econnct]
            line = line + econnct
            mui.writeFormatIntegers(fo, line)









    def writeGmshMsh(self, fo, nid_begin=1, eid_begin=1, loc=[0, 0, 0], *args, **kwargs):
        # if fn == '':
        #     fn = self.name + '.msh'

        # with open(self.fn_gmsh_msh, 'w') as fo:
        fo.write('$MeshFormat\n')
        fo.write('2.2  0  8\n')
        fo.write('$EndMeshFormat\n')
        fo.write('\n')


        # Write nodes
        fo.write('$Nodes\n')
        fo.write(str(len(self.nodes))+'\n')

        self.writeGmshNodes(fo, nid_begin, loc)

        fo.write('$EndNodes\n')
        fo.write('\n')


        # Write Elements
        fo.write('$Elements\n')
        fo.write(str(len(self.elements))+'\n')

        self.writeGmshElements(fo, nid_begin, eid_begin)

        fo.write('$EndElements\n')
        fo.write('\n')

        return









    def __writeInputSGNodes(self, f, sfi:str='8d', sff:str='16.6e'):
        ssfi = '{:' + sfi + '}'
        # count = 0
        # nnode = len(self.nodes)
        # for nid, ncoord in self.nodes.items():
        for i, ncoord in enumerate(self.mesh.points):
            # count += 1
            nid = i + 1
            # ncoord = self.nodes[nid]
            f.write(ssfi.format(nid))
            if self.sgdim == 1:
                mui.writeFormatFloats(f, ncoord[2:], fmt=sff, newline=False)
            elif self.sgdim == 2:
                mui.writeFormatFloats(f, ncoord[1:], fmt=sff, newline=False)
            elif self.sgdim == 3:
                mui.writeFormatFloats(f, ncoord, fmt=sff, newline=False)

            if i == 0:
                f.write('  # nodal coordinates')

            f.write('\n')

        f.write('\n')

        return









    def __writeInputSGElements(self, f, solver, sfi:str='8d'):
        count = 0
        for eid in self.elementids1d:
            count += 1
            # elem = np.zeros(7, dtype=int)
            elem = [0,]*7
            elem[0] = eid
            elem[1] = self.elem_prop[eid]  # mid/cid
            for i, nid in enumerate(self.elements[eid]):
                elem[i+2] = nid
            mui.writeFormatIntegers(f, elem, fmt=sfi, newline=False)
            if count == 1:
                f.write('  # element connectivity')
            f.write('\n')

        for eid in self.elementids2d:
            count += 1
            # elem = np.zeros(11, dtype=int)
            elem = [0,]*10
            elem[0] = eid
            # elem[1] = self.elem_prop[eid]
            elem_type = 'quad'
            if (len(self.elements[eid]) == 3) or (len(self.elements[eid]) == 6):
                elem_type = 'tri'
            for i, nid in enumerate(self.elements[eid]):
                if (i >= 3) and (elem_type == 'tri'):
                    elem[i+2] = nid
                else:
                    elem[i+1] = nid
            if solver.lower().startswith('s'):
                elem.insert(1, self.elem_prop[eid])
            mui.writeFormatIntegers(f, elem, fmt=sfi, newline=False)
            if count == 1:
                f.write('  # element connectivity')
            f.write('\n')

        for eid in self.elementids3d:
            count += 1
            # elem = np.zeros(22, dtype=int)
            elem = [0,]*22
            elem[0] = eid
            elem[1] = self.elem_prop[eid]
            elem_type = 'hexa'
            if (len(self.elements[eid]) == 4) or (len(self.elements[eid]) == 10):
                elem_type = 'tetra'
            for i, nid in enumerate(self.elements[eid]):
                if (i >= 4) and (elem_type == 'tetra'):
                    elem[i+3] = nid
                else:
                    elem[i+2] = nid
            mui.writeFormatIntegers(f, elem, fmt=sfi, newline=False)
            if count == 1:
                f.write('  # element connectivity')
            f.write('\n')

        f.write('\n')
        return









    def __writeInputSGElementOrientations(self, fobj, sfi, sff, solver):
        ssfi = '{:' + sfi + '}'
        ssff = '{:' + sff + '}'
        count = 0
        if solver.lower().startswith('v'):
            for eid, orient in self.elem_orient.items():
                fobj.write(ssfi.format(eid))
                fobj.write(ssfi.format(self.elem_prop[eid]))
                # theta1 = np.arctan2(orient[1][2], orient[1][1])
                theta1 = math.degrees(math.atan2(orient[1][2], orient[1][1]))
                fobj.write(ssff.format(theta1))
                fobj.write('\n')
        elif solver.lower().startswith('s'):
            for eid, orient in self.elem_orient.items():
                count += 1
                fobj.write(ssfi.format(eid))
                # mui.writeFormatFloats(fobj, np.hstack(orient))
                mui.writeFormatFloats(fobj, orient[0], sff, False)
                mui.writeFormatFloats(fobj, orient[1], sff, False)
                mui.writeFormatFloats(fobj, orient[2], sff, False)
                if count == 1:
                    fobj.write('  # element orientation')
                fobj.write('\n')
        fobj.write('\n')
        return









    def __writeInputSGMOCombos(self, fobj, sfi, sff):
        ssfi = '{:' + sfi + '}'
        ssff = '{:' + sff + '}'
        count = 0
        for cid, combo in self.mocombos.items():
            count += 1
            fobj.write((ssfi + ssfi + ssff).format(cid, combo[0], combo[1]))
            if count == 1:
                fobj.write('  # combination id, material id, in-plane rotation angle')
            fobj.write('\n')
        fobj.write('\n')
        return









    def __writeInputSGMaterials(self, fobj, sfi, sff, solver):
        for mid, m in self.materials.items():

            # print('writing material {}'.format(mid))

            if m.stff:
                anisotropy = 2
            else:
                anisotropy = m.anisotropy

            # print(m.stff)
            # print(anisotropy)

            if solver.lower().startswith('v'):
                mui.writeFormatIntegers(fobj, (mid, anisotropy), sfi)
            elif solver.lower().startswith('s'):
                mui.writeFormatIntegers(fobj, (mid, anisotropy, 1), sfi)
                mui.writeFormatFloats(fobj, (0, m.density), sff)

            # Write elastic properties
            if anisotropy == 0:
                # mpc = m.constants
                mui.writeFormatFloats(fobj, [m.e1, m.nu12], sff)

            elif anisotropy == 1:
                # mpc = m.constants
                mui.writeFormatFloats(fobj, [m.e1, m.e2, m.e3], sff)
                mui.writeFormatFloats(fobj, [m.g12, m.g13, m.g23], sff)
                mui.writeFormatFloats(fobj, [m.nu12, m.nu13, m.nu23], sff)


            elif anisotropy == 2:
                for i in range(6):
                    mui.writeFormatFloats(fobj, m.stff[i][i:], sff)
                    # for j in range(i, 6):
                    #     fobj.write(sff.format(m.stff[i][j]))
                    # fobj.write('\n')

            # print('self.physics =', self.physics)
            # print('m.cte =', m.cte)
            # print('m.specific_heat =', m.specific_heat)
            if self.physics in [1, 4, 6]:
                mui.writeFormatFloats(fobj, m.cte+[m.specific_heat,], sff)

            fobj.write('\n')

            if solver.lower().startswith('v'):
                mui.writeFormatFloats(fobj, (m.density,), sff)

        fobj.write('\n')
        return









    def __writeInputSGHeader(self, fobj, sfi, sff, solver, sg_fmt, version=None):
        ssfi = '{:' + sfi + '}'

        # VABS
        if solver.lower().startswith('v'):
            # format_flag  nlayer
            mui.writeFormatIntegers(fobj, [sg_fmt, len(self.mocombos)])
            fobj.write('\n')

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
            mui.writeFormatIntegers(
                fobj, [model, self.do_dampling, physics], sfi)
            fobj.write('\n')

            # curve_flag  oblique_flag  trapeze_flag  vlasov_flag
            line = [0, 0, trapeze, vlasov]
            if (self.initial_twist != 0.0) or (self.initial_curvature[0] != 0.0) or (self.initial_curvature[1] != 0.0):
                line[0] = 1
            if (self.oblique[0] != 1.0) or (self.oblique[1] != 0.0):
                line[1] = 1
            mui.writeFormatIntegers(fobj, line, sfi)
            fobj.write('\n')

            # k1  k2  k3
            if line[0] == 1:
                mui.writeFormatFloats(
                    fobj,
                    [self.initial_twist, self.initial_curvature[0], self.initial_curvature[1]],
                    sff
                )
                fobj.write('\n')
            
            # oblique1  oblique2
            if line[1] == 1:
                mui.writeFormatFloats(fobj, self.oblique, sff)
                fobj.write('\n')
            
            # nnode  nelem  nmate
            mui.writeFormatIntegers(
                fobj, [len(self.nodes), len(self.elements), len(self.materials)], sfi)
            fobj.write('\n')


        # SwiftComp
        elif solver.lower().startswith('s'):
            # Extra inputs for dimensionally reducible structures
            if (self.smdim == 1) or (self.smdim == 2):
                # model (0: classical, 1: shear refined)
                fobj.write(ssfi.format(self.model))
                fobj.write('  # structural model (0: classical, 1: shear refined)')
                fobj.write('\n\n')

                if self.smdim == 1:  # beam
                    # initial twist/curvatures
                    # fobj.write((sff * 3 + '\n').format(0., 0., 0.))
                    mui.writeFormatFloats(
                        fobj,
                        [self.initial_twist, self.initial_curvature[0], self.initial_curvature[1]],
                        sff, newline=False
                    )
                    fobj.write('  # initial curvatures k11, k12, k13\n')
                    fobj.write('\n')
                    # oblique cross section
                    # fobj.write((sff * 2 + '\n').format(1., 0.))
                    mui.writeFormatFloats(fobj, self.oblique, sff)

                elif self.smdim == 2:  # shell
                    # initial twist/curvatures
                    # fobj.write((sff * 2 + '\n').format(
                    #     self.initial_curvature[0], self.initial_curvature[1]
                    # ))
                    mui.writeFormatFloats(fobj, self.initial_curvature, sff, newline=False)
                    fobj.write('  # initial curvatures k12, k21\n')
                    # if self.geo_correct:
                    # if self.initial_curvature[0] != 0 or self.initial_curvature[1] != 0:
                    if version > '2.1':
                        mui.writeFormatFloats(fobj, self.lame_params, sff, newline=False)
                        fobj.write('  # Lame parameters\n')
                fobj.write('\n')

            # Head
            nums = [
                self.physics, self.ndim_degen_elem, self.use_elem_local_orient,
                self.is_temp_nonuniform
            ]
            cmt = '  # analysis, elem_flag, trans_flag, temp_flag'
            if version > '2.1':
                nums += [self.force_flag, self.steer_flag]
                cmt = cmt + ', force_flag, steer_flag'
            mui.writeFormatIntegers(fobj, nums, sfi, newline=False)
            fobj.write(cmt)
            fobj.write('\n\n')
            # fobj.write((sfi * 6 + '\n').format(
            #     self.sgdim,
            #     len(self.nodes),
            #     len(self.elements),
            #     len(self.materials),
            #     self.num_slavenodes,
            #     len(self.mocombos)
            # ))
            mui.writeFormatIntegers(fobj, [
                self.sgdim,
                len(self.nodes),
                len(self.elements),
                len(self.materials),
                self.num_slavenodes,
                len(self.mocombos)
            ], sfi, newline=False)
            fobj.write('  # nsg, nnode, nelem, nmate, nslave, nlayer')
            fobj.write('\n\n')

        return









    def __writeInputMaterialStrength(self, fobj, sfi, sff):
        for i, m in self.materials.items():
            # print(m.strength)
            # print(m.failure_criterion)
            # print(m.char_len)

            # fobj.write('{} {}'.format(m.failure_criterion, len(m.strength)))

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

            mui.writeFormatIntegers(
                fobj,
                # (m.strength['criterion'], len(m.strength['constants'])),
                [m.failure_criterion, len(strength)],
                sfi
            )
            # fobj.write((sff+'\n').format(m.strength['chara_len']))
            mui.writeFormatFloats(fobj, [m.char_len,], sff)
            # mui.writeFormatFloats(fobj, m.strength['constants'], sff[2:-1])
            mui.writeFormatFloats(fobj, strength, sff)
        return









    def __writeInputDisplacements(self, fobj, sff):
        mui.writeFormatFloats(fobj, self.global_displacements, sff[2:-1])
        mui.writeFormatFloatsMatrix(fobj, self.global_rotations, sff[2:-1])









    def __writeInputLoads(self, fobj, sfi, sff, solver):
        if solver.lower().startswith('v'):
            if self.model == 0:
                mui.writeFormatFloats(fobj, self.global_loads)
            else:
                mui.writeFormatFloats(fobj, [self.global_loads[i] for i in [0, 3, 4, 5]])
                mui.writeFormatFloats(fobj, [self.global_loads[i] for i in [1, 2]])
                fobj.write('\n')
                mui.writeFormatFloats(fobj, self.global_loads_dist[0])
                mui.writeFormatFloats(fobj, self.global_loads_dist[1])
                mui.writeFormatFloats(fobj, self.global_loads_dist[2])
                mui.writeFormatFloats(fobj, self.global_loads_dist[3])
        elif solver.lower().startswith('s'):
            # fobj.write((sfi+'\n').format(self.global_loads_type))
            for load_case in self.global_loads:
                mui.writeFormatFloats(fobj, load_case, sff)
        fobj.write('\n')
        return









    def writeInputSG(self, fn, sfi, sff, solver, sg_fmt, version=None):
        ssff = '{:' + sff + '}'
        if not version is None:
            self.version = muv.Version(version)

        logger.debug('format version: {}'.format(self.version))

        with open(fn, 'w') as fobj:
            self.__writeInputSGHeader(fobj, sfi, sff, solver, sg_fmt, version)
            self.__writeInputSGNodes(fobj, sfi, sff)
            self.__writeInputSGElements(fobj, sfi, solver)

            if self.use_elem_local_orient != 0:
                self.__writeInputSGElementOrientations(fobj, sfi, sff, solver)

            if len(self.mocombos) > 0:
                self.__writeInputSGMOCombos(fobj, sfi, sff)

            self.__writeInputSGMaterials(fobj, sfi, sff, solver)

            if solver.lower().startswith('s'):
                fobj.write((ssff + '\n').format(self.omega))
                # fobj.write('\n')

            # fobj.write('\n')









    def writeInputGlobal(self, fn, sfi, sff, solver, analysis, version=None):
        with open(fn, 'w') as fobj:
            if analysis.lower().startswith('d') or analysis.lower().startswith('l'):
                self.__writeInputDisplacements(fobj, sff)
            elif analysis.lower().startswith('f'):
                self.__writeInputMaterialStrength(fobj, sfi, sff)

            if solver.lower().startswith('s'):
                # fobj.write((sfi+'\n').format(self.global_loads_type))
                mui.writeFormatIntegers(fobj, [self.global_loads_type, ], sfi)

            if analysis != 'f':
                self.__writeInputLoads(fobj, sfi, sff, solver)


    # def writeSCInF(self, fn, sfi, sff):
    #     with open(fn, 'w') as fobj:
    #         # Addtional material properties
    #         for i, m in self.materials.items():
    #             mui.writeFormatIntegers(
    #                 fobj,
    #                 (m.strength['criterion'], len(m.strength['constants'])),
    #                 sfi[2:-1]
    #             )
    #             fobj.write((sff+'\n').format(m.strength['chara_len']))
    #             mui.writeFormatFloats(fobj, m.strength['constants'], sff[2:-1])

    #         # Load type
    #         fobj.write((sfi+'\n').format(self.global_loads_type))

    #         # (fe) Axes

    #         # (fi) Loads
    #         mui.writeFormatFloats(fobj, self.global_loads, sff[2:-1])




    def writeInput(
        self, fn, solver, analysis='h', sg_fmt=1, sfi='8d', sff='16.6e', version=None
        ):
        """Write analysis input

        Parameters
        ----------
        fn : str
            Name of the input file
        solver : {'vabs' (or 'v'), 'swfitcomp' (or 'sc', 's')}
            Solver of the analysis
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

        if analysis.lower().startswith('h'):
            self.writeInputSG(fn, sfi, sff, solver, sg_fmt, version)
        elif (analysis.lower().startswith('d')) or (analysis.lower().startswith('l')) or (analysis.lower().startswith('f')):
            self.writeInputGlobal(fn+'.glb', sfi, sff, solver, analysis, version)

        return fn


