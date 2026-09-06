.. _ref_io:

I/O Functions
==============


.. currentmodule:: sgio


Reading SG data
---------------

..  autosummary::
    :toctree: _temp

    read
    read_fe_model
    read_sg_from_gmsh_bundle


Reading analysis output
-----------------------

..  autosummary::
    :toctree: _temp

    read_output
    read_output_model
    read_output_state


Writing and converting SG data
------------------------------

..  autosummary::
    :toctree: _temp

    write
    convert


Sections, materials, and configuration
--------------------------------------

..  autosummary::
    :toctree: _temp

    read_sections_from_json
    write_sections_to_json
    read_config_from_json
    write_config_to_json
    read_material_from_json
    read_materials_from_json
    write_material_to_json
    section_model_to_record


Section layout and merging
--------------------------

..  autosummary::
    :toctree: _temp

    read_section_layout_csv
    read_load_csv
    merge_sections
    merge_sections_from_csv
    write_merged_sections


Mesh data helpers
-----------------

..  autosummary::
    :toctree: _temp

    add_cell_dict_data_to_mesh
    add_point_dict_data_to_mesh


Solver execution
----------------

..  autosummary::
    :toctree: _temp

    run
