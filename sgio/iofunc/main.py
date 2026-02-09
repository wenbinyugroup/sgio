from __future__ import annotations

import csv
import logging
import meshio
from meshio import Mesh


import sgio._global as GLOBAL
import sgio.iofunc._meshio as _meshio
import sgio.iofunc.abaqus as _abaqus
import sgio.iofunc.gmsh as _gmsh
import sgio.iofunc.swiftcomp as _swiftcomp
import sgio.iofunc.vabs as _vabs
import sgio.model as sgmodel
from sgio.core import (
	    StructureGene,
	)
from sgio.core.numbering import ensure_node_ids
from sgio.utils import (
	    readNextNonEmptyLine,
	)
# Import utility functions from refactored modules
from .utils import (
    readLoadCsv,
    readSGInterfacePairs,
    readSGInterfaceNodes,
)

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION: Mesh Conversion Functions
# ============================================================================


def _mesh_to_sg(mesh: Mesh, sgdim: int = 3, model_type: str = 'SD1') -> StructureGene:
    """Convert a meshio Mesh object to a StructureGene object.

    Parameters
    ----------
    mesh : meshio.Mesh
        The mesh object to convert.
    sgdim : int
        Dimension of the structure gene geometry.
    model_type : str
        Type of the macro structural model.

    Returns
    -------
    StructureGene
        The structure gene object.
    """
    import numpy as np

    sg = StructureGene()
    sg.sgdim = sgdim

    if isinstance(model_type, int):
        smdim = model_type
        _submodel = model_type
    elif isinstance(model_type, str):
        if model_type.upper()[:2] == 'SD':
            smdim = 3
        elif model_type.upper()[:2] == 'PL':
            smdim = 2
        elif model_type.upper()[:2] == 'BM':
            smdim = 1
        else:
            smdim = 3
        try:
            _submodel = int(model_type[2]) - 1
        except (IndexError, ValueError):
            _submodel = 0
    else:
        smdim = 3
        _submodel = 0

    sg.smdim = smdim
    sg.model = _submodel
    sg.mesh = mesh

    # Ensure node_id point_data exists (e.g., for gmsh/meshio readers)
    ensure_node_ids(mesh)

    # Ensure element_id cell_data exists (generate if missing)
    if 'element_id' not in mesh.cell_data:
        element_id = []
        elem_idx = 0
        for cell_block in mesh.cells:
            block_ids = list(range(elem_idx + 1, elem_idx + 1 + len(cell_block.data)))
            element_id.append(np.array(block_ids, dtype=int))
            elem_idx += len(cell_block.data)
        mesh.cell_data['element_id'] = element_id

    # Ensure property_id cell_data exists (use gmsh:physical or gmsh:geometrical if available)
    if 'property_id' not in mesh.cell_data:
        if 'gmsh:physical' in mesh.cell_data:
            mesh.cell_data['property_id'] = [
                np.array(arr, dtype=int) for arr in mesh.cell_data['gmsh:physical']
            ]
        elif 'gmsh:geometrical' in mesh.cell_data:
            mesh.cell_data['property_id'] = [
                np.array(arr, dtype=int) for arr in mesh.cell_data['gmsh:geometrical']
            ]
        else:
            # Default property_id to 1
            property_id = []
            for cell_block in mesh.cells:
                property_id.append(np.ones(len(cell_block.data), dtype=int))
            mesh.cell_data['property_id'] = property_id

    # Extract material name-ID pairs from Gmsh PhysicalNames (field_data)
    # field_data format: {'name': [physical_id, dimension], ...}
    if hasattr(mesh, 'field_data') and mesh.field_data:
        for name, (phys_id, dim) in mesh.field_data.items():
            # Only store relevant dimension physical names as materials
            # For 3D SG, use 3D physicals; for 2D SG, use 2D physicals, etc.
            if dim == sgdim:
                sg.add_material_name_id_pair(name, phys_id)

    # Process property_id from cell_data
    if 'property_id' in mesh.cell_data:
        # Create mocombos from unique property_ids
        property_ids = set()
        for prop_block in mesh.cell_data['property_id']:
            for prop_id in prop_block:
                if prop_id is not None:
                    property_ids.add(int(prop_id))

        for prop_id in property_ids:
            if prop_id not in sg.mocombos:
                # Check if we have a name from PhysicalNames
                mat_name = sg.get_material_name_by_id(prop_id)
                if mat_name is None:
                    # No PhysicalName found, use default naming
                    mat_name = f'Material_{prop_id}'
                    sg.add_material_name_id_pair(mat_name, prop_id)
                
                if mat_name not in sg.materials:
                    # Create a default material placeholder with basic properties
                    import sgio.model.solid as smdl
                    mat = smdl.CauchyContinuumModel(name=mat_name)
                    # Set default isotropic properties to avoid None values
                    mat.set('isotropy', 0)
                    mat.set('elastic', [200e9, 0.3])  # Default steel-like properties
                    sg.materials[mat_name] = mat
                sg.mocombos[prop_id] = (mat_name, 0.0)  # (material_name, angle)

    return sg



# ============================================================================
# SECTION: Input Reading Functions
# ============================================================================

def read(
    filename: str,
    file_format: str,
    model_type: str = 'SD1',
    format_version: str = '',
    sgdim: int = 3,
    sg: StructureGene = None,
    **kwargs
) -> StructureGene:
    """Read SG data file.

    Parameters
    ----------
    filename : str
        Name of the SG data file
    file_format : str
        Format of the SG data file.
        Choose one from 'abaqus', 'vabs', 'sc', 'swiftcomp'.
    model_type : str
        Type of the macro structural model.
        Choose one from

        * 'SD1': Cauchy continuum model
        * 'PL1': Kirchhoff-Love plate/shell model
        * 'PL2': Reissner-Mindlin plate/shell model
        * 'BM1': Euler-Bernoulli beam model
        * 'BM2': Timoshenko beam model
    format_version : str
        Version of the format
    sgdim : int
        Dimension of the geometry. Default is 3.
        Choose one from 1, 2, 3.
    sg : :obj:`sgio.core.sg.StructureGene`, optional
        Structure gene object

    Returns
    -------
    :obj:`sgio.core.sg.StructureGene`
        Structure gene object
    """
    logger.info('Reading file...')
    logger.debug(locals())

    # sutils.check_file_exists(filename)
    file_format = file_format.lower()
    if file_format == 'sc' or file_format == 'swiftcomp':
        with open(filename, 'r') as file:
            sg = _swiftcomp.read_input_buffer(
                file, format_version, model_type
            )
    elif file_format == 'vabs':
        with open(filename, 'r') as file:
            sg = _vabs.read_buffer(
                file, format_version
            )
    elif file_format == 'abaqus':
        # with open(filename, 'r') as file:
        sg = _abaqus.read(
            filename, sgdim=sgdim, model=model_type
        )
    elif file_format == 'gmsh':
        with open(filename, 'rb') as file:
            mesh = _gmsh.read_buffer(file, format_version=format_version)
        sg = _mesh_to_sg(mesh, sgdim=sgdim, model_type=model_type)
    else:
        raise ValueError(f"Unknown file format: {file_format}")

    if not sg:
        sg = StructureGene(sgdim=sgdim, smdim=model_type)
    if not sg.mesh:
        sg.mesh, _, _ = _meshio.read(filename, file_format)

    return sg




def readOutputModel(
    filename: str, file_format: str, model_type: str = "", sg: StructureGene = None,
    **kwargs
):
    """Read SG homogenization output file.

    Parameters
    ----------
    filename : str
        Name of the SG analysis output file
    file_format : str
        Format of the SG data file.
        Choose one from 'vabs', 'sc', 'swiftcomp'.
    model_type : str
        Type of the macro structural model.
        Choose one from

        * 'SD1': Cauchy continuum model
        * 'PL1': Kirchhoff-Love plate/shell model
        * 'PL2': Reissner-Mindlin plate/shell model
        * 'BM1': Euler-Bernoulli beam model
        * 'BM2': Timoshenko beam model
    sg : StructureGene, optional
        SG object.

    Returns
    -------
    Model
        If `analysis` is 'h', return the consitutive model.
    """

    model = None
    try:
        with open(filename, "r") as file:
            if file_format.lower().startswith("s"):
                model = _swiftcomp.read_output_buffer(
                    file, analysis="h", model_type=model_type, sg=sg, **kwargs
                )
            elif file_format.lower().startswith("v"):
                model = _vabs.read_output_buffer(
                    file, analysis="h", sg=sg, model_type=model_type, **kwargs
                )
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
    except Exception as e:
        logger.error(f"Error: {e}")

    return model




def readOutputState(
    filename:str, file_format:str, analysis:str, model_type:str="",
    extension:str="ele", sg:StructureGene=None, tool_version:str="",
    num_cases:int=1, num_elements:int=0, output_format:int=0, **kwargs
    ):
    """Read SG dehomogenization or failure analysis output.

    Parameters
    ----------
    filename : str
        Name of the SG analysis output file
    file_format : str
        Format of the SG data file.
        Choose one from 'vabs', 'sc', 'swiftcomp'.
    analysis : str
        Indicator of SG analysis.
        Choose one from

        * 'd' or 'l': Dehomogenization
        * 'fi': Initial failure indices and strength ratios
    model_type : str
        Type of the macro structural model.
        Choose one from

        * 'SD1': Cauchy continuum model
        * 'PL1': Kirchhoff-Love plate/shell model
        * 'PL2': Reissner-Mindlin plate/shell model
        * 'BM1': Euler-Bernoulli beam model
        * 'BM2': Timoshenko beam model
    extension : str or list of str
        Extension of the output data.
        Default is 'ele'.
        Include one or more of the following keywords:

        * 'u': Displacement
        * 'ele': Element strain and stress
    sg : StructureGene
        Structure gene object
    tool_version : str
        Version of the tool
    num_cases : int
        Number of load cases
    num_elements : int
        Number of elements
    output_format : int
        Format of the output file. Choose one from

        * 0 - Native format
        * 1 - Gmsh format

    Returns
    -------
    StateCase
        State case object
    """
    logger.debug('reading output state...')
    logger.debug(locals())

    state_cases = [sgmodel.StateCase({}, {}) for _ in range(num_cases)]

    if analysis == "fi":
        # Read failure index
        if file_format.lower().startswith("s"):
            with open(f"{filename}.fi", "r") as file:
                return _swiftcomp.read_output_buffer(
                    file, analysis=analysis, model_type=model_type, **kwargs
                )

        elif file_format.lower().startswith("v"):
            if num_elements == 0:
                num_elements = sg.nelems

            with open(f"{filename}.fi", "r") as file:

                for i_case in range(num_cases):
                    # print(f'i_case: {i_case}')

                    state_case = state_cases[i_case]

                    try:
                        # fi, sr, eids_sr_min = _vabs.read_output_buffer(
                        #     file, analysis, sg, tool_version=tool_version,
                        #     num_cases=num_cases, num_elements=num_elements, **kwargs
                        # )
                        if float(tool_version) > 4:
                            line = file.readline()  # skip the first line
                            while line.strip() == '':
                                line = file.readline()
                            print(f'line: {line}')
                        fi, sr, eids_sr_min = _vabs._readOutputFailureIndexCase(
                            file, num_elements
                        )

                    except Exception as e:
                        logger.error(f"Error: {e}")
                        return None

                    if fi is None or sr is None:
                        logger.error("Error: No data read")
                        return None

                    state_case.addState(
                        name="fi", state=sgmodel.State(
                            name="fi", data=fi, label=["fi"], location="element"
                        )
                    )
                    state_case.addState(
                        name="sr", state=sgmodel.State(
                            name="sr", data=sr, label=["sr"], location="element"
                        )
                    )
                    sr_min = {}
                    for eid in eids_sr_min:
                        sr_min[eid] = sr[eid]
                    state_case.addState(
                        name="sr_min", state=sgmodel.State(
                            name="sr_min", data=sr_min, label=["sr_min"], location="element"
                        )
                    )

    elif analysis == "d" or analysis == "l":
        # Read dehomogenization output
        if file_format.lower().startswith("s"):
            if not isinstance(extension, list):
                extension = [extension,]
            extension = [e.lower() for e in extension]

            # Displacement
            if 'u' in extension:
                if num_elements == 0:
                    num_elements = sg.nelems
                u = None

                logger.info(f'reading displacement... {filename}.u')
                with open(f"{filename}.u", "r") as file:
                    for i_case in range(num_cases):

                        # print(f'i_case: {i_case}')

                        state_case = state_cases[i_case]

                        try:
                            u = _swiftcomp._read_output_node_disp_case(file, sg.nnodes)
                        except Exception as e:
                            logger.error(f"Error: {e}")
                            return None

                        if u is None:
                            logger.error("Error: No data read")
                            return None

                        state_case.addState(
                            name="u", state=sgmodel.State(
                                name="u", data=u, label=["u1", "u2", "u3"], location="node"
                            )
                        )

            # Element node strain and stress
            if 'sn' in extension:

                if num_elements == 0:
                    num_elements = sg.nelems

                logger.info(f'reading element node strain and stress... {filename}.sn')
                with open(f"{filename}.sn", "r") as file:
                    for i_case in range(num_cases):

                        # print(f'i_case: {i_case}')

                        state_case = state_cases[i_case]

                        try:
                            strains, stresses = _swiftcomp._read_output_node_strain_stress_case_global_gmsh(
                                file, num_elements, sg
                            )
                        except Exception as e:
                            logger.error(f"Error: {e}")
                            return None

                        if strains is None or stresses is None:
                            logger.error("Error: No data read")
                            return None

                        # Add strain state
                        state_case.addState(
                            name='e',
                            state=sgmodel.State(
                                name='e',
                                data=strains,
                                label=['e11', 'e22', 'e33', '2e23', '2e13', '2e12'],
                                location='element_node'
                            )
                        )

                        # Add stress state
                        state_case.addState(
                            name='s',
                            state=sgmodel.State(
                                name='s',
                                data=stresses,
                                label=['s11', 's22', 's33', 's23', 's13', 's12'],
                                location='element_node'
                            )
                        )

                        # state_case.addState(
                        #     name="ee", state=sgmodel.State(
                        #         name="ee", data=ee,
                        #         label=["e11", "e22", "e33", "2e23", "2e13", "2e12"],
                        #         location="element_node"
                        #     )
                        # )

            if 'snm' in extension:
                
                if num_elements == 0:
                    num_elements = sg.nelems

                logger.info(f'reading element node strain and stress in material c/s... {filename}.snm')
                with open(f"{filename}.snm", "r") as file:
                    for i_case in range(num_cases):

                        # print(f'i_case: {i_case}')

                        state_case = state_cases[i_case]

                        try:
                            strains, stresses = _swiftcomp._read_output_node_strain_stress_case_global_gmsh(
                                file, num_elements, sg
                            )
                        except Exception as e:
                            logger.error(f"Error: {e}")
                            return None

                        if strains is None or stresses is None:
                            logger.error("Error: No data read")
                            return None

                        # Add strain state in material coordinate system
                        state_case.addState(
                            name='em',
                            state=sgmodel.State(
                                name='em',
                                data=strains,
                                label=['e11m', 'e22m', 'e33m', '2e23m', '2e13m', '2e12m'],
                                location='element_node'
                            )
                        )

                        # Add stress state in material coordinate system
                        state_case.addState(
                            name='sm',
                            state=sgmodel.State(
                                name='sm',
                                data=stresses,
                                label=['s11m', 's22m', 's33m', 's23m', 's13m', 's12m'],
                                location='element_node'
                            )
                        )

        elif file_format.lower().startswith("v"):
            if not isinstance(extension, list):
                extension = [extension,]
            extension = [e.lower() for e in extension]

            # Displacement
            if "u" in extension:
                if num_elements == 0:
                    num_elements = sg.nelems
                u = None
                with open(f"{filename}.U", "r") as file:
                    for i_case in range(num_cases):

                        # print(f'i_case: {i_case}')

                        state_case = state_cases[i_case]

                        try:
                            u = _vabs.read_output_buffer(file, analysis, extension="u", **kwargs)
                        except Exception as e:
                            logger.error(f"Error: {e}")
                            return None

                        if u is None:
                            logger.error("Error: No data read")
                            return None

                        state_case.addState(
                            name="u", state=sgmodel.State(
                                name="u", data=u, label=["u1", "u2", "u3"], location="node"
                            )
                        )

            # Element strain and stress
            if "ele" in extension:

                if num_elements == 0:
                    num_elements = sg.nelems

                with open(f"{filename}.ELE", "r") as file:
                    for i_case in range(num_cases):

                        # print(f'i_case: {i_case}')

                        state_case = state_cases[i_case]

                        ee, es, eem, esm = None, None, None, None

                        try:
                            # ee, es, eem, esm = _vabs.read_output_buffer(
                            #     file, analysis, sg=sg, extension="ele", tool_version=tool_version,
                            #     ncase=num_cases, nelem=num_elements, **kwargs
                            # )
                            # print(float(tool_version))
                            if float(tool_version) > 4:
                                line = file.readline()  # skip the first line
                                while line.strip() == '':
                                    line = file.readline()
                                print(f'line: {line}')
                            ee, es, eem, esm = _vabs._readOutputElementStrainStressCase(
                                file, num_elements
                            )

                        except Exception as e:
                            logger.error(f"Error: {e}")
                            return None

                        if ee is None or es is None or eem is None or esm is None:
                            logger.error("Error: No data read")
                            return None

                        state_case.addState(
                            name="ee", state=sgmodel.State(
                                name="ee", data=ee,
                                label=["e11", "2e12", "2e13", "e22", "2e23", "e33"],
                                location="element"
                            )
                        )
                        state_case.addState(
                            name="es", state=sgmodel.State(
                                name="es", data=es,
                                label=["s11", "s12", "s13", "s22", "s23", "s33"],
                                location="element"
                            )
                        )
                        state_case.addState(
                            name="eem", state=sgmodel.State(
                                name="eem", data=eem,
                                label=["em11", "2em12", "2em13", "em22", "2em23", "em33"],
                                location="element"
                            )
                        )
                        state_case.addState(
                            name="esm", state=sgmodel.State(
                                name="esm", data=esm,
                                label=["sm11", "sm12", "sm13", "sm22", "sm23", "sm33"],
                                location="element"
                            )
                        )

                        # state_cases.append(state_case)

    return state_cases




def readOutput(
    fn, file_format, analysis='h', model_type='',
    sg=None, **kwargs
    ):
    """Read SG analysis output file.

    Parameters
    ----------
    fn : str
        Name of the SG analysis output file.
    file_format : str
        Format of the SG data file.
        Choose one from 'vabs', 'sc', 'swiftcomp'.
    analysis : str, optional
        Indicator of SG analysis.
        Default is 'h'.
        Choose one from
        * 'h': Homogenization
        * 'd' or 'l': Dehomogenization
        * 'fi': Initial failure indices and strength ratios
    model_type : str
        Type of the macro structural model.
        Choose one from
        * 'SD1': Cauchy continuum model
        * 'PL1': Kirchhoff-Love plate/shell model
        * 'PL2': Reissner-Mindlin plate/shell model
        * 'BM1': Euler-Bernoulli beam model
        * 'BM2': Timoshenko beam model
    sg : :obj:`StructureGene`
        Structure gene object

    Returns
    -------
    Model
        If `analysis` is 'h', return the consitutive model.
        * :obj:`EulerBernoulliBeamModel` if `model_type` is 'BM1'
        * :obj:`TimoshenkoBeamModel` if `model_type` is 'BM2'
        * :obj:`KirchhoffLovePlateModel` if `model_type` is 'PL1' and `file_format` is 'sc' or 'swiftcomp'
        * :obj:`ReissnerMindlinPlateModel` if `model_type` is 'PL2' and `file_format` is 'sc' or 'swiftcomp'
        * :obj:`CauchyContinuumModel` if `model_type` is 'SD1' and `file_format` is 'sc' or 'swiftcomp'
    StateCase
        If `analysis` is 'd' or 'l', return the state case.
    """

    if analysis == 'h':
        with open(fn, 'r') as file:
            if file_format.lower().startswith('s'):
                return _swiftcomp.read_output_buffer(
                    file, analysis=analysis, model_type=model_type,
                    **kwargs)
            elif file_format.lower().startswith('v'):
                return _vabs.read_output_buffer(
                    file, analysis, sg, model_type=model_type,
                    **kwargs)

    elif analysis == 'fi':
        if file_format.lower().startswith('s'):
            _fn = f'{fn}.fi'
            with open(_fn, 'r') as file:
                return _swiftcomp.read_output_buffer(
                    file, analysis=analysis, model_type=model_type,
                    **kwargs)
        elif file_format.lower().startswith('v'):
            _fn = f'{fn}.fi'
            with open(_fn, 'r') as file:
                return _vabs.read_output_buffer(file, analysis, sg, **kwargs)

    elif analysis == 'd' or analysis == 'l':
        if file_format.lower().startswith('s'):
            pass

        elif file_format.lower().startswith('v'):
            state_case = sgmodel.StateCase()

            # Displacement
            _u = None
            _fn = f'{fn}.U'
            with open(_fn, 'r') as file:
                _u = _vabs.read_output_buffer(file, analysis, ext='u', **kwargs)
            _state = sgmodel.State(
                name='u', data=_u, label=['u1', 'u2', 'u3'], location='node')
            state_case.addState(name='u', state=_state)

            # Element strain and stress
            _ee, _es, _eem, _esm = None, None, None, None
            _fn = f'{fn}.ELE'
            with open(_fn, 'r') as file:
                _ee, _es, _eem, _esm = _vabs.read_output_buffer(file, analysis, ext='ele', **kwargs)
            _state = sgmodel.State(
                name='ee', data=_ee, label=['e11', 'e12', 'e13', 'e22', 'e23', 'e33'], location='element')
            state_case.addState(name='ee', state=_state)
            _state = sgmodel.State(
                name='es', data=_es, label=['s11', 's12', 's13', 's22', 's23', 's33'], location='element')
            state_case.addState(name='es', state=_state)
            _state = sgmodel.State(
                name='eem', data=_eem, label=['em11', 'em12', 'em13', 'em22', 'em23', 'em33'], location='element')
            state_case.addState(name='eem', state=_state)
            _state = sgmodel.State(
                name='esm', data=_esm, label=['sm11', 'sm12', 'sm13', 'sm22', 'sm23', 'sm33'], location='element')
            state_case.addState(name='esm', state=_state)

            # state_field = sgmodel.StateField(
            #     node_displ=_u,
            #     elem_strain=_ee, elem_stress=_es, elem_strain_m=_eem, elem_stress_m=_esm
            # )

            return state_case


    return




def write(
    sg:StructureGene, fn:str, file_format:str,
    format_version:str='', analysis:str='h', sg_format:int=1,
    model_space:str='', prop_ref_y:str='x',
    macro_responses:list[sgmodel.StateCase]=[], model_type:str='SD1',
    load_type:int=0, sfi:str='8d', sff:str='20.12e', mesh_only:bool=False,
    binary:bool=False
) -> str:
    """Write analysis input.

    Parameters
    ----------
    sg : StructureGene
        Structure gene object
    fn : str
        Name of the input file
    file_format : str
        Format of the SG data file.
        Choose one from 'vabs', 'sc', 'swiftcomp'.
    format_version : str, optional
        Version of the format. Default is ''
    analysis : str, optional
        Indicator of SG analysis.
        Default is 'h'.
        Choose one from

        * 'h': Homogenization
        * 'd' or 'l': Dehomogenization
        * 'fi': Initial failure indices and strength ratios
    sg_format : {0, 1}, optional
        Format for the VABS input. Default is 1
    macro_responses : list[StateCase], optional
        Macroscopic responses. Default is `[]`.
    model_type : str
        Type of the macro structural model.
        Default is 'SD1'.
    load_type : int, optional
        Type of the load. Default is 0
    sfi : str, optional
        String formatting integers. Default is '8d'
    sff : str, optional
        String formatting floats. Default is '20.12e'
    mesh_only : bool, optional
        If write meshing data only. Default is False
    """

    logger.info('Writing file...')
    logger.debug(locals())

    # Check if file_format is valid
    if file_format not in ['sc', 'swiftcomp', 'vabs']:
        mesh_only = True

    # Check if structure_gene is valid
    if sg is None:
        raise ValueError('structure_gene is None')

    # Check if structure_gene.mesh is valid
    if sg.mesh is None:
        raise ValueError('structure_gene.mesh is None')

    # Open the file and write the data
    with open(fn, 'w', encoding='utf-8') as file:
        if file_format.startswith('s'):
            if format_version == '':
                format_version = GLOBAL.SC_VERSION_DEFAULT

            _swiftcomp.write_buffer(
                sg, file,
                analysis=analysis, model=model_type,
                macro_responses=macro_responses,
                model_space=model_space, prop_ref_y=prop_ref_y,
                load_type=load_type,
                sfi=sfi, sff=sff, version=format_version
            )

        elif file_format.startswith('v'):
            if format_version == '':
                format_version = GLOBAL.VABS_VERSION_DEFAULT

            _vabs.write_buffer(
                sg, file,
                analysis=analysis, sg_format=sg_format,
                macro_responses=macro_responses, model=model_type,
                model_space=model_space, prop_ref_y=prop_ref_y,
                sfi=sfi, sff=sff, version=format_version,
                mesh_only=mesh_only
            )

        elif file_format.startswith('gmsh'):
            _gmsh.write_buffer(
                file,
                sg.mesh,
                format_version=format_version,
                float_fmt=sff,
                sgdim=sg.sgdim,
                mesh_only=mesh_only,
                binary=binary
            )

        else:
            meshio.write(
                file, sg.mesh, file_format=file_format,
                int_fmt=sfi, float_fmt=sff)
            # sg.mesh.write(
            #     file,
            #     file_format,
            #     int_fmt=sfi,
            #     float_fmt=sff
            # )

    return fn




def convert(
    file_name_in: str,
    file_name_out: str,
    file_format_in: str,
    file_format_out: str,
    file_version_in: str = '',
    file_version_out: str = '',
    analysis: str = 'h',
    sgdim: int = 3,
    model_space: str = 'xy',
    prop_ref_y: str = 'x',
    model_type: str = 'SD1',
    vabs_format_version: int = 1,
    str_format_int: str = '8d',
    str_format_float: str = '20.12e',
    mesh_only: bool = False,
    renum_node: bool = False,
    renum_elem: bool = False
) -> StructureGene:
    """Convert the Structure Gene data file format.

    Parameters
    ----------
    file_name_in : str
        File name before conversion
    file_name_out : str
        File name after conversion
    file_format_in : str
        Format of the input file.
        Choose one from 'vabs', 'sc', 'swiftcomp'.
    file_format_out : str
        Format of the output file.
        Choose one from 'vabs', 'sc', 'swiftcomp'.
    file_version_in : str, optional
        Version of the input file, by default ''
    file_version_out : str, optional
        Version of the output file, by default ''
    analysis : str, optional
        Indicator of Structure Gene analysis.
        Default is 'h'.
        Choose one from

        * 'h': Homogenization
        * 'd' or 'l': Dehomogenization
        * 'fi': Initial failure indices and strength ratios
    sgdim : int
        Dimension of the geometry. Default is 3.
        Choose one from 1, 2, 3.
    model_type : str
        Type of the macro structural model.
        Default is 'SD1'.
        Choose one from

        * 'SD1': Cauchy continuum model
        * 'PL1': Kirchhoff-Love plate/shell model
        * 'PL2': Reissner-Mindlin plate/shell model
        * 'BM1': Euler-Bernoulli beam model
        * 'BM2': Timoshenko beam model
    vabs_format_version : int, optional
        Format for the VABS input, by default 1
    str_format_int : str, optional
        String formating integers, by default '8d'
    str_format_float : str, optional
        String formating floats, by default '20.12e'
    mesh_only : bool, optional
        If write meshing data only, by default False
    renum_elem : bool, optional
        If renumber elements, by default False
    """

    logger.info('Converting file format...')
    logger.debug(locals())

    if file_name_in is None:
        raise ValueError("Input file name should not be None.")

    if file_name_out is None:
        raise ValueError("Output file name should not be None.")

    sg = read(
        filename=file_name_in,
        file_format=file_format_in,
        model_type=model_type,
        format_version=file_version_in,
        sgdim=sgdim,
        mesh_only=mesh_only)

    if sg is None:
        raise ValueError("Input file is not a valid SG file.")

    if renum_node or renum_elem:
        logger.warning(
			"Parameters renum_node/renum_elem are deprecated and ignored. "
			"Numbering is now handled automatically based on format requirements."
		)

    write(
        sg=sg,
        fn=file_name_out,
        file_format=file_format_out,
        format_version=file_version_out,
        analysis=analysis,
        sg_format=vabs_format_version,
        model_space=model_space,
        prop_ref_y=prop_ref_y,
        model_type=model_type,
        sfi=str_format_int,
        sff=str_format_float,
        mesh_only=mesh_only)

    logger.info('File format converted.')

    return sg




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



















# ============================================================================
# Utility functions are now imported from sgio.iofunc.utils
# readSGInterfacePairs, readSGInterfaceNodes, readLoadCsv
# ============================================================================









# def readLoadCsv(fn, delimiter=',', nhead=1, encoding='utf-8-sig'):
#     r"""
#     load = {
#         'flight_condition_1': {
#             'fx': {
#                 'a': [],
#                 'r': [],
#                 'v': []
#             },
#             'fy': [],
#             'fz': [],
#             'mx', [],
#             'my', [],
#             'mz', []
#         },
#         'flight_condition_2': {},
#         ...
#     }
#     """

#     load = {}
#     azimuth = []

#     with open(fn, 'r', encoding=encoding) as file:
#         cr = csv.reader(file, delimiter=delimiter)

#         for i, row in enumerate(cr):
#             row = [s.strip() for s in row]
#             if row[0] == '':
#                 continue

#             if i < nhead:
#                 continue
#                 # # Read head
#                 # for label in row:
#                 #     if label.lower().startswith('rotor'):
#                 #         nid = int(label.split('NODE')[1])
#                 #         load['node_id'].append(nid)

#             else:
#                 condition = str(row[0])
#                 if not condition in load.keys():
#                     load[condition] = {
#                         'fx': {'a': [], 'r': [], 'v': []},
#                         'fy': {'a': [], 'r': [], 'v': []},
#                         'fz': {'a': [], 'r': [], 'v': []},
#                         'mx': {'a': [], 'r': [], 'v': []},
#                         'my': {'a': [], 'r': [], 'v': []},
#                         'mz': {'a': [], 'r': [], 'v': []}
#                     }

#                 a, r, fx, fy, fz, mx, my, mz = list(map(float, row[1:]))
#                 v = {
#                     'fx': fx, 'fy': fy, 'fz': fz,
#                     'mx': mx, 'my': my, 'mz': mz
#                 }

#                 azimuth.append(a)

#                 for component in ['fx', 'fy', 'fz', 'mx', 'my', 'mz']:
#                     load[condition][component]['a'].append(a)
#                     load[condition][component]['r'].append(r)
#                     load[condition][component]['v'].append(v[component])

#     azimuth = list(set(azimuth))

#     return load, azimuth
