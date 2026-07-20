from . import (
    abaqus,
    nastran,
    swiftcomp,
    vabs,
)

from ._meshio import add_cell_dict_data_to_mesh, add_point_dict_data_to_mesh
from .layout import (
    merge_sections,
    merge_sections_from_csv,
    read_section_layout_csv,
    write_merged_sections,
)
from .gmsh.bundle import (
    read_config_from_json,
    read_sections_from_json,
    read_sg_from_gmsh_bundle,
    section_model_to_record,
    write_config_to_json,
    write_sections_to_json,
)
from .main import (
    convert,
    read, read_fe_model, read_load_csv,
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
    "read_fe_model",
    "write",
    "convert",
    "read_output",
    "read_output_model",
    "read_output_state",
    "read_load_csv",
    "merge_sections",
    "merge_sections_from_csv",
    "read_section_layout_csv",
    "write_merged_sections",
    "read_sg_from_gmsh_bundle",
    "read_sections_from_json",
    "write_sections_to_json",
    "read_config_from_json",
    "write_config_to_json",
    "section_model_to_record",

    # Base classes and registry
    "BaseFormatReader",
    "BaseFormatWriter",
    "FormatRegistry",
    "get_format_registry",

    # Mesh utilities
    "add_cell_dict_data_to_mesh",
    "add_point_dict_data_to_mesh",
]
