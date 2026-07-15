"""Test stiffness/compliance matrix heatmap plotting.

Test cases are driven by the shared output-model fixtures
``tests/fixtures/test_io_sc_out_model.yml`` (SwiftComp) and
``tests/fixtures/test_io_vabs_out_model.yml`` (VABS). For every case the
homogenization output file is read into its constitutive model and the
stiffness / compliance matrices are rendered as annotated symmetric-log
heatmaps via :func:`sgio.plot_model_matrix`.

Each generated figure is written to ``tests/visualization/outputs/`` for
visual inspection.

Cases whose model type the reader does not yet support (e.g. Reissner-Mindlin
``PL2``) are reported as skips rather than failures.
"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for testing
import matplotlib.pyplot as plt
import numpy as np
import pytest
import yaml

from sgio import read_output_model, plot_matrix_bar3d, plot_model_matrix
from sgio.visualization.matrix import _extract_model_matrix

# Directory where generated matrix plots are saved.
OUTPUT_DIR = Path(__file__).parent / "outputs"

# Fixture case lists shared with the I/O tests.
_CASE_FILES = {
    'sc': 'test_io_sc_out_model.yml',
    'vabs': 'test_io_vabs_out_model.yml',
}


def _load_cases(fixtures_dir: Path):
    """Load and flatten the SwiftComp + VABS output-model fixture cases."""
    cases = []
    for _fmt, fname in _CASE_FILES.items():
        with open(fixtures_dir / fname) as fp:
            for case in yaml.safe_load(fp):
                cases.append(case)
    return cases


def _case_id(case: dict) -> str:
    """Readable pytest id for a fixture case."""
    stem = case.get('fn_base') or Path(case['fn']).name
    return f"{case['file_format']}-{case['model']}-{stem}"


def _input_path(case: dict, fixtures_dir: Path) -> Path:
    """Resolve the output file path for a fixture case."""
    base_dir = fixtures_dir / case['dir']
    if 'fn' in case:
        return base_dir / case['fn']
    # SwiftComp results use '.sg.k'; VABS results use '.sg.K'.
    ext = '.sg.k' if case['file_format'] == 'sc' else '.sg.K'
    return base_dir / f"{case['fn_base']}{ext}"


# Fixtures live under tests/fixtures; resolve relative to this test file so the
# parametrization can run at collection time.
_FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
_ALL_CASES = _load_cases(_FIXTURES_DIR)


@pytest.fixture(scope="session", autouse=True)
def _ensure_output_dir():
    """Make sure the plot output directory exists."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(params=_ALL_CASES, ids=[_case_id(c) for c in _ALL_CASES])
def loaded_model(request, test_data_dir):
    """Read one output model from a fixture case.

    Skips cases whose file is missing or whose model type the reader does not
    support (the model comes back as ``None`` or raises).
    """
    case = request.param
    fn_in = _input_path(case, test_data_dir)
    if not fn_in.exists():
        pytest.skip(f"Fixture file not found: {fn_in}")

    try:
        model = read_output_model(str(fn_in), case['file_format'], model_type=case['model'])
    except Exception as exc:  # reader limitation, not a plotting failure
        pytest.skip(f"Reader could not parse {fn_in.name}: {exc}")

    if model is None:
        pytest.skip(f"Model type {case['model']!r} not supported for {fn_in.name}")

    return model, case


@pytest.mark.visualization
@pytest.mark.io
@pytest.mark.parametrize('kind', ['stiffness', 'compliance'])
def test_extract_model_matrix(loaded_model, kind):
    """Matrix and physical labels are extracted consistently."""
    model, _case = loaded_model

    matrix, row_labels, col_labels = _extract_model_matrix(model, kind)

    assert isinstance(matrix, np.ndarray)
    assert matrix.ndim == 2
    assert np.all(np.isfinite(matrix))
    # Labels (schema-based for sections, Voigt for solids) match the shape.
    assert row_labels is not None and col_labels is not None
    assert len(row_labels) == matrix.shape[0]
    assert len(col_labels) == matrix.shape[1]


@pytest.mark.visualization
@pytest.mark.io
def test_plot_and_save_matrix(loaded_model):
    """Render stiffness + compliance heatmaps side by side and save a PNG."""
    model, case = loaded_model

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), layout='constrained')
    stem = case.get('fn_base') or Path(case['fn']).stem
    try:
        for ax, kind in zip(axes, ('stiffness', 'compliance')):
            plot_model_matrix(
                model, kind=kind, fig=fig, ax=ax,
                title=f"{stem} [{case['model']}]\n{kind}",
            )
            assert len(ax.images) == 1  # one heatmap drawn

        out_file = OUTPUT_DIR / f"{stem}_{case['file_format']}_matrix.png"
        fig.savefig(out_file, dpi=110)
        assert out_file.exists() and out_file.stat().st_size > 0
    finally:
        plt.close(fig)


@pytest.mark.visualization
@pytest.mark.io
def test_plot_and_save_matrix_bar3d(loaded_model):
    """Render stiffness + compliance as 3D bar charts and save a PNG."""
    model, case = loaded_model
    stem = case.get('fn_base') or Path(case['fn']).stem

    fig = plt.figure(figsize=(14, 6))
    try:
        for idx, kind in enumerate(('stiffness', 'compliance'), start=1):
            matrix, row_labels, col_labels = _extract_model_matrix(model, kind)
            ax = fig.add_subplot(1, 2, idx, projection='3d')
            bars = plot_matrix_bar3d(
                matrix, fig=fig, ax=ax,
                row_labels=row_labels, col_labels=col_labels,
            )
            ax.set_title(f"{stem} [{case['model']}]\n{kind}")
            assert bars is not None

        out_file = OUTPUT_DIR / f"{stem}_{case['file_format']}_bar3d.png"
        fig.savefig(out_file, dpi=110)
        assert out_file.exists() and out_file.stat().st_size > 0
    finally:
        plt.close(fig)


@pytest.mark.visualization
def test_plot_matrix_bar3d_requires_3d_axes(loaded_model):
    """Passing a non-3D axes to bar3d raises ValueError."""
    model, _case = loaded_model
    matrix, _rl, _cl = _extract_model_matrix(model, 'stiffness')
    fig, ax = plt.subplots()  # 2D axes
    try:
        with pytest.raises(ValueError):
            plot_matrix_bar3d(matrix, fig=fig, ax=ax)
    finally:
        plt.close(fig)


@pytest.mark.visualization
def test_plot_model_matrix_invalid_kind(loaded_model):
    """An unknown matrix kind raises ValueError."""
    model, _case = loaded_model
    with pytest.raises(ValueError):
        plot_model_matrix(model, kind='not-a-kind')
