"""Tests for VABS <-> Gmsh format conversion."""
from __future__ import annotations

import os
import re
from pathlib import Path

import numpy as np
import pytest
import yaml

from sgio import convert, configure_logging, logger, read, read_sg_from_gmsh_bundle, write

configure_logging(cout_level='info')

_YML = 'test_convert_vabs_gmsh.yml'


def _load_test_cases(test_data_dir: Path) -> list[dict]:
    path = test_data_dir / 'yaml' / _YML
    if not path.exists():
        path = test_data_dir / _YML
    if not path.exists():
        legacy = Path(__file__).parent.parent / 'files' / _YML
        if legacy.exists():
            path = legacy
        else:
            pytest.skip(f'Test case file not found: {_YML}')
    with open(path) as f:
        return yaml.safe_load(f)


def _resolve_input(fn_rel: str, test_data_dir: Path) -> str:
    fn = str(test_data_dir / fn_rel)
    if not Path(fn).exists():
        fn = str(Path(__file__).parent.parent / 'files' / fn_rel)
    return fn


@pytest.mark.conversion
@pytest.mark.gmsh
def test_vabs_gmsh_conversion(test_data_dir, capsys):
    """Test VABS <-> Gmsh file format conversion."""
    with capsys.disabled():
        test_cases = _load_test_cases(test_data_dir)
        output_dir = Path(__file__).parent.parent / '_temp'
        os.makedirs(output_dir, exist_ok=True)

        for _case in test_cases:
            fn_in = _resolve_input(_case['fn_in'], test_data_dir)
            fn_out = str(output_dir / _case['fn_out'])

            logger.info(f'Converting {fn_in} to {fn_out}...')
            convert(
                fn_in, fn_out,
                _case['ff_in'], _case['ff_out'],
                file_version_in=_case.get('version_in'),
                file_version_out=_case.get('version_out'),
                model_type=_case.get('model'),
            )

            assert os.path.exists(fn_out), f'Output file was not created: {fn_out}'
            assert os.path.getsize(fn_out) > 0, f'Output file is empty: {fn_out}'

            if _case.get('solver'):
                pytest.skip('Solver execution skipped (requires external tool)')


@pytest.mark.conversion
@pytest.mark.gmsh
def test_convert_to_gmsh(test_data_dir, capsys):
    """Test conversion to Gmsh format."""
    with capsys.disabled():
        test_cases = _load_test_cases(test_data_dir)
        gmsh_cases = [c for c in test_cases if c.get('ff_out') == 'gmsh']

        if not gmsh_cases:
            pytest.skip('No Gmsh output test cases found')

        output_dir = Path(__file__).parent.parent / '_temp'
        os.makedirs(output_dir, exist_ok=True)

        for _case in gmsh_cases:
            fn_in = _resolve_input(_case['fn_in'], test_data_dir)
            fn_out = str(output_dir / _case['fn_out'])

            convert(
                fn_in, fn_out,
                _case['ff_in'], _case['ff_out'],
                file_version_in=_case.get('version_in'),
                file_version_out=_case.get('version_out'),
                model_type=_case.get('model'),
            )

            assert os.path.exists(fn_out), f'Output file was not created: {fn_out}'
            assert os.path.getsize(fn_out) > 0, f'Output file is empty: {fn_out}'


@pytest.mark.conversion
@pytest.mark.gmsh
@pytest.mark.vabs
def test_gmsh_xy_section_converts_to_vabs(test_data_dir, temp_dir):
    """A Gmsh section mesh in the ``xy`` plane should convert to VABS."""
    src = test_data_dir / 'gmsh' / 'laminate_simple.msh'
    sections = test_data_dir / 'gmsh' / 'sections_laminate_simple.json'
    dst = temp_dir / 'laminate_simple_xy.sg'

    source_sg = read(
        str(src), 'gmsh', format_version='4.1', sgdim=2, model_type='BM2',
        sections_json=str(sections),
    )

    convert(
        str(src),
        str(dst),
        'gmsh',
        'vabs',
        file_version_in='4.1',
        file_version_out='4.1',
        sgdim=2,
        model_space='xy',
        model_type='BM2',
        sections_json=str(sections),
    )

    assert dst.exists(), f'Output file was not created: {dst}'
    assert dst.stat().st_size > 0, f'Output file is empty: {dst}'

    roundtrip = read(str(dst), 'vabs', format_version='4.1', model_type='BM2')
    np.testing.assert_allclose(roundtrip.mesh.points[:, 0], 0.0)
    np.testing.assert_allclose(roundtrip.mesh.points[:, 1], source_sg.mesh.points[:, 0])
    np.testing.assert_allclose(roundtrip.mesh.points[:, 2], source_sg.mesh.points[:, 1])


@pytest.mark.conversion
@pytest.mark.gmsh
@pytest.mark.vabs
@pytest.mark.parametrize(
    ('model_space', 'expected_axes'),
    [('xy', (0, 1)), ('yz', (1, 2)), ('zx', (2, 0))],
)
def test_gmsh_to_vabs_respects_model_space_projection(
    test_data_dir,
    temp_dir,
    model_space,
    expected_axes,
):
    """Gmsh -> VABS conversion should project nodes onto the requested section plane."""
    src = test_data_dir / 'gmsh' / 'laminate_simple.msh'
    sections = test_data_dir / 'gmsh' / 'sections_laminate_simple.json'
    dst = temp_dir / f'laminate_simple_{model_space}.sg'

    source_sg = read(
        str(src), 'gmsh', format_version='4.1', sgdim=2, model_type='BM2',
        sections_json=str(sections),
    )

    convert(
        str(src),
        str(dst),
        'gmsh',
        'vabs',
        file_version_in='4.1',
        file_version_out='4.1',
        sgdim=2,
        model_space=model_space,
        model_type='BM2',
        sections_json=str(sections),
    )

    roundtrip = read(str(dst), 'vabs', format_version='4.1', model_type='BM2')
    expected_points = source_sg.mesh.points[:, expected_axes]

    np.testing.assert_allclose(roundtrip.mesh.points[:, 0], 0.0)
    np.testing.assert_allclose(roundtrip.mesh.points[:, 1], expected_points[:, 0])
    np.testing.assert_allclose(roundtrip.mesh.points[:, 2], expected_points[:, 1])


@pytest.mark.conversion
@pytest.mark.gmsh
@pytest.mark.vabs
def test_laminate_simple_bundle_to_vabs(test_data_dir, temp_dir):
    """Convert the laminate_simple Gmsh bundle to VABS and validate the full payload.

    Bundle inputs (Gmsh ``xy`` plane):

    * ``laminate_simple.msh`` — mesh + ``element_local_csys`` +
      ``additional_rotation_2`` (= 30° on every element)
    * ``sections.json`` — one orthotropic material ``mat_1`` (label 1)
    * ``config.json`` — Euler-Bernoulli homogenization config (model=1)

    The test exercises the key invariants of the Gmsh-bundle → VABS path:

    1. Coordinate projection ``xy → yz``: the Gmsh ``z`` is dropped, Gmsh
       ``x`` becomes VABS ``x2`` and Gmsh ``y`` becomes VABS ``x3``.
    2. ``additional_rotation_2`` collapses into the layer ``theta_3`` (30°).
    3. The sidecar material from ``sections.json`` is bound to the layer; the
       VABS file references it instead of the Gmsh physical-group name.
    4. ``element_local_csys`` / ``property_ref_csys`` survive the bundle read
       and drive the per-element ``theta_1`` written to VABS.
    """
    bundle_dir = test_data_dir / 'gmsh'
    main_msh = bundle_dir / 'laminate_simple.msh'
    sections_json = bundle_dir / 'sections.json'
    config_json = bundle_dir / 'config.json'
    dst = temp_dir / 'laminate_simple.sg'

    # --- Read bundle and inspect SG state ---------------------------------
    sg = read_sg_from_gmsh_bundle(
        main_msh=main_msh,
        sections_json=sections_json,
        config_json=config_json,
        model_type='BM1',
    )

    # Bundle config.json drives the analysis config
    assert sg.sgdim == 2
    assert sg.analysis_config.model == 1

    # The read step preserves the raw per-element rotation field; folding into
    # ``theta_3`` happens at write time because it depends on ``model_space``.
    assert dict(sg.mocombos) == {1: ('mat_1', 0.0)}
    np.testing.assert_allclose(
        sg.mesh.cell_data['additional_rotation_2'][0], 30.0
    )
    assert 'mat_1' in sg.materials
    assert sg.materials['mat_1'].e1 == pytest.approx(140e9)

    # element_local_csys is preserved by the Gmsh reader and mirrored into
    # property_ref_csys so the VABS writer can map it to theta_1.
    csys_block = np.asarray(sg.mesh.cell_data['element_local_csys'][0])
    assert csys_block.shape == (53, 9)
    np.testing.assert_array_equal(
        sg.mesh.cell_data['property_ref_csys'][0], csys_block
    )

    # --- Write to VABS using xy → yz projection ---------------------------
    write(
        sg=sg,
        filename=str(dst),
        file_format='vabs',
        model_type='BM1',
        model_space='xy',
    )

    # --- Re-read the VABS file and validate the on-disk contract ----------
    vabs_sg = read(str(dst), 'vabs', format_version='4.1', model_type='BM1')

    # Projection: Gmsh xy nodes → VABS yz nodes (VABS x1 is zero).
    np.testing.assert_allclose(vabs_sg.mesh.points[:, 0], 0.0)
    np.testing.assert_allclose(vabs_sg.mesh.points[:, 1], sg.mesh.points[:, 0])
    np.testing.assert_allclose(vabs_sg.mesh.points[:, 2], sg.mesh.points[:, 1])

    # Layer line ``layer_id  mate_id  theta_3`` must carry the 30° angle.
    text = dst.read_text(encoding='utf-8')
    layer_line = re.search(
        r'^\s*(\d+)\s+(\d+)\s+([-\d.eE+]+)\s+! combination id,',
        text,
        re.MULTILINE,
    )
    assert layer_line is not None, 'VABS layer header line missing'
    layer_id, mat_id, theta_3 = layer_line.groups()
    assert int(layer_id) == 1
    assert float(theta_3) == pytest.approx(30.0)

    # The referenced mate_id resolves to the sidecar material (mat_1) and not
    # to the physical-group placeholder. ``build_material_id_map`` is the
    # same mapping the VABS writer uses.
    from sgio.iofunc.common import build_material_id_map
    material_id_map = build_material_id_map(sg.materials)
    name_by_id = {mid: name for name, mid in material_id_map.items()}
    assert name_by_id[int(mat_id)] == 'mat_1'

    # ``element_local_csys`` is stored in the Gmsh xy frame. The writer maps
    # each local y2 axis into the VABS x2-x3 plane via model_space='xy' and
    # writes the per-element ``theta_1``. The fixture has two distinct frames:
    # ``b = (1, 0, 0)`` -> theta_1 = 0°, ``b = (0.707, 0.707, 0)`` -> 45°.
    assert len(np.unique(sg.mesh.cell_data['element_local_csys'][0], axis=0)) == 2
    theta_1_values = sorted({
        float(match.group(1))
        for match in re.finditer(
            r'^\s*\d+\s+1\s+([-\d.eE+]+)\s*$', text, re.MULTILINE
        )
    })
    assert theta_1_values == [pytest.approx(0.0), pytest.approx(45.0)]
