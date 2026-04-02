from ._version import __version__

from ._global import logger, configure_logging

from ._exceptions import (
    SwiftCompLicenseError,
    VABSLicenseError,
    SwiftCompIOError,
    VABSIOError,
    SwiftCompError,
    VABSError,
    OutputFileError,
)

from .core import (
    StructureGene,
    SGMesh,
    check_isolated_nodes,
    renumber_elements,
    validate_node_ids,
    validate_element_ids,
    get_node_id_mapping,
    ensure_node_ids,
    ensure_element_ids,
    auto_renumber_for_format,
    check_duplicate_ids,
    check_forbidden_ids,
    FormatNumberingRequirements,
    FORMAT_ALIASES,
    FORMAT_REQUIREMENTS,
    normalize_format_name,
    get_numbering_requirements,
)
from .core.builder import build_sg_1d
from .core.merge import combine_sg

from .model import *

from .iofunc import (
    read,
    read_output,
    read_output_model,
    read_output_state,
    write,
    convert,
    read_load_csv,
    add_cell_dict_data_to_mesh,
    add_point_dict_data_to_mesh,
    # write_points_cells,
    # register_format,
    # deregister_format,
    # extension_to_filetypes,
    # sg_reader_map,
    # sg_writer_map,
    # overridden_formats
)

from .execu import run

from .utils import (
    plot_sg_2d,
)

from ._vendors import inprw

__all__ = [
    # Version
    "__version__",
    # Configuration and logging
    "configure_logging",
    # I/O functions
    "read",
    "read_output",
    "read_output_model",
    "read_output_state",
    "write",
    "convert",
    "read_load_csv",
    "add_cell_dict_data_to_mesh",
    "add_point_dict_data_to_mesh",
    # Execution
    "run",
    # Core functions and classes
    "build_sg_1d",
    "combine_sg",
    "SGMesh",
    "StructureGene",
    "check_isolated_nodes",
    "renumber_elements",
    # Numbering validation and utilities
    "validate_node_ids",
    "validate_element_ids",
    "get_node_id_mapping",
    "ensure_node_ids",
    "ensure_element_ids",
    "auto_renumber_for_format",
    "check_duplicate_ids",
    "check_forbidden_ids",
    # Format requirements registry (Phase 4.1)
    "FormatNumberingRequirements",
    "FORMAT_ALIASES",
    "FORMAT_REQUIREMENTS",
    "normalize_format_name",
    "get_numbering_requirements",
    # Utility functions
    "plot_sg_2d",
    # Model classes from .model import *
    "CauchyContinuumModel",
    "KirchhoffLovePlateShellModel",
    "ReissnerMindlinPlateShellModel",
    "EulerBernoulliBeamModel",
    "TimoshenkoBeamModel",
    # Exception classes
    "SwiftCompLicenseError",
    "VABSLicenseError",
    "SwiftCompIOError",
    "VABSIOError",
    "SwiftCompError",
    "VABSError",
    "OutputFileError",
]
