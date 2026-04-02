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
from sgio.core import StructureGene
from sgio.core.numbering import ensure_node_ids
from sgio.utils import readNextNonEmptyLine

# Import utility functions from refactored modules
from .utils import (
    read_load_csv,
    read_sg_interface_pairs,
    read_sg_interface_nodes,
)

logger = logging.getLogger(__name__)

# ============================================================================
# SECTION: Constants
# ============================================================================

DEFAULT_MATERIAL_PROPERTIES = {
    'elastic': [200e9, 0.3],  # Default steel-like properties
    'isotropy': 0
}

FILE_EXTENSIONS = {
    'displacement': 'u',
    'element': 'ele', 
    'element_vabs': 'ELE',
    'failure_index': 'fi',
    'element_node_strain': 'sn',
    'element_node_strain_material': 'snm'
}

# ============================================================================
# SECTION: Utility Functions
# ============================================================================

def _safe_file_read(filename: str, mode: str = 'r'):
    """Context manager for safe file operations with error handling.
    
    Parameters
    ----------
    filename : str
        Path to file
    mode : str
        File read mode ('r' or 'rb')
        
    Returns
    -------
    context manager
        File context manager with error handling
        
    Raises
    ------
    FileNotFoundError
        If file does not exist
    IOError
        If file cannot be opened
    """
    try:
        return open(filename, mode)
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        raise
    except IOError as e:
        logger.error(f"Error opening file {filename}: {e}")
        raise


def _get_file_extension(file_format: str, extension_type: str) -> str:
    """Get the appropriate file extension for a given format and type.
    
    Parameters
    ----------
    file_format : str
        File format ('vabs', 'swiftcomp', etc.)
    extension_type : str
        Type of extension ('displacement', 'element', etc.)
        
    Returns
    -------
    str
        File extension
    """
    if file_format.lower().startswith('v'):
        if extension_type == 'displacement':
            return FILE_EXTENSIONS['displacement'].upper()
        elif extension_type == 'element':
            return FILE_EXTENSIONS['element_vabs']
    
    # Default to lowercase extensions
    return FILE_EXTENSIONS.get(extension_type, extension_type)


def _validate_sg_parameter(sg: StructureGene | None) -> StructureGene:
    """Validate StructureGene parameter, raise error if None.
    
    Parameters
    ----------
    sg : StructureGene or None
        StructureGene object to validate
        
    Returns
    -------
    StructureGene
        Valid StructureGene object
        
    Raises
    ------
    ValueError
        If sg is None
    """
    if sg is None:
        raise ValueError("StructureGene parameter cannot be None")
    return sg


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
    sg.smdim, sg.model = _parse_model_type(model_type)
    sg.mesh = mesh

    # Ensure required data exists in mesh
    _ensure_mesh_data(mesh)
    
    # Process materials and properties
    _process_materials_from_mesh(sg, mesh, sgdim)

    return sg


def _restore_sg_from_mesh_extras(sg: StructureGene, mesh) -> None:
    """Restore SG layer definitions and config from custom mesh attributes.

    Reads ``mesh.sg_layer_defs`` and ``mesh.sg_configs`` (attached by the Gmsh
    reader from ``$SGLayerDef`` / ``$SGConfig`` blocks) and repopulates the
    corresponding StructureGene fields.

    Parameters
    ----------
    sg : StructureGene
        Structure gene object to update.
    mesh : meshio.Mesh
        Mesh object that may carry ``sg_layer_defs`` and ``sg_configs``.
    """
    # Restore mocombos from $SGLayerDef
    sg_layer_defs = getattr(mesh, 'sg_layer_defs', {})
    if sg_layer_defs:
        # sg_layer_defs: {layer_id: (mat_id, angle)}
        # mocombos needs: {property_id: (material_name, angle)}
        for layer_id, (mat_id, angle) in sg_layer_defs.items():
            mat_name = sg.get_material_name_by_id(mat_id)
            if mat_name is None:
                mat_name = f'Material_{mat_id}'
                sg.add_material_name_id_pair(mat_name, mat_id)
            sg.mocombos[layer_id] = (mat_name, angle)

    # Restore solver config from $SGConfig
    sg_configs = getattr(mesh, 'sg_configs', {})
    if sg_configs:
        if 'sgdim' in sg_configs:
            sg.sgdim = int(sg_configs['sgdim'])
        if 'model' in sg_configs:
            sg.model = int(sg_configs['model'])
        if 'do_damping' in sg_configs:
            sg.do_damping = int(sg_configs['do_damping'])
        if 'thermal' in sg_configs:
            sg.physics = int(sg_configs['thermal'])


def _parse_model_type(model_type: str | int) -> tuple[int, int]:
    """Parse model type string/integer into smdim and submodel.
    
    Parameters
    ----------
    model_type : str or int
        Model type specification
        
    Returns
    -------
    tuple[int, int]
        (smdim, submodel) values
    """
    if isinstance(model_type, int):
        return model_type, model_type
    
    if isinstance(model_type, str):
        prefix = model_type.upper()[:2]
        if prefix == 'SD':
            smdim = 3
        elif prefix == 'PL':
            smdim = 2
        elif prefix == 'BM':
            smdim = 1
        else:
            smdim = 3
            
        try:
            submodel = int(model_type[2]) - 1
        except (IndexError, ValueError):
            submodel = 0
        return smdim, submodel
    
    return 3, 0


def _ensure_mesh_data(mesh: Mesh) -> None:
    """Ensure required mesh data (node_id, element_id, property_id) exists.
    
    Parameters
    ----------
    mesh : Mesh
        Mesh object to update
    """
    import numpy as np
    
    # Ensure node_id point_data exists
    ensure_node_ids(mesh)

    # Ensure element_id cell_data exists
    if 'element_id' not in mesh.cell_data:
        element_id = []
        elem_idx = 0
        for cell_block in mesh.cells:
            block_ids = list(range(elem_idx + 1, elem_idx + 1 + len(cell_block.data)))
            element_id.append(np.array(block_ids, dtype=int))
            elem_idx += len(cell_block.data)
        mesh.cell_data['element_id'] = element_id

    # Ensure property_id cell_data exists
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


def _process_materials_from_mesh(sg: StructureGene, mesh: Mesh, sgdim: int) -> None:
    """Process materials from mesh field_data and cell_data.
    
    Parameters
    ----------
    sg : StructureGene
        Structure gene object to update
    mesh : Mesh
        Mesh object containing material information
    sgdim : int
        Structure gene dimension
    """
    # Extract material name-ID pairs from Gmsh PhysicalNames
    if hasattr(mesh, 'field_data') and mesh.field_data:
        for name, (phys_id, dim) in mesh.field_data.items():
            if dim == sgdim:
                sg.add_material_name_id_pair(name, phys_id)

    # Process property_id from cell_data and create materials
    if 'property_id' in mesh.cell_data:
        property_ids = set()
        for prop_block in mesh.cell_data['property_id']:
            for prop_id in prop_block:
                if prop_id is not None:
                    property_ids.add(int(prop_id))

        for prop_id in property_ids:
            if prop_id not in sg.mocombos:
                mat_name = _get_or_create_material_name(sg, prop_id)
                _ensure_material_exists(sg, mat_name)
                sg.mocombos[prop_id] = (mat_name, 0.0)  # (material_name, angle)


def _get_or_create_material_name(sg: StructureGene, prop_id: int) -> str:
    """Get material name by property ID or create a default name.
    
    Parameters
    ----------
    sg : StructureGene
        Structure gene object
    prop_id : int
        Property ID
        
    Returns
    -------
    str
        Material name
    """
    mat_name = sg.get_material_name_by_id(prop_id)
    if mat_name is None:
        mat_name = f'Material_{prop_id}'
        sg.add_material_name_id_pair(mat_name, prop_id)
    return mat_name


def _ensure_material_exists(sg: StructureGene, mat_name: str) -> None:
    """Ensure material exists in structure gene, create with defaults if needed.
    
    Parameters
    ----------
    sg : StructureGene
        Structure gene object
    mat_name : str
        Material name to ensure exists
    """
    if mat_name not in sg.materials:
        import sgio.model.solid as smdl
        mat = smdl.CauchyContinuumModel(name=mat_name)
        mat.set('isotropy', 0)
        mat.set('elastic', DEFAULT_MATERIAL_PROPERTIES['elastic'])
        sg.materials[mat_name] = mat


def _read_swiftcomp_output_state(
    filename: str, analysis: str, model_type: str, extension: list[str], 
    num_cases: int, num_elements: int, sg: StructureGene, **kwargs
) -> list[sgmodel.StateCase]:
    """Read SwiftComp output state data.
    
    Parameters
    ----------
    filename : str
        Base filename
    analysis : str
        Analysis type
    model_type : str
        Model type
    extension : list[str]
        Extensions to read
    num_cases : int
        Number of cases
    num_elements : int
        Number of elements
    sg : StructureGene
        Structure gene object
    **kwargs
        Additional arguments
        
    Returns
    -------
    list[StateCase]
        List of state cases
    """
    state_cases = [sgmodel.StateCase({}, {}) for _ in range(num_cases)]
    
    if analysis == "fi":
        with open(f"{filename}.fi", "r") as file:
            return _swiftcomp.read_output_buffer(
                file, analysis=analysis, model_type=model_type, **kwargs
            )
    
    elif analysis == "d" or analysis == "l":
        # Read displacement
        if 'u' in extension:
            if num_elements == 0:
                num_elements = sg.nelems
            logger.info(f'reading displacement... {filename}.u')
            with open(f"{filename}.u", "r") as file:
                for i_case in range(num_cases):
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

        # Read element node strain and stress
        if 'sn' in extension:
            if num_elements == 0:
                num_elements = sg.nelems
            logger.info(f'reading element node strain and stress... {filename}.sn')
            with open(f"{filename}.sn", "r") as file:
                for i_case in range(num_cases):
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
                        name='e', state=sgmodel.State(
                            name='e', data=strains,
                            label=['e11', 'e22', 'e33', '2e23', '2e13', '2e12'],
                            location='element_node'
                        )
                    )
                    # Add stress state
                    state_case.addState(
                        name='s', state=sgmodel.State(
                            name='s', data=stresses,
                            label=['s11', 's22', 's33', 's23', 's13', 's12'],
                            location='element_node'
                        )
                    )

        # Read element node strain and stress in material coordinate system
        if 'snm' in extension:
            if num_elements == 0:
                num_elements = sg.nelems
            logger.info(f'reading element node strain and stress in material c/s... {filename}.snm')
            with open(f"{filename}.snm", "r") as file:
                for i_case in range(num_cases):
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
                        name='em', state=sgmodel.State(
                            name='em', data=strains,
                            label=['e11m', 'e22m', 'e33m', '2e23m', '2e13m', '2e12m'],
                            location='element_node'
                        )
                    )
                    # Add stress state in material coordinate system
                    state_case.addState(
                        name='sm', state=sgmodel.State(
                            name='sm', data=stresses,
                            label=['s11m', 's22m', 's33m', 's23m', 's13m', 's12m'],
                            location='element_node'
                        )
                    )

    return state_cases


def _read_vabs_output_state(
    filename: str, analysis: str, extension: list[str], 
    num_cases: int, num_elements: int, sg: StructureGene, 
    tool_version: str, **kwargs
) -> list[sgmodel.StateCase]:
    """Read VABS output state data.
    
    Parameters
    ----------
    filename : str
        Base filename
    analysis : str
        Analysis type
    extension : list[str]
        Extensions to read
    num_cases : int
        Number of cases
    num_elements : int
        Number of elements
    sg : StructureGene
        Structure gene object
    tool_version : str
        Tool version
    **kwargs
        Additional arguments
        
    Returns
    -------
    list[StateCase]
        List of state cases
    """
    state_cases = [sgmodel.StateCase({}, {}) for _ in range(num_cases)]
    
    if analysis == "fi":
        if num_elements == 0:
            num_elements = sg.nelems
        with open(f"{filename}.fi", "r") as file:
            for i_case in range(num_cases):
                state_case = state_cases[i_case]
                try:
                    if float(tool_version) > 4:
                        line = file.readline()  # skip the first line
                        while line.strip() == '':
                            line = file.readline()
                        print(f'line: {line}')
                    fi, sr, eids_sr_min = _vabs._readOutputFailureIndexCase(file, num_elements)
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
        # Read displacement
        if "u" in extension:
            if num_elements == 0:
                num_elements = sg.nelems
            with open(f"{filename}.U", "r") as file:
                for i_case in range(num_cases):
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

        # Read element strain and stress
        if "ele" in extension:
            if num_elements == 0:
                num_elements = sg.nelems
            with open(f"{filename}.ELE", "r") as file:
                for i_case in range(num_cases):
                    state_case = state_cases[i_case]
                    ee, es, eem, esm = None, None, None, None
                    try:
                        if float(tool_version) > 4:
                            line = file.readline()  # skip the first line
                            while line.strip() == '':
                                line = file.readline()
                            print(f'line: {line}')
                        ee, es, eem, esm = _vabs._readOutputElementStrainStressCase(file, num_elements)
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

    return state_cases


def read_output_state(
    filename: str, file_format: str, analysis: str, model_type: str = "",
    extension: str = "ele", sg: StructureGene = None, tool_version: str = "",
    num_cases: int = 1, num_elements: int = 0, output_format: int = 0, **kwargs
) -> list[sgmodel.StateCase]:
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
    list[StateCase]
        List of state case objects
    """
    logger.debug('reading output state...')
    logger.debug(locals())

    # Validate and normalize parameters
    if not isinstance(extension, list):
        extension = [extension]
    extension = [e.lower() for e in extension]
    
    # Delegate to format-specific handlers
    if file_format.lower().startswith("s"):
        return _read_swiftcomp_output_state(
            filename, analysis, model_type, extension, 
            num_cases, num_elements, sg, **kwargs
        )
    elif file_format.lower().startswith("v"):
        return _read_vabs_output_state(
            filename, analysis, extension, num_cases, 
            num_elements, sg, tool_version, **kwargs
        )
    else:
        raise ValueError(f"Unsupported file format: {file_format}")


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
        sg = _abaqus.read(
            filename, sgdim=sgdim, model=model_type
        )
    elif file_format == 'gmsh':
        with open(filename, 'rb') as file:
            mesh = _gmsh.read_buffer(file, format_version=format_version)
        sg = _mesh_to_sg(mesh, sgdim=sgdim, model_type=model_type)
        _restore_sg_from_mesh_extras(sg, mesh)
    else:
        raise ValueError(f"Unknown file format: {file_format}")

    if not sg:
        sg = StructureGene(sgdim=sgdim, smdim=model_type)
    if not sg.mesh:
        sg.mesh, _, _ = _meshio.read(filename, file_format)

    return sg


def read_output_model(
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


def read_output(
    filename: str, file_format: str, analysis: str = 'h', model_type: str = '',
    sg: StructureGene = None, **kwargs
) -> sgmodel.Model | sgmodel.StateCase | None:
    """Read SG analysis output file.

    Parameters
    ----------
    filename : str
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
    sg : StructureGene
        Structure gene object

    Returns
    -------
    Model
        If `analysis` is 'h', return consitutive model.
        * :obj:`EulerBernoulliBeamModel` if `model_type` is 'BM1'
        * :obj:`TimoshenkoBeamModel` if `model_type` is 'BM2'
        * :obj:`KirchhoffLovePlateModel` if `model_type` is 'PL1' and `file_format` is 'sc' or 'swiftcomp'
        * :obj:`ReissnerMindlinPlateModel` if `model_type` is 'PL2' and `file_format` is 'sc' or 'swiftcomp'
        * :obj:`CauchyContinuumModel` if `model_type` is 'SD1' and `file_format` is 'sc' or 'swiftcomp'
    StateCase
        If `analysis` is 'd' or 'l', return the state case.
    """

    if analysis == 'h':
        with open(filename, 'r') as file:
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
            fi_filename = f'{filename}.fi'
            with open(fi_filename, 'r') as file:
                return _swiftcomp.read_output_buffer(
                    file, analysis=analysis, model_type=model_type,
                    **kwargs)
        elif file_format.lower().startswith('v'):
            fi_filename = f'{filename}.fi'
            with open(fi_filename, 'r') as file:
                return _vabs.read_output_buffer(file, analysis, sg, **kwargs)

    elif analysis == 'd' or analysis == 'l':
        if file_format.lower().startswith('v'):
            state_case = sgmodel.StateCase()

            # Displacement
            u_data = None
            u_filename = f'{filename}.U'
            with open(u_filename, 'r') as file:
                u_data = _vabs.read_output_buffer(file, analysis, ext='u', **kwargs)
            state = sgmodel.State(
                name='u', data=u_data, label=['u1', 'u2', 'u3'], location='node')
            state_case.addState(name='u', state=state)

            # Element strain and stress
            ee, es, eem, esm = None, None, None, None
            ele_filename = f'{filename}.ELE'
            with open(ele_filename, 'r') as file:
                ee, es, eem, esm = _vabs.read_output_buffer(file, analysis, ext='ele', **kwargs)
            state = sgmodel.State(
                name='ee', data=ee, label=['e11', 'e12', 'e13', 'e22', 'e23', 'e33'], location='element')
            state_case.addState(name='ee', state=state)
            state = sgmodel.State(
                name='es', data=es, label=['s11', 's12', 's13', 's22', 's23', 's33'], location='element')
            state_case.addState(name='es', state=state)
            state = sgmodel.State(
                name='eem', data=eem, label=['em11', 'em12', 'em13', 'em22', 'em23', 'em33'], location='element')
            state_case.addState(name='eem', state=state)
            state = sgmodel.State(
                name='esm', data=esm, label=['sm11', 'sm12', 'sm13', 'sm22', 'sm23', 'sm33'], location='element')
            state_case.addState(name='esm', state=state)

            return state_case

    return None


def write(
    sg: StructureGene, filename: str, file_format: str,
    format_version: str = '', analysis: str = 'h', sg_format: int = 1,
    model_space: str = '', prop_ref_y: str = 'x',
    macro_responses: list[sgmodel.StateCase] = [], model_type: str = 'SD1',
    load_type: int = 0, sfi: str = '8d', sff: str = '20.12e', mesh_only: bool = False,
    binary: bool = False
) -> str:
    """Write analysis input.

    Parameters
    ----------
    sg : StructureGene
        Structure gene object
    filename : str
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
    with open(filename, 'w', encoding='utf-8') as file:
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
            # Build material_id_map and sg_configs for custom SG blocks
            material_id_map = sg.get_export_material_ids() if sg.mocombos else {}
            sg_configs = {}
            if sg.sgdim is not None:
                sg_configs['sgdim'] = sg.sgdim
            if sg.smdim is not None:
                sg_configs['model'] = sg.model
            sg_configs['do_damping'] = sg.do_damping
            sg_configs['thermal'] = sg.physics

            _gmsh.write_buffer(
                file,
                sg.mesh,
                format_version=format_version,
                float_fmt=sff,
                sgdim=sg.sgdim,
                mesh_only=mesh_only,
                binary=binary,
                mocombos=sg.mocombos if sg.mocombos else None,
                material_id_map=material_id_map,
                sg_configs=sg_configs,
            )

        else:
            meshio.write(
                file, sg.mesh, file_format=file_format,
                int_fmt=sfi, float_fmt=sff)

    return filename


def convert_file_format(
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
        filename=file_name_out,
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


# Backward compatibility alias
convert = convert_file_format


# ============================================================================
# SECTION: All Backward Compatibility Aliases
# ============================================================================

# Create all backward compatibility aliases for camelCase function names
__all__ = [
    'read_output_model', 'read_output_state', 'read_output', 'read_load_csv', 'write', 'convert',
]