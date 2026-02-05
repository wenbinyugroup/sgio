"""Example: check tetra4 ordering in a Gmsh mesh."""
from pathlib import Path

import sgio
from sgio.core.mesh import (
    check_cell_ordering,
    fix_cell_ordering,
    get_invalid_cell_ordering_element_ids,
)


def main() -> None:
    """Run the cell-ordering check on a sample Gmsh mesh."""
    input_file = Path(__file__).parent / "files" / "sg33_cube_tetra4_min_gmsh41.msh"
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        print("Please ensure the file exists in the examples/files/ directory")
        return

    sg = sgio.read(
        str(input_file),
        file_format="gmsh",
        format_version="4.1",
    )
    if sg.mesh is None:
        print("Error: Mesh data not found in the structure gene")
        return

    invalid_element_ids = get_invalid_cell_ordering_element_ids(sg.mesh)
    if not invalid_element_ids:
        print("Cell ordering check passed for all supported cell types.")
        return

    print("Cell ordering check failed.")
    for (cb_id, cell_type), element_ids in invalid_element_ids.items():
        ids_str = ", ".join(str(eid) for eid in element_ids)
        print(
            f"block {cb_id} '{cell_type}': {len(element_ids)} invalid element IDs"
        )
        print(f"element_ids: {ids_str}")

    fixed = fix_cell_ordering(sg.mesh)
    if not fixed:
        print("No supported cell types were fixed.")
        return

    print("Applied ordering fix to supported cell types.")
    for (cb_id, cell_type), indices in fixed.items():
        indices_str = ", ".join(str(idx) for idx in indices)
        print(
            f"block {cb_id} '{cell_type}': {len(indices)} cells fixed"
        )
        print(f"cell_indices: {indices_str}")

    check_cell_ordering(sg.mesh)
    print("Cell ordering check passed after fix.")


if __name__ == "__main__":
    main()
