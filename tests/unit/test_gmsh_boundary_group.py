"""Regression tests for lower-dimensional physical groups on the Gmsh read path.

A Gmsh mesh may carry auxiliary physical groups that are markers rather than
material regions -- ``gmshModel``'s RVE builders add a ``boundary`` surface
group unconditionally. Those elements must not become SG elements. What decides
membership is whether an element's physical group resolves to a declared
section; element topological dimension is never compared against ``sgdim``.
"""

from __future__ import annotations

import numpy as np
import pytest

import sgio
from sgio._exceptions import IncompleteModelDataError
from sgio.core.mesh import SGMesh, check_isolated_nodes
from sgio.iofunc._mesh_convert import mesh_to_sg


@pytest.mark.unit
@pytest.mark.parametrize(
    ('mesh_name', 'sections_name', 'model_type', 'expected_elements', 'expected_sgdim'),
    [
        (
            'sg33_cube_boundary_group_bug_min_gmsh41.msh',
            'sections_sg33_cube_boundary_group.json',
            'SD1',
            24,
            3,
        ),
        # Same situation one dimension down, so a fix cannot be a 3D special case.
        (
            'sg22_square_boundary_group_bug_min_gmsh41.msh',
            'sections_sg22_square_boundary_group.json',
            'PL1',
            4,
            2,
        ),
    ],
)
def test_boundary_group_elements_are_not_sg_elements(
    gmsh_test_files,
    mesh_name,
    sections_name,
    model_type,
    expected_elements,
    expected_sgdim,
):
    """The undeclared ``boundary`` group must not add elements or materials."""
    root = gmsh_test_files["root"]

    sg = sgio.read_sg_from_gmsh_bundle(
        root / mesh_name, root / sections_name, model_type=model_type
    )

    assert sg.nelems == expected_elements
    assert list(sg.materials) == ['matrix']
    # sgdim is read off the elements that belong to the gene, not off whichever
    # cell block happens to come first in the file (here a lower-dim one).
    assert sg.sgdim == expected_sgdim


@pytest.mark.unit
def test_boundary_group_removal_leaves_no_isolated_nodes(gmsh_test_files):
    """Dropping the surface group must not orphan nodes in a conforming mesh."""
    root = gmsh_test_files["root"]

    sg = sgio.read_sg_from_gmsh_bundle(
        root / 'sg33_cube_boundary_group_bug_min_gmsh41.msh',
        root / 'sections_sg33_cube_boundary_group.json',
        model_type='SD1',
    )

    assert sg.nnodes == 14
    # Raises if any node lost every referencing element; all 14 stay referenced.
    _, nodes_in_cells = check_isolated_nodes(sg.mesh)
    assert len(nodes_in_cells) == 14


@pytest.mark.unit
def test_beam_elements_survive_in_a_solid_structure_gene():
    """1D beam elements are real SG elements of a 3D strut lattice.

    Guard against a fix regressing to a ``dim == sgdim`` filter, which would
    delete the whole model here.
    """
    mesh = SGMesh(
        points=np.array(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]],
            dtype=float,
        ),
        cells=[("line", np.array([[0, 1], [1, 2], [2, 3]], dtype=int))],
        cell_data={"property_id": [np.array([1, 1, 1], dtype=int)]},
        field_data={"strut": np.array([1, 1], dtype=int)},
    )

    sg = mesh_to_sg(mesh, sgdim=3, model_type="SD1", section_names={"strut"})

    assert sg.nelems == 3
    assert sg.mocombos[1] == ("strut", 0.0)


@pytest.mark.unit
def test_mixed_tags_in_one_cell_block_are_filtered_per_element():
    """A block mixing a resolving and a non-resolving physical group.

    A cell block is not a proxy for a physical group: MSH 2.2 (and any other
    format that merges same-typed elements from different physical groups
    into one block) can put a section element and an auxiliary marker element
    side by side in the same block. Filtering per block instead of per
    element either drops the whole block (losing the legitimate element) or
    keeps it whole (leaking the auxiliary one) -- both wrong.
    """
    mesh = SGMesh(
        points=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0]]),
        cells=[("triangle", np.array([[0, 1, 2], [1, 3, 2]], dtype=int))],
        cell_data={"property_id": [np.array([1, 2], dtype=int)]},
        field_data={
            "matrix": np.array([1, 2], dtype=int),
            "boundary": np.array([2, 2], dtype=int),
        },
    )

    sg = mesh_to_sg(mesh, sgdim=2, model_type="PL1", section_names={"matrix"})

    assert sg.nelems == 1
    assert sg.mocombos == {1: ("matrix", 0.0)}
    np.testing.assert_array_equal(sg.mesh.cells[0].data, [[0, 1, 2]])


@pytest.mark.unit
def test_no_matching_section_error_lists_raw_tags_without_physical_names():
    """No ``$PhysicalNames`` must still name the tags present, not say "none"."""
    mesh = SGMesh(
        points=np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]),
        cells=[("triangle", np.array([[0, 1, 2]], dtype=int))],
        cell_data={"property_id": [np.array([5], dtype=int)]},
    )

    with pytest.raises(IncompleteModelDataError, match="tag 5"):
        mesh_to_sg(mesh, sgdim=2, model_type="PL1", section_names={"absent"})


@pytest.mark.unit
def test_reading_a_bare_msh_as_a_structure_gene_is_refused(gmsh_test_files):
    """A ``.msh`` carries no material data, so sgio refuses rather than inventing."""
    fixture = gmsh_test_files["root"] / 'sg33_cube_boundary_group_bug_min_gmsh41.msh'

    with pytest.raises(IncompleteModelDataError, match="mesh data only"):
        sgio.read(str(fixture), 'gmsh', sgdim=3, model_type='SD1')


@pytest.mark.unit
def test_sections_matching_no_element_are_reported(gmsh_test_files, tmp_path):
    """A section set that matches nothing names the groups the mesh actually has."""
    import json

    sections_path = tmp_path / "sections.json"
    sections_path.write_text(
        json.dumps(
            {
                "sections": [
                    {
                        "kind": "material",
                        "theory": "cauchy_continuum",
                        "name": "absent",
                        "payload": {
                            "name": "absent",
                            "model": "sd1",
                            "isotropy": 0,
                            "elastic": {"e": 1.0e9, "nu": 0.3},
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(IncompleteModelDataError, match="boundary"):
        sgio.read_sg_from_gmsh_bundle(
            gmsh_test_files["root"] / 'sg33_cube_boundary_group_bug_min_gmsh41.msh',
            sections_path,
            model_type='SD1',
        )
