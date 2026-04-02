from . import (
    abaqus,
    nastran,
    swiftcomp,
    vabs,
)

from ._meshio import add_cell_dict_data_to_mesh, add_point_dict_data_to_mesh
from .main import (
    convert,
    read, read_load_csv,
    read_output, read_output_model, read_output_state,
    write
    )
from .base import (
    BaseFormatReader,
    BaseFormatWriter,
    FormatRegistry,
    get_format_registry,
)

# Auto-register all format adapters
from . import registry_init
# from ..legacy.iofunc._helpers import (
#     read,
#     write,
#     write_points_cells,
#     register_format,
#     deregister_format,
#     extension_to_filetypes,
#     sg_reader_map,
#     sg_writer_map,
#     overridden_formats
# )

__all__ = [
    # Main functions
    "read",
    "write",
    "convert",
    "read_output",
    "read_output_model",
    "read_output_state",
    "read_load_csv",

    # Base classes and registry
    "BaseFormatReader",
    "BaseFormatWriter",
    "FormatRegistry",
    "get_format_registry",

    # Mesh utilities
    "add_cell_dict_data_to_mesh",
    "add_point_dict_data_to_mesh",
]
