"""Regenerate the minimal bug-reproduction fixtures under tests/fixtures/.

Run from the repository root:

    uv run python tests/fixtures/make_bug_fixtures.py

Each fixture is the smallest input that still triggers one documented defect;
see BUG_FIXTURES.md for what each is expected to do, before and after a fix.
Meshes are deliberately coarse (one element size equal to the whole domain) --
these exercise parser and writer paths, not numerics, so the point is a few
dozen elements rather than tens of thousands.
"""
import json
import os
import sys

import gmsh

_HERE = os.path.dirname(os.path.abspath(__file__))
OUT_GMSH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "gmsh")
OUT_ABQ = sys.argv[2] if len(sys.argv) > 2 else os.path.join(_HERE, "abaqus")
SIZE = 1.0


def _write(path, version):
    gmsh.option.setNumber("Mesh.MshFileVersion", version)
    # Without this, Gmsh stores parametric coordinates for OCC-backed entities,
    # which meshio's MSH 4.0 reader rejects outright ("parametric nodes not
    # implemented") -- a different failure that would mask the one under test.
    gmsh.option.setNumber("Mesh.SaveParametric", 0)
    gmsh.write(path)
    print("wrote", os.path.basename(path))


def cube_with_boundary_group():
    """3D cube: 'matrix' (dim 3) + 'boundary' (dim 2). Coarse on purpose."""
    gmsh.initialize()
    gmsh.model.add("cube_boundary_group")
    box = gmsh.model.occ.addBox(0, 0, 0, SIZE, SIZE, SIZE)
    gmsh.model.occ.synchronize()

    vol = gmsh.model.addPhysicalGroup(3, [box], 1)
    gmsh.model.setPhysicalName(3, vol, "matrix")
    faces = [tag for dim, tag in gmsh.model.getBoundary([(3, box)], combined=True, oriented=False)]
    bnd = gmsh.model.addPhysicalGroup(2, faces, 2)
    gmsh.model.setPhysicalName(2, bnd, "boundary")

    gmsh.option.setNumber("Mesh.MeshSizeMin", SIZE)
    gmsh.option.setNumber("Mesh.MeshSizeMax", SIZE)
    gmsh.model.mesh.generate(3)
    _write(os.path.join(OUT_GMSH, "sg33_cube_boundary_group_bug_min_gmsh41.msh"), 4.1)
    _report(3)
    gmsh.finalize()


def square_with_boundary_group():
    """2D square: 'matrix' (dim 2) + 'boundary' (dim 1) -- the sgdim-1 rule is not 3D-only."""
    gmsh.initialize()
    gmsh.model.add("square_boundary_group")
    surf = gmsh.model.occ.addRectangle(0, 0, 0, SIZE, SIZE)
    gmsh.model.occ.synchronize()

    face = gmsh.model.addPhysicalGroup(2, [surf], 1)
    gmsh.model.setPhysicalName(2, face, "matrix")
    edges = [tag for dim, tag in gmsh.model.getBoundary([(2, surf)], combined=True, oriented=False)]
    bnd = gmsh.model.addPhysicalGroup(1, edges, 2)
    gmsh.model.setPhysicalName(1, bnd, "boundary")

    gmsh.option.setNumber("Mesh.MeshSizeMin", SIZE)
    gmsh.option.setNumber("Mesh.MeshSizeMax", SIZE)
    gmsh.model.mesh.generate(2)
    _write(os.path.join(OUT_GMSH, "sg22_square_boundary_group_bug_min_gmsh41.msh"), 4.1)
    _report(2)
    gmsh.finalize()


def cube_version_variants():
    """Re-emit the existing sg33_cube_tetra4_min_gmsh41 fixture as 4.0 and 2.2.

    Deriving all three from one mesh is the point: a test can assert the same
    node/element counts across every format version, so a version-dispatch or
    mesh-type defect shows up as a mismatch rather than needing its own
    hand-checked expectations.
    """
    source = os.path.join(OUT_GMSH, "sg33_cube_tetra4_min_gmsh41.msh")
    gmsh.initialize()
    gmsh.open(source)
    _report(3)
    _write(os.path.join(OUT_GMSH, "sg33_cube_tetra4_min_gmsh40.msh"), 4.0)
    _write(os.path.join(OUT_GMSH, "sg33_cube_tetra4_min_gmsh22.msh"), 2.2)
    gmsh.finalize()


def cube_two_materials():
    """Two stacked boxes -> 'matrix' + 'fibre', so one mesh covers an isotropic
    and an orthotropic material in the same SwiftComp write."""
    gmsh.initialize()
    gmsh.model.add("cube_two_materials")
    lower = gmsh.model.occ.addBox(0, 0, 0, SIZE, SIZE, SIZE / 2)
    upper = gmsh.model.occ.addBox(0, 0, SIZE / 2, SIZE, SIZE, SIZE / 2)
    gmsh.model.occ.fragment([(3, lower)], [(3, upper)])
    gmsh.model.occ.synchronize()

    vols = sorted(tag for dim, tag in gmsh.model.getEntities(3))
    g1 = gmsh.model.addPhysicalGroup(3, [vols[0]], 1)
    gmsh.model.setPhysicalName(3, g1, "matrix")
    g2 = gmsh.model.addPhysicalGroup(3, [vols[1]], 2)
    gmsh.model.setPhysicalName(3, g2, "fibre")

    gmsh.option.setNumber("Mesh.MeshSizeMin", SIZE)
    gmsh.option.setNumber("Mesh.MeshSizeMax", SIZE)
    gmsh.model.mesh.generate(3)
    _write(os.path.join(OUT_GMSH, "sg33_cube_two_materials_min_gmsh41.msh"), 4.1)
    _report(3)
    gmsh.finalize()


def _report(sgdim):
    counts = {}
    for dim, tag in gmsh.model.getPhysicalGroups():
        name = gmsh.model.getPhysicalName(dim, tag)
        n = 0
        for ent in gmsh.model.getEntitiesForPhysicalGroup(dim, tag):
            types, tags, _ = gmsh.model.mesh.getElements(dim, int(ent))
            n += sum(len(t) for t in tags)
        counts[name] = (dim, n)
    nodes = len(gmsh.model.mesh.getNodes()[0])
    print(f"   nodes={nodes} groups={counts}")




def thermoelastic_sidecars():
    """sections.json + config.json that drive the CTE-vector-length defect.

    One isotropic and one orthotropic material, both carrying a 6-component CTE
    vector and a specific heat, plus physics=1 so the writer emits the thermal
    record at all.
    """
    sections = {"sections": [
        _material_record("matrix", 1, isotropy=0, density=1200.0,
                         elastic={"e1": 3.5e9, "nu12": 0.35},
                         cte=[58.0e-6, 58.0e-6, 58.0e-6, 0.0, 0.0, 0.0],
                         specific_heat=1100.0),
        _material_record("fibre", 2, isotropy=1, density=1760.0,
                         elastic={"e1": 230.0e9, "e2": 15.0e9, "e3": 15.0e9,
                                  "g12": 15.0e9, "g13": 15.0e9, "g23": 7.0e9,
                                  "nu12": 0.2, "nu13": 0.2, "nu23": 0.07},
                         cte=[-0.5e-6, 10.0e-6, 10.0e-6, 0.0, 0.0, 0.0],
                         specific_heat=750.0),
    ]}
    config = {"analysis": 0, "physics": 1, "model": 0, "geo_correct": False,
              "do_damping": 0, "is_temp_nonuniform": 0, "force_flag": 0, "steer_flag": 0}
    _dump_json(os.path.join(OUT_GMSH, "sections_thermoelastic_cte_bug.json"), sections)
    _dump_json(os.path.join(OUT_GMSH, "config_thermoelastic.json"), config)


def _material_record(name, mat_id, **payload):
    record = {"name": name, "model": "sd1", "label": str(mat_id)}
    record.update(payload)
    return {"kind": "material", "theory": "cauchy_continuum",
            "name": name, "id": mat_id, "payload": record}


def _dump_json(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, indent=2)
        file.write("\n")
    print("wrote", os.path.basename(path))


def abaqus_distribution_input():
    """A deck whose *Distribution keeps its rows in an external Input= file.

    Three stacked hexahedra: element 1 is the isotropic matrix, elements 2 and 3
    are orthotropic and take their orientation from the distribution --
    deliberately with DIFFERENT fibre directions (+X and +Y), so a reader that
    drops the external file collapses them onto one value and the failure shows
    up as a count of distinct orientations rather than needing inspection.

    Keyword order matters: the *Solid Section cards must not be the file's last
    block. A trailing newline after their bare "," data line makes inpRW emit an
    extra empty data row, and sgio's `_process_section` does
    `float(section_block.data[-2])` guarding only ValueError/IndexError, so it
    dies with a TypeError before ever reaching the defect under test.
    """
    for name, text in (("sg33_cube_distribution_input_bug.inp", _ABQ_INP),
                       ("sg33_cube_distribution_input_bug.ori", _ABQ_ORI)):
        with open(os.path.join(OUT_ABQ, name), "w", encoding="utf-8", newline="\n") as file:
            file.write(text)
        print("wrote", name)


_ABQ_INP = """** Minimal reproduction: *Distribution with its data in an external Input= file.
**
** sgio builds its distribution table only from the rows physically present
** under the keyword and never follows Input=, so this table reads as empty.
** 0.7.0 then silently gave every element in the Yarn set the same default
** orientation; 0.8.0 raises "has no coordinates for element 2".
**
** Geometry is 3 stacked C3D8 hexahedra on a 1x1x3 column:
**   element 1 -> Matrix, isotropic, no orientation
**   elements 2,3 -> Yarn,  orthotropic, orientation from the distribution
** The two yarn elements are given DIFFERENT fibre directions in the .ori file
** (+X and +Y), so a reader that drops the file collapses them onto one
** orientation and the failure is visible by counting distinct values.
*Heading
sgio fixture: external *Distribution Input= file
*Node
1, 0.0, 0.0, 0.0
2, 1.0, 0.0, 0.0
3, 1.0, 1.0, 0.0
4, 0.0, 1.0, 0.0
5, 0.0, 0.0, 1.0
6, 1.0, 0.0, 1.0
7, 1.0, 1.0, 1.0
8, 0.0, 1.0, 1.0
9, 0.0, 0.0, 2.0
10, 1.0, 0.0, 2.0
11, 1.0, 1.0, 2.0
12, 0.0, 1.0, 2.0
13, 0.0, 0.0, 3.0
14, 1.0, 0.0, 3.0
15, 1.0, 1.0, 3.0
16, 0.0, 1.0, 3.0
*Element, Type=C3D8
1, 1, 2, 3, 4, 5, 6, 7, 8
2, 5, 6, 7, 8, 9, 10, 11, 12
3, 9, 10, 11, 12, 13, 14, 15, 16
*ElSet, ElSet=Matrix
1
*ElSet, ElSet=Yarn
2, 3
*Distribution Table, Name=OrientationVectors
COORD3D,COORD3D
*Distribution, Location=Element, Table=OrientationVectors, Name=OrientationVectors, Input=sg33_cube_distribution_input_bug.ori
*Orientation, Name=Orientations, Definition=coordinates
OrientationVectors
1, 0
*Solid Section, ElSet=Matrix, Material=Mat0
,
*Solid Section, ElSet=Yarn, Material=Mat1, Orientation=Orientations
,
*Material, Name=Mat0
*Elastic
3.5e+09, 0.35
*Material, Name=Mat1
*Elastic, type=ENGINEERING CONSTANTS
2.3e+11, 1.5e+10, 1.5e+10, 0.2, 0.2, 0.07, 1.5e+10, 1.5e+10
7.0e+09
"""

_ABQ_ORI = """** Orientation vectors, Abaqus *Distribution external data format.
** 1st vector is the fibre direction, 2nd an arbitrary perpendicular vector.
** The leading blank-label row is Abaqus's default entry.
, 1.0, 0.0, 0.0,   0.0, 1.0, 0.0
2, 1.0, 0.0, 0.0,   0.0, 1.0, 0.0
3, 0.0, 1.0, 0.0,   -1.0, 0.0, 0.0
"""


if __name__ == "__main__":
    cube_with_boundary_group()
    square_with_boundary_group()
    cube_version_variants()
    cube_two_materials()
    thermoelastic_sidecars()
    abaqus_distribution_input()
