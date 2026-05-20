from __future__ import annotations

from typing import Any

from abaqus import mdb
from abaqusConstants import (
    ANALYSIS,
    AXIS_1,
    AXIS_3,
    CARTESIAN,
    COPLANAR_EDGES,
    DEFAULT,
    DEFORMABLE_BODY,
    DISCRETE,
    DOMAIN,
    EDGE,
    ENGINEERING_CONSTANTS,
    FROM_SECTION,
    MIDDLE_SURFACE,
    ODB,
    OFF,
    ON,
    PERCENTAGE,
    QUAD,
    RIGHT,
    ROTATION_NONE,
    SIDE1,
    SINGLE,
    STACK_3,
    STRUCTURED,
    TWO_D_PLANAR,
    VECTOR,
)
from regionToolset import Region
from section import SectionLayer

DEFAULT_MODEL_NAME = "Model-1"
DEFAULT_JOB_NAME = "sg2_box_solid_section"
DEFAULT_OUTER_HALF_SIZE = 25.0
DEFAULT_INNER_HALF_SIZE = 20.0
DEFAULT_PARTITION_HALF_SIZE = 21.18
DEFAULT_MESH_SIZE = 5.0
DEFAULT_DENSITY = 1.0
DEFAULT_ELASTIC_CONSTANTS = (
    10.0,
    20.0,
    30.0,
    0.12,
    0.13,
    0.23,
    1.2,
    1.3,
    2.3,
)
DEFAULT_INNER_PLY_THICKNESS = 1.0
DEFAULT_OUTER_PLY_THICKNESS = 1.0
DEFAULT_INNER_PLY_ANGLE = 0.0
DEFAULT_OUTER_PLY_ANGLE = 45.0
DEFAULT_INNER_NUM_PLIES = 2
DEFAULT_OUTER_NUM_PLIES = 2

INNER_SET_NAME = "Set-2"
OUTER_SET_NAME = "Set-1"
ORIENTATION_EDGE_SET_NAME = "Set-4"
PART_NAME = "Part-1"
INSTANCE_NAME = "Part-1-1"
MATERIAL_NAME = "Material-1"
OUTER_SECTION_NAME = "Section-3"
INNER_SECTION_NAME = "Section-2"


def _ensure_fresh_fixture_names(
    model: Any,
    job_name: str,
    create_job: bool,
) -> None:
    """Validate that the target model does not already contain this fixture."""
    used_names = [
        (PART_NAME, model.parts, "part"),
        (MATERIAL_NAME, model.materials, "material"),
        (OUTER_SECTION_NAME, model.sections, "section"),
        (INNER_SECTION_NAME, model.sections, "section"),
        (INSTANCE_NAME, model.rootAssembly.instances, "instance"),
    ]

    for name, container, object_type in used_names:
        if name in container:
            raise ValueError(
                "Model '{}' already contains {} '{}'. "
                "Use a fresh model name.".format(model.name, object_type, name)
            )

    if create_job and job_name in mdb.jobs:
        raise ValueError("Job '{}' already exists.".format(job_name))


def _validate_parameters(
    outer_half_size: float,
    inner_half_size: float,
    partition_half_size: float,
    mesh_size: float,
    density: float,
    elastic_constants: tuple[float, ...],
    inner_ply_thickness: float,
    outer_ply_thickness: float,
    inner_num_plies: int,
    outer_num_plies: int,
) -> None:
    """Validate the input parameters used to build the fixture."""
    if outer_half_size <= 0.0:
        raise ValueError("`outer_half_size` must be positive.")
    if inner_half_size <= 0.0:
        raise ValueError("`inner_half_size` must be positive.")
    if inner_half_size >= outer_half_size:
        raise ValueError(
            "`inner_half_size` must be smaller than `outer_half_size`."
        )
    if not inner_half_size < partition_half_size < outer_half_size:
        raise ValueError(
            "`partition_half_size` must be between `inner_half_size` and `outer_half_size`."
        )
    if mesh_size <= 0.0:
        raise ValueError("`mesh_size` must be positive.")
    if density <= 0.0:
        raise ValueError("`density` must be positive.")
    if len(elastic_constants) != 9:
        raise ValueError(
            "`elastic_constants` must contain 9 engineering constants."
        )
    if inner_ply_thickness <= 0.0 or outer_ply_thickness <= 0.0:
        raise ValueError("Ply thickness values must be positive.")
    if inner_num_plies <= 0 or outer_num_plies <= 0:
        raise ValueError("The number of plies must be positive.")


def _create_box_part(
    model: Any,
    outer_half_size: float,
    inner_half_size: float,
) -> Any:
    """Create the box cross-section base shell."""
    sketch = model.ConstrainedSketch(name="__profile__", sheetSize=200.0)
    sketch.rectangle(
        point1=(-outer_half_size, outer_half_size),
        point2=(outer_half_size, -outer_half_size),
    )
    sketch.rectangle(
        point1=(-inner_half_size, inner_half_size),
        point2=(inner_half_size, -inner_half_size),
    )

    part = model.Part(
        name=PART_NAME,
        dimensionality=TWO_D_PLANAR,
        type=DEFORMABLE_BODY,
    )
    part.BaseShell(sketch=sketch)
    del model.sketches["__profile__"]
    return part


def _partition_box_faces(
    model: Any,
    part: Any,
    outer_half_size: float,
    inner_half_size: float,
    partition_half_size: float,
) -> None:
    """Partition the ring into outer corner bands and inner wall bands."""
    sketch = model.ConstrainedSketch(
        name="__profile__",
        sheetSize=150.0,
        transform=part.MakeSketchTransform(
            sketchPlane=part.faces[0],
            sketchPlaneSide=SIDE1,
            sketchOrientation=RIGHT,
            origin=(0.0, 0.0, 0.0),
        ),
    )
    part.projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=sketch)
    sketch.rectangle(
        point1=(-partition_half_size, partition_half_size),
        point2=(partition_half_size, -partition_half_size),
    )
    sketch.Line(
        point1=(-outer_half_size, outer_half_size),
        point2=(-inner_half_size, inner_half_size),
    )
    sketch.Line(
        point1=(inner_half_size, inner_half_size),
        point2=(outer_half_size, outer_half_size),
    )
    sketch.Line(
        point1=(-inner_half_size, -inner_half_size),
        point2=(-outer_half_size, -outer_half_size),
    )
    sketch.Line(
        point1=(inner_half_size, -inner_half_size),
        point2=(outer_half_size, -outer_half_size),
    )

    part.PartitionFaceBySketch(faces=part.faces[:], sketch=sketch)
    del model.sketches["__profile__"]


def _build_layup(
    thickness: float,
    angle: float,
    material_name: str,
    num_plies: int,
) -> tuple[SectionLayer, ...]:
    """Create a repeated solid layup definition."""
    return tuple(
        SectionLayer(
            thickness=thickness,
            orientAngle=angle,
            numIntPts=1,
            material=material_name,
        )
        for _ in range(num_plies)
    )


def _create_material_and_sections(
    model: Any,
    density: float,
    elastic_constants: tuple[float, ...],
    inner_ply_thickness: float,
    outer_ply_thickness: float,
    inner_ply_angle: float,
    outer_ply_angle: float,
    inner_num_plies: int,
    outer_num_plies: int,
) -> None:
    """Create the orthotropic material and the two composite layups."""
    material = model.Material(name=MATERIAL_NAME)
    material.Density(table=((density,),))
    material.Elastic(
        table=(elastic_constants,),
        type=ENGINEERING_CONSTANTS,
    )

    model.CompositeSolidSection(
        name=INNER_SECTION_NAME,
        layupName="layer1",
        layup=_build_layup(
            thickness=inner_ply_thickness,
            angle=inner_ply_angle,
            material_name=MATERIAL_NAME,
            num_plies=inner_num_plies,
        ),
        symmetric=False,
    )
    model.CompositeSolidSection(
        name=OUTER_SECTION_NAME,
        layupName="layer2",
        layup=_build_layup(
            thickness=outer_ply_thickness,
            angle=outer_ply_angle,
            material_name=MATERIAL_NAME,
            num_plies=outer_num_plies,
        ),
        symmetric=False,
    )


def _create_face_sets(
    part: Any,
    outer_half_size: float,
    inner_half_size: float,
    partition_half_size: float,
) -> None:
    """Create face sets for the outer and inner laminate regions."""
    outer_sample = 0.5 * (outer_half_size + partition_half_size)
    inner_sample = 0.5 * (inner_half_size + partition_half_size)

    outer_faces = part.faces.findAt(
        ((0.0, outer_sample, 0.0),),
        ((-outer_sample, 0.0, 0.0),),
        ((outer_sample, 0.0, 0.0),),
        ((0.0, -outer_sample, 0.0),),
    )
    inner_faces = part.faces.findAt(
        ((0.0, inner_sample, 0.0),),
        ((-inner_sample, 0.0, 0.0),),
        ((inner_sample, 0.0, 0.0),),
        ((0.0, -inner_sample, 0.0),),
    )

    part.Set(faces=outer_faces, name=OUTER_SET_NAME)
    part.Set(faces=inner_faces, name=INNER_SET_NAME)


def _assign_sections(part: Any) -> None:
    """Assign the two composite sections to their corresponding face groups."""
    part.SectionAssignment(
        region=part.sets[OUTER_SET_NAME],
        sectionName=OUTER_SECTION_NAME,
        offset=0.0,
        offsetType=MIDDLE_SURFACE,
        offsetField="",
        thicknessAssignment=FROM_SECTION,
    )
    part.SectionAssignment(
        region=part.sets[INNER_SET_NAME],
        sectionName=INNER_SECTION_NAME,
        offset=0.0,
        offsetType=MIDDLE_SURFACE,
        offsetField="",
        thicknessAssignment=FROM_SECTION,
    )


def _assign_material_orientation(part: Any, outer_half_size: float) -> None:
    """Use the outer perimeter as the discrete reference direction."""
    outer_edges = part.edges.findAt(
        ((0.0, outer_half_size, 0.0),),
        ((-outer_half_size, 0.0, 0.0),),
        ((outer_half_size, 0.0, 0.0),),
        ((0.0, -outer_half_size, 0.0),),
    )
    part.Set(edges=outer_edges, name=ORIENTATION_EDGE_SET_NAME)
    part.MaterialOrientation(
        region=Region(faces=part.faces[:]),
        orientationType=DISCRETE,
        axis=AXIS_3,
        angle=0.0,
        additionalRotationType=ROTATION_NONE,
        additionalRotationField="",
        stackDirection=STACK_3,
        normalAxisDefinition=VECTOR,
        normalAxisVector=(0.0, 0.0, 1.0),
        normalAxisDirection=AXIS_3,
        primaryAxisDefinition=EDGE,
        primaryAxisRegion=part.sets[ORIENTATION_EDGE_SET_NAME],
        primaryAxisDirection=AXIS_1,
        flipNormalDirection=False,
        flipPrimaryDirection=True,
    )


def _mesh_part(part: Any, mesh_size: float) -> None:
    """Apply a structured quadrilateral mesh."""
    part.setMeshControls(
        regions=part.faces[:],
        elemShape=QUAD,
        technique=STRUCTURED,
    )
    part.seedPart(size=mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
    part.generateMesh()


def _create_assembly_and_job(
    model: Any,
    part: Any,
    job_name: str,
    create_job: bool,
) -> None:
    """Create the assembly instance and, optionally, the analysis job."""
    assembly = model.rootAssembly
    assembly.DatumCsysByDefault(CARTESIAN)
    assembly.Instance(name=INSTANCE_NAME, part=part, dependent=ON)
    assembly.regenerate()

    if not create_job:
        return

    mdb.Job(
        name=job_name,
        model=model.name,
        description="",
        type=ANALYSIS,
        atTime=None,
        waitMinutes=0,
        waitHours=0,
        queue=None,
        memory=90,
        memoryUnits=PERCENTAGE,
        getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE,
        nodalOutputPrecision=SINGLE,
        echoPrint=OFF,
        modelPrint=OFF,
        contactPrint=OFF,
        historyPrint=OFF,
        userSubroutine="",
        scratch="",
        resultsFormat=ODB,
        multiprocessingMode=DEFAULT,
        numCpus=1,
        numDomains=1,
        numGPUs=0,
        activateLoadBalancing=False,
        parallelizationMethodExplicit=DOMAIN,
    )


def _parse_bool(value: str, field_name: str) -> bool:
    """Parse a boolean-like dialog input."""
    normalized = value.strip().lower()
    if normalized in ("1", "true", "t", "yes", "y", "on"):
        return True
    if normalized in ("0", "false", "f", "no", "n", "off"):
        return False
    raise ValueError(
        "`{}` must be one of yes/no, true/false, or 1/0.".format(field_name)
    )


def _parse_float(value: str, field_name: str) -> float:
    """Parse a floating-point dialog input."""
    try:
        return float(value)
    except ValueError:
        raise ValueError("`{}` must be a number.".format(field_name))


def _parse_int(value: str, field_name: str) -> int:
    """Parse an integer dialog input."""
    try:
        return int(value)
    except ValueError:
        raise ValueError("`{}` must be an integer.".format(field_name))


def _prompt_sg2_box_solid_section_inputs() -> dict[str, Any] | None:
    """Open an Abaqus/CAE parameter dialog for this fixture."""
    from abaqus import getInputs

    fields = (
        ("Model name", DEFAULT_MODEL_NAME),
        ("Job name", DEFAULT_JOB_NAME),
        ("Create job? [yes/no]", "yes"),
        ("Geometry - outer half size", str(DEFAULT_OUTER_HALF_SIZE)),
        ("Geometry - inner half size", str(DEFAULT_INNER_HALF_SIZE)),
        ("Geometry - partition half size", str(DEFAULT_PARTITION_HALF_SIZE)),
        ("Mesh - seed size", str(DEFAULT_MESH_SIZE)),
        ("Material - density", str(DEFAULT_DENSITY)),
        ("Material - E1", str(DEFAULT_ELASTIC_CONSTANTS[0])),
        ("Material - E2", str(DEFAULT_ELASTIC_CONSTANTS[1])),
        ("Material - E3", str(DEFAULT_ELASTIC_CONSTANTS[2])),
        ("Material - nu12", str(DEFAULT_ELASTIC_CONSTANTS[3])),
        ("Material - nu13", str(DEFAULT_ELASTIC_CONSTANTS[4])),
        ("Material - nu23", str(DEFAULT_ELASTIC_CONSTANTS[5])),
        ("Material - G12", str(DEFAULT_ELASTIC_CONSTANTS[6])),
        ("Material - G13", str(DEFAULT_ELASTIC_CONSTANTS[7])),
        ("Material - G23", str(DEFAULT_ELASTIC_CONSTANTS[8])),
        (
            "Inner layup - ply thickness",
            str(DEFAULT_INNER_PLY_THICKNESS),
        ),
        ("Inner layup - ply angle (deg)", str(DEFAULT_INNER_PLY_ANGLE)),
        ("Inner layup - number of plies", str(DEFAULT_INNER_NUM_PLIES)),
        (
            "Outer layup - ply thickness",
            str(DEFAULT_OUTER_PLY_THICKNESS),
        ),
        ("Outer layup - ply angle (deg)", str(DEFAULT_OUTER_PLY_ANGLE)),
        ("Outer layup - number of plies", str(DEFAULT_OUTER_NUM_PLIES)),
    )
    values = getInputs(
        fields=fields,
        label="Specify sg2_box_solid_section parameters:",
        dialogTitle="Build sg2_box_solid_section",
    )
    if values is None:
        return None

    return {
        "model_name": values[0].strip() or DEFAULT_MODEL_NAME,
        "job_name": values[1].strip() or DEFAULT_JOB_NAME,
        "create_job": _parse_bool(values[2], "Create job"),
        "outer_half_size": _parse_float(
            values[3], "Geometry - outer half size"
        ),
        "inner_half_size": _parse_float(
            values[4], "Geometry - inner half size"
        ),
        "partition_half_size": _parse_float(
            values[5], "Geometry - partition half size"
        ),
        "mesh_size": _parse_float(values[6], "Mesh - seed size"),
        "density": _parse_float(values[7], "Material - density"),
        "elastic_constants": (
            _parse_float(values[8], "Material - E1"),
            _parse_float(values[9], "Material - E2"),
            _parse_float(values[10], "Material - E3"),
            _parse_float(values[11], "Material - nu12"),
            _parse_float(values[12], "Material - nu13"),
            _parse_float(values[13], "Material - nu23"),
            _parse_float(values[14], "Material - G12"),
            _parse_float(values[15], "Material - G13"),
            _parse_float(values[16], "Material - G23"),
        ),
        "inner_ply_thickness": _parse_float(
            values[17], "Inner layup - ply thickness"
        ),
        "inner_ply_angle": _parse_float(values[18], "Inner layup - ply angle"),
        "inner_num_plies": _parse_int(
            values[19], "Inner layup - number of plies"
        ),
        "outer_ply_thickness": _parse_float(
            values[20], "Outer layup - ply thickness"
        ),
        "outer_ply_angle": _parse_float(values[21], "Outer layup - ply angle"),
        "outer_num_plies": _parse_int(
            values[22], "Outer layup - number of plies"
        ),
    }


def build_sg2_box_solid_section(
    model_name: str = DEFAULT_MODEL_NAME,
    job_name: str = DEFAULT_JOB_NAME,
    create_job: bool = True,
    outer_half_size: float = DEFAULT_OUTER_HALF_SIZE,
    inner_half_size: float = DEFAULT_INNER_HALF_SIZE,
    partition_half_size: float = DEFAULT_PARTITION_HALF_SIZE,
    mesh_size: float = DEFAULT_MESH_SIZE,
    density: float = DEFAULT_DENSITY,
    elastic_constants: tuple[float, ...] = DEFAULT_ELASTIC_CONSTANTS,
    inner_ply_thickness: float = DEFAULT_INNER_PLY_THICKNESS,
    outer_ply_thickness: float = DEFAULT_OUTER_PLY_THICKNESS,
    inner_ply_angle: float = DEFAULT_INNER_PLY_ANGLE,
    outer_ply_angle: float = DEFAULT_OUTER_PLY_ANGLE,
    inner_num_plies: int = DEFAULT_INNER_NUM_PLIES,
    outer_num_plies: int = DEFAULT_OUTER_NUM_PLIES,
) -> Any:
    """Build the `sg2_box_solid_section` Abaqus SG fixture.

    Parameters
    ----------
    model_name : str, optional
        Name of the Abaqus model to populate. A new model is created if needed.
    job_name : str, optional
        Name of the Abaqus job to create when ``create_job`` is ``True``.
    create_job : bool, optional
        Whether to create the analysis job after meshing the part.
    outer_half_size : float, optional
        Half size of the outer square boundary.
    inner_half_size : float, optional
        Half size of the inner square boundary.
    partition_half_size : float, optional
        Half size of the intermediate partition square.
    mesh_size : float, optional
        Global seed size used for structured meshing.
    density : float, optional
        Density assigned to the orthotropic material.
    elastic_constants : tuple[float, ...], optional
        Abaqus engineering constants ordered as
        ``(E1, E2, E3, nu12, nu13, nu23, G12, G13, G23)``.
    inner_ply_thickness : float, optional
        Thickness of each inner layup ply.
    outer_ply_thickness : float, optional
        Thickness of each outer layup ply.
    inner_ply_angle : float, optional
        Orientation angle in degrees for inner plies.
    outer_ply_angle : float, optional
        Orientation angle in degrees for outer plies.
    inner_num_plies : int, optional
        Number of plies in the inner layup.
    outer_num_plies : int, optional
        Number of plies in the outer layup.

    Returns
    -------
    Any
        The created Abaqus part object.

    Raises
    ------
    ValueError
        If the target model already contains fixture objects with the same names,
        or if the requested job name already exists.
    """
    if model_name not in mdb.models:
        mdb.Model(name=model_name)

    model = mdb.models[model_name]
    _validate_parameters(
        outer_half_size=outer_half_size,
        inner_half_size=inner_half_size,
        partition_half_size=partition_half_size,
        mesh_size=mesh_size,
        density=density,
        elastic_constants=elastic_constants,
        inner_ply_thickness=inner_ply_thickness,
        outer_ply_thickness=outer_ply_thickness,
        inner_num_plies=inner_num_plies,
        outer_num_plies=outer_num_plies,
    )
    _ensure_fresh_fixture_names(
        model=model,
        job_name=job_name,
        create_job=create_job,
    )

    part = _create_box_part(
        model=model,
        outer_half_size=outer_half_size,
        inner_half_size=inner_half_size,
    )
    _partition_box_faces(
        model=model,
        part=part,
        outer_half_size=outer_half_size,
        inner_half_size=inner_half_size,
        partition_half_size=partition_half_size,
    )
    _create_material_and_sections(
        model=model,
        density=density,
        elastic_constants=elastic_constants,
        inner_ply_thickness=inner_ply_thickness,
        outer_ply_thickness=outer_ply_thickness,
        inner_ply_angle=inner_ply_angle,
        outer_ply_angle=outer_ply_angle,
        inner_num_plies=inner_num_plies,
        outer_num_plies=outer_num_plies,
    )
    _create_face_sets(
        part=part,
        outer_half_size=outer_half_size,
        inner_half_size=inner_half_size,
        partition_half_size=partition_half_size,
    )
    _assign_sections(part)
    _assign_material_orientation(part, outer_half_size=outer_half_size)
    _mesh_part(part, mesh_size=mesh_size)
    _create_assembly_and_job(model, part, job_name, create_job)
    return part


def prompt_and_build_sg2_box_solid_section() -> Any | None:
    """Prompt for parameters in Abaqus/CAE and build the fixture."""
    kwargs = _prompt_sg2_box_solid_section_inputs()
    if kwargs is None:
        return None
    return build_sg2_box_solid_section(**kwargs)


if __name__ == "__main__":
    prompt_and_build_sg2_box_solid_section()
