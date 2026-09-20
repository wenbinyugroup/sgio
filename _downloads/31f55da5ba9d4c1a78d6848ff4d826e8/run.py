"""Export blade cross-section failure results to ParaView.

For every cross-section listed in ``blade.csv`` this script:

1. reads the VABS Structure Gene mesh (``*.sg``),
2. reads the VABS failure output (``*.sg.fi``) -- per-element *failure index*
   and *strength ratio*,
3. attaches those fields as cell data on the mesh,
4. places the 2D section at its spanwise location along the blade axis (x1),
5. bridges the mesh to a ``pyvista`` grid (:meth:`SGMesh.to_pyvista`).

All sections are collected into a single ParaView MultiBlock file
(``blade_fi.vtm``). Open it in ParaView and color by ``failure_index`` or
``strength_ratio`` to see the field on every section of the whole blade.

pyvista is an optional dependency::

    pip install sgio[pyvista]
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pyvista as pv

import sgio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("view_css_fi")

CWD = Path(__file__).resolve().parent

# VABS writes sys.float_info.max as the strength ratio of elements that carry
# no load (infinite margin); mask it so it does not swamp the color scale.
_SR_SENTINEL = 1e300

# The failure output header is a VABS 4.1+ style line; tell the reader to skip
# it. See sgio.read_output_state(..., tool_version=...).
_TOOL_VERSION = "4.1"


def _load_section_grid(location: float, cs_name: str) -> pv.UnstructuredGrid:
    """Read one section + its failure output and return a pyvista grid."""
    sg_path = CWD / "blade1" / cs_name / f"{cs_name}.sg"

    # 1. Structure Gene mesh (2D cross-section; points are (x1=0, x2, x3)).
    sg = sgio.read(
        str(sg_path), file_format="vabs", format_version="4",
        sgdim=2, model_type="BM2",
    )
    mesh = sg.mesh

    # 2. Failure index / strength ratio, per element, for load case 1.
    states = sgio.read_output_state(
        str(sg_path), "vabs", analysis="fi", sg=sg, tool_version=_TOOL_VERSION,
    )
    if not states:
        raise RuntimeError(f"Could not read failure output for {cs_name}")
    case = states[0]
    fi = case.getState("fi").data   # {element_id: failure_index}
    sr = case.getState("sr").data   # {element_id: strength_ratio}

    # 3. Attach as element (cell) data. add_cell_data_from_dict expects
    #    {eid: [values]} and uses mesh.cell_data['element_id'] for ordering.
    fi_cell = {eid: [float(v)] for eid, v in fi.items()}
    sr_cell = {
        eid: [float(v) if v < _SR_SENTINEL else np.nan]
        for eid, v in sr.items()
    }
    mesh.add_cell_data_from_dict("failure_index", fi_cell)
    mesh.add_cell_data_from_dict("strength_ratio", sr_cell)

    # 4. Place the section at its spanwise station along the blade axis (x1).
    mesh.points[:, 0] = location

    # 5. Bridge to pyvista (geometry + cell data cross over via meshio).
    return mesh.to_pyvista()


def main() -> None:
    layout = sgio.read_section_layout_csv(str(CWD / "blade.csv"))
    logger.info("Loaded %d sections from blade.csv", len(layout))

    blocks = {
        cs_name: _load_section_grid(location, cs_name)
        for location, cs_name in layout
    }

    multiblock = pv.MultiBlock(blocks)
    out_file = CWD / "blade_fi.vtm"
    multiblock.save(str(out_file))
    logger.info("Wrote %d-block ParaView file: %s", multiblock.n_blocks, out_file)
    print(f"\nOpen in ParaView and color by 'failure_index' or 'strength_ratio':\n  {out_file}")


if __name__ == "__main__":
    main()
