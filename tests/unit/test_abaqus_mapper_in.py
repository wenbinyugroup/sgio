"""Unit tests for the Abaqus input mapper layer."""

from __future__ import annotations

import numpy as np
import pytest

from sgio.core.property_ref_csys import (
    property_ref_csys_to_axes,
    property_ref_value_to_vabs_theta,
)
from sgio.iofunc.abaqus.mapper_in import map_input_to_structure_gene
from sgio.iofunc.abaqus.parser import parse_input_file


def _write_direct_orientation_input(
    tmp_path,
    orientation_options: str = "",
    rotation_axis: int = 3,
    rotation_angle: float = 0.0,
) -> str:
    """Write one minimal 3D Abaqus input with a direct orientation origin."""
    filename = tmp_path / "direct_orientation.inp"
    filename.write_text(
        f"""*Heading
*Part, name=RVE
*Node
1, 0., 0., 0.
2, 1., 0., 0.
3, 0., 1., 0.
4, 0., 0., 1.
5, 1., 1., 1.
*Element, type=C3D4, elset=FIBRE
1, 1, 2, 3, 4
*Element, type=C3D4, elset=MATRIX
2, 2, 3, 4, 5
*Material, name=FIBRE_MAT
*Elastic
1.0, 0.3
*Material, name=MATRIX_MAT
*Elastic
1.0, 0.3
*Orientation, name=FIBRE_ORIENTATION{orientation_options}
2., 1., 0., 1., 3., 0., 1., 1., 0.
{rotation_axis}, {rotation_angle}
*Solid Section, elset=FIBRE, material=FIBRE_MAT, orientation=FIBRE_ORIENTATION
,
*Solid Section, elset=MATRIX, material=MATRIX_MAT
,
*End Part
""",
        encoding="utf-8",
    )
    return str(filename)


def _write_2d_direct_orientation_input(tmp_path, rotation_axis: int) -> str:
    """Write a minimal 2D input with one additional orientation rotation."""
    filename = tmp_path / "direct_orientation_2d.inp"
    filename.write_text(
        f"""*Heading
*Part, name=RVE
*Node
1, 0., 0.
2, 1., 0.
3, 1., 1.
4, 0., 1.
*Element, type=CPE4, elset=FIBRE
1, 1, 2, 3, 4
*Material, name=FIBRE_MAT
*Elastic
1.0, 0.3
*Orientation, name=FIBRE_ORIENTATION
1., 0., 0., 0., 1., 0.
{rotation_axis}, 45.
*Solid Section, elset=FIBRE, material=FIBRE_MAT, orientation=FIBRE_ORIENTATION
,
*End Part
""",
        encoding="utf-8",
    )
    return str(filename)


def _write_2d_direct_orientation_without_rotation(tmp_path) -> str:
    """Write a minimal 2D input using Abaqus's default axis and angle."""
    filename = tmp_path / "direct_orientation_2d_default_rotation.inp"
    filename.write_text(
        """*Heading
*Part, name=RVE
*Node
1, 0., 0.
2, 1., 0.
3, 1., 1.
4, 0., 1.
*Element, type=CPE4, elset=FIBRE
1, 1, 2, 3, 4
*Material, name=FIBRE_MAT
*Elastic
1.0, 0.3
*Orientation, name=FIBRE_ORIENTATION
1., 0., 0., 0., 1., 0.
*Solid Section, elset=FIBRE, material=FIBRE_MAT, orientation=FIBRE_ORIENTATION
,
*End Part
""",
        encoding="utf-8",
    )
    return str(filename)


def _write_distribution_orientation_input(tmp_path, *, use_input_file: bool = False) -> str:
    """Write a 3D input with one distribution override and one defaulted element.

    Element 1 gets an explicit distribution row; element 2 has none and must
    fall back to the blank-label default row. With ``use_input_file=True``
    those rows live entirely in an external ``Input=`` file instead of
    inline under the ``*Distribution`` keyword -- the same
    ``*Distribution Table`` / ``*Orientation`` / ``*Solid Section`` wiring
    covers both read paths.
    """
    distribution_rows = ", 0., 1., 0., -1., 0., 0.\n1, 1., 0., 0., 0., 1., 0.\n"

    if use_input_file:
        (tmp_path / "orientation.ori").write_text(distribution_rows, encoding="utf-8")
        distribution_card = (
            "*Distribution, name=FIBRE_DISTRIBUTION, location=ELEMENT, "
            "Table=ORIENTATION_TABLE, Input=orientation.ori\n"
        )
    else:
        distribution_card = (
            "*Distribution, name=FIBRE_DISTRIBUTION, location=ELEMENT, Table=ORIENTATION_TABLE\n"
            + distribution_rows
        )

    filename = tmp_path / "distribution_orientation.inp"
    filename.write_text(
        f"""*Heading
*Part, name=RVE
*Node
1, 0., 0., 0.
2, 1., 0., 0.
3, 0., 1., 0.
4, 0., 0., 1.
5, 1., 1., 1.
*Element, type=C3D4, elset=FIBRE
1, 1, 2, 3, 4
2, 2, 3, 4, 5
*Distribution Table, name=ORIENTATION_TABLE
coord3D, coord3D
{distribution_card}*Orientation, name=FIBRE_ORIENTATION
FIBRE_DISTRIBUTION
3, 0.
*Solid Section, elset=FIBRE, material=FIBRE_MAT, orientation=FIBRE_ORIENTATION
,
*End Part
*Material, name=FIBRE_MAT
*Elastic
1.0, 0.3
""",
        encoding="utf-8",
    )
    return str(filename)


def _write_missing_orientation_input(tmp_path) -> str:
    """Write a minimal input whose section references an unknown orientation."""
    filename = tmp_path / "missing_orientation.inp"
    filename.write_text(
        """*Heading
*Part, name=RVE
*Node
1, 0., 0., 0.
2, 1., 0., 0.
3, 0., 1., 0.
4, 0., 0., 1.
*Element, type=C3D4, elset=FIBRE
1, 1, 2, 3, 4
*Solid Section, elset=FIBRE, material=FIBRE_MAT, orientation=MISSING_ORIENTATION
,
*End Part
*Material, name=FIBRE_MAT
*Elastic
1.0, 0.3
""",
        encoding="utf-8",
    )
    return str(filename)


@pytest.mark.unit
def test_map_input_to_structure_gene_builds_structure_gene(abaqus_test_files):
    """Mapper should convert parsed Abaqus payload into a populated SG."""
    fixture = abaqus_test_files["root"] / "sg2_min.inp"

    parsed = parse_input_file(str(fixture), sgdim=2, model="PL1")
    sg = map_input_to_structure_gene(parsed)

    assert sg.sgdim == 2
    assert sg.smdim == 2
    assert sg.analysis_config.model == 0
    assert sg.mesh is not None
    assert len(sg.mesh.points) > 0
    assert "node_id" in sg.mesh.point_data
    assert "property_id" in sg.mesh.cell_data
    assert sg.materials
    assert sg.mocombos


@pytest.mark.unit
def test_map_input_to_structure_gene_maps_2d_discrete_orientations_to_vabs_angles(
    abaqus_test_files,
):
    """2D Abaqus discrete orientations should preserve sectional in-plane angles."""
    fixture = abaqus_test_files["root"] / "sg2_i_simple_eo1.inp"

    parsed = parse_input_file(str(fixture), sgdim=2, model="BM2")
    sg = map_input_to_structure_gene(parsed)

    element_to_expected_theta = {
        41: 180.0,
        46: 90.0,
        86: -90.0,
        70: 0.0,
    }

    # The Abaqus mapper stores property_ref_csys in the source (Abaqus xy)
    # frame; ``model_space='xy'`` resolves it to the VABS theta_1.
    theta_by_element_id: dict[int, float] = {}
    for block_index, element_ids in enumerate(sg.mesh.cell_data["element_id"]):
        for element_index, element_id in enumerate(element_ids):
            theta_by_element_id[int(element_id)] = property_ref_value_to_vabs_theta(
                sg.mesh.cell_data["property_ref_csys"][block_index][element_index],
                model_space="xy",
            )

    for element_id, expected_theta in element_to_expected_theta.items():
        assert element_id in theta_by_element_id
        assert theta_by_element_id[element_id] == pytest.approx(expected_theta)


@pytest.mark.unit
def test_map_input_to_structure_gene_maps_direct_3d_orientation_to_global_default(
    abaqus_test_files,
):
    """A direct global 3D orientation should equal the no-orientation default."""
    fixture = abaqus_test_files["root"] / "sg33_ud_fiber_direct_orientation_bug.inp"

    parsed = parse_input_file(str(fixture), sgdim=3, model="SD1")
    sg = map_input_to_structure_gene(parsed)

    expected_element_ids = set(sg.mesh.cell_sets["FIBRE"]) | set(sg.mesh.cell_sets["MATRIX"])
    expected_csys = np.array([1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])

    for element_ids, csys_block in zip(
        sg.mesh.cell_data["element_id"],
        sg.mesh.cell_data["property_ref_csys"],
    ):
        for element_id, csys in zip(element_ids, csys_block):
            if int(element_id) in expected_element_ids:
                assert np.allclose(csys, expected_csys)


@pytest.mark.unit
def test_map_input_to_structure_gene_applies_2d_orientation_axis_3_rotation(
    abaqus_test_files,
):
    """Abaqus axis-3 rotation should become the 2D sectional orientation."""
    fixture = abaqus_test_files["root"] / "sg31_rec_ori_discrete.inp"

    parsed = parse_input_file(str(fixture), sgdim=2, model="BM2")
    sg = map_input_to_structure_gene(parsed)

    csys = sg.mesh.cell_data["property_ref_csys"][0][0]
    theta = property_ref_value_to_vabs_theta(csys, model_space="xy")

    assert theta == pytest.approx(45.0)


@pytest.mark.unit
def test_map_input_to_structure_gene_accepts_default_2d_orientation_rotation(tmp_path):
    """A missing Abaqus rotation row defaults to axis 1 and zero degrees."""
    filename = _write_2d_direct_orientation_without_rotation(tmp_path)
    parsed = parse_input_file(filename, sgdim=2, model="BM2")

    sg = map_input_to_structure_gene(parsed)

    csys = sg.mesh.cell_data["property_ref_csys"][0][0]
    assert np.allclose(csys, [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    assert sg.orientations["FIBRE_ORIENTATION"].extras["axis"] == 1
    assert sg.orientations["FIBRE_ORIENTATION"].angle == pytest.approx(0.0)


@pytest.mark.unit
def test_map_input_to_structure_gene_binds_direct_orientation_to_its_section(tmp_path):
    """A direct 9-value orientation applies only to its section and retains ``c``."""
    parsed = parse_input_file(_write_direct_orientation_input(tmp_path), sgdim=3, model="SD1")

    sg = map_input_to_structure_gene(parsed)

    csys_by_element_id = dict(
        zip(
            sg.mesh.cell_data["element_id"][0],
            sg.mesh.cell_data["property_ref_csys"][0],
        )
    )
    assert np.allclose(csys_by_element_id[1], [2.0, 1.0, 0.0, 1.0, 2.0, 0.0, 1.0, 1.0, 0.0])
    assert np.allclose(csys_by_element_id[2], [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])


@pytest.mark.unit
def test_map_input_to_structure_gene_rejects_nonrectangular_orientation(tmp_path):
    """Unsupported Abaqus orientation systems must not be interpreted as rectangular."""
    filename = _write_direct_orientation_input(tmp_path, ", SYSTEM=CYLINDRICAL")
    parsed = parse_input_file(filename, sgdim=3, model="SD1")

    with pytest.raises(ValueError, match="FIBRE_ORIENTATION.*CYLINDRICAL"):
        map_input_to_structure_gene(parsed)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("orientation_options", "message"),
    [
        (", DEFINITION=OFFSET TO NODES", "definition='OFFSET TO NODES'"),
        (", SYSTEM=Z RECTANGULAR", "system='Z RECTANGULAR'"),
        (", LOCAL DIRECTIONS", "LOCAL DIRECTIONS"),
        (", DISPERSION", "DISPERSION"),
    ],
)
def test_map_input_to_structure_gene_rejects_unsupported_orientation_syntax(
    tmp_path,
    orientation_options,
    message,
):
    """Unsupported Abaqus orientation syntax must report its semantic cause."""
    filename = _write_direct_orientation_input(tmp_path, orientation_options)
    parsed = parse_input_file(filename, sgdim=3, model="SD1")

    with pytest.raises(ValueError, match=message):
        map_input_to_structure_gene(parsed)


@pytest.mark.unit
def test_map_input_to_structure_gene_applies_distribution_default_and_override(tmp_path):
    """A distribution default must fill elements without an explicit record."""
    parsed = parse_input_file(_write_distribution_orientation_input(tmp_path), sgdim=3, model="SD1")

    sg = map_input_to_structure_gene(parsed)

    csys_by_element_id = dict(
        zip(
            sg.mesh.cell_data["element_id"][0],
            sg.mesh.cell_data["property_ref_csys"][0],
        )
    )
    assert np.allclose(csys_by_element_id[1], [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
    assert np.allclose(csys_by_element_id[2], [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0])


@pytest.mark.unit
def test_map_input_to_structure_gene_reads_distribution_input_file(abaqus_test_files):
    """A ``*Distribution`` with ``Input=<file>`` must read that file, not go empty.

    Regression fixture: ``sg33_cube_distribution_input_bug.inp`` has 3 elements
    -- 1 isotropic Matrix (no orientation) and 2 orthotropic Yarn elements whose
    orientation comes from a ``*Distribution`` table stored entirely in the
    external ``.ori`` file (nothing under the keyword in the ``.inp`` itself).
    The two Yarn elements are given deliberately different fibre directions
    (+X and +Y) so a reader that drops the external file collapses them onto
    one orientation instead of raising -- the silent 0.7.0 failure mode.
    """
    fixture = abaqus_test_files["root"] / "sg33_cube_distribution_input_bug.inp"

    parsed = parse_input_file(str(fixture), sgdim=3, model="SD1")
    sg = map_input_to_structure_gene(parsed)

    csys_by_element_id = dict(
        zip(
            sg.mesh.cell_data["element_id"][0],
            sg.mesh.cell_data["property_ref_csys"][0],
        )
    )

    # Element 1 (Matrix) has no orientation -> the global default.
    assert np.allclose(csys_by_element_id[1], [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
    # Element 2 (Yarn, fibre +X per the .ori file) and element 3 (fibre +Y)
    # must resolve to their own, distinct rows from the external file.
    assert np.allclose(csys_by_element_id[2], [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
    assert np.allclose(csys_by_element_id[3], [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    assert not np.allclose(csys_by_element_id[2], csys_by_element_id[3])


@pytest.mark.unit
def test_map_input_to_structure_gene_applies_input_file_distribution_default(tmp_path):
    """A distribution read from an external Input= file must keep its real default.

    The external file's own trailing newline produces one spurious, all-blank
    row after the real data rows; if that row is mistaken for the (also
    blank-label) default row it silently replaces the real default with an
    empty coordinate list, which then breaks the element that needed it.
    """
    parsed = parse_input_file(
        _write_distribution_orientation_input(tmp_path, use_input_file=True),
        sgdim=3, model="SD1",
    )

    sg = map_input_to_structure_gene(parsed)

    csys_by_element_id = dict(
        zip(
            sg.mesh.cell_data["element_id"][0],
            sg.mesh.cell_data["property_ref_csys"][0],
        )
    )
    assert np.allclose(csys_by_element_id[1], [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
    # Element 2 has no explicit row -- must fall back to the real default,
    # not the spurious trailing blank row.
    assert np.allclose(csys_by_element_id[2], [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0])


@pytest.mark.unit
def test_map_input_to_structure_gene_reports_unknown_section_orientation(tmp_path):
    """A missing section orientation must not leak a bare ``KeyError``."""
    parsed = parse_input_file(_write_missing_orientation_input(tmp_path), sgdim=3, model="SD1")

    with pytest.raises(ValueError, match="unknown orientation 'MISSING_ORIENTATION'"):
        map_input_to_structure_gene(parsed)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("rotation_axis", "message"),
    [
        (1, "tilts the section normal"),
        (2, "section/material combo assignment"),
    ],
)
def test_map_input_to_structure_gene_rejects_unsupported_2d_orientation_rotations(
    tmp_path,
    rotation_axis,
    message,
):
    """2D rotations that cannot map to the property frame must fail clearly."""
    filename = _write_2d_direct_orientation_input(tmp_path, rotation_axis)
    parsed = parse_input_file(filename, sgdim=2, model="BM2")

    with pytest.raises(ValueError, match=message):
        map_input_to_structure_gene(parsed)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("rotation_axis", "expected_axes"),
    [
        (1, ([1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, -1.0, 0.0])),
        (2, ([0.0, 0.0, -1.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0])),
        (3, ([0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 1.0])),
    ],
)
def test_map_input_to_structure_gene_applies_3d_orientation_rotation_about_local_axis(
    tmp_path,
    rotation_axis,
    expected_axes,
):
    """Each 3D Abaqus local rotation axis must follow the right-hand rule."""
    filename = _write_direct_orientation_input(
        tmp_path,
        rotation_axis=rotation_axis,
        rotation_angle=90.0,
    )
    parsed = parse_input_file(filename, sgdim=3, model="SD1")

    sg = map_input_to_structure_gene(parsed)

    csys = sg.mesh.cell_data["property_ref_csys"][0][0]
    actual_axes = property_ref_csys_to_axes(csys)
    for actual_axis, expected_axis in zip(actual_axes, expected_axes):
        assert np.allclose(actual_axis, expected_axis)


def _write_material_input(tmp_path, elastic_data: str) -> str:
    """Write a minimal 2D input with a customizable ``*Elastic`` data line."""
    filename = tmp_path / "material.inp"
    filename.write_text(
        f"""*Heading
*Part, name=RVE
*Node
1, 0., 0.
2, 1., 0.
3, 1., 1.
4, 0., 1.
*Element, type=CPE4, elset=FIBRE
1, 1, 2, 3, 4
*Material, name=FIBRE_MAT
*Elastic
{elastic_data}
*Solid Section, elset=FIBRE, material=FIBRE_MAT
,
*End Part
""",
        encoding="utf-8",
    )
    return str(filename)


@pytest.mark.unit
def test_map_input_to_structure_gene_ignores_trailing_comma_blank_cell(tmp_path):
    """A trailing comma on the last populated *Elastic data line produces one
    blank cell; it must be skipped, not treated as an invalid constant."""
    filename = _write_material_input(tmp_path, "1.0, 0.3,")

    sg = map_input_to_structure_gene(parse_input_file(filename, sgdim=2, model="BM2"))

    assert sg.materials["FIBRE_MAT"].e == pytest.approx(1.0)


@pytest.mark.unit
def test_map_input_to_structure_gene_rejects_invalid_elastic_constant(tmp_path):
    """A genuinely non-numeric *Elastic constant must raise, not be dropped
    silently -- unlike a trailing-comma blank cell, this is real data loss."""
    filename = _write_material_input(tmp_path, "1.0, not_a_number")

    with pytest.raises(ValueError, match="Invalid elastic constant"):
        map_input_to_structure_gene(parse_input_file(filename, sgdim=2, model="BM2"))


def _write_composite_section_input(tmp_path, angle_token: str) -> str:
    """Write a minimal 2D input with a customizable composite ply angle."""
    filename = tmp_path / "composite_section.inp"
    filename.write_text(
        f"""*Heading
*Part, name=RVE
*Node
1, 0., 0.
2, 1., 0.
3, 1., 1.
4, 0., 1.
*Element, type=CPE4, elset=FIBRE
1, 1, 2, 3, 4
*Material, name=FIBRE_MAT
*Elastic
1.0, 0.3
*Orientation, name=Ori-1
1., 0., 0., 0., 1., 0.
*Solid Section, elset=FIBRE, composite, orientation=Ori-1
1., 1, FIBRE_MAT, {angle_token}, Ply-1
*End Part
""",
        encoding="utf-8",
    )
    return str(filename)


@pytest.mark.unit
def test_map_input_to_structure_gene_rejects_invalid_composite_ply_angle(tmp_path):
    """A composite ply row that has an angle column but it is not numeric
    must raise, not silently default to 0 degrees like a genuinely absent
    angle would."""
    filename = _write_composite_section_input(tmp_path, "not_an_angle")

    with pytest.raises(ValueError, match="orientation angle"):
        map_input_to_structure_gene(parse_input_file(filename, sgdim=2, model="BM2"))


@pytest.mark.unit
def test_map_input_to_structure_gene_defaults_composite_ply_angle_when_numeric(tmp_path):
    """Sanity check: a real numeric composite ply angle still works."""
    filename = _write_composite_section_input(tmp_path, "30.")

    sg = map_input_to_structure_gene(parse_input_file(filename, sgdim=2, model="BM2"))

    assert list(sg.mocombos.values())[0][1] == pytest.approx(30.0)
