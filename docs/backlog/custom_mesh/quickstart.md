(custom_mesh_quickstart)=
# Quick Start: Simple Triangle Mesh

This page shows you how to create a simple StructureGene from scratch with a
minimal working example.

## Goal

Create a square plate with 2 triangular elements and write it to SwiftComp
format.

```{image} https://via.placeholder.com/300x300/e0e0e0/000000?text=Square+with+2+Triangles
:alt: Square divided into 2 triangles
:align: center
```

```text
Node Layout:
3 -------- 2
|        / |
|      /   |
|    /     |
|  /       |
0 -------- 1
```

## Complete Example

Here's a complete, working example you can copy and run:

```python
import numpy as np
from meshio import Mesh, CellBlock
from sgio import StructureGene
from sgio.model import CauchyContinuumModel
import sgio

# Step 1: Create StructureGene with configuration
sg = StructureGene(
    name='simple_plate',
    sgdim=2,  # 2D plate analysis
    smdim=2   # 2D structural model
)

# Step 2: Define material
steel = CauchyContinuumModel(
    name='Steel',
    isotropy=2,      # 2 = isotropic
    e=200e9,         # Young's modulus (Pa)
    nu=0.3,          # Poisson's ratio
    density=7850     # Density (kg/m³)
)
sg.materials['Steel'] = steel

# Step 3: Create material-orientation combination
sg.mocombos = {
    1: ('Steel', 0.0),  # Property ID 1 -> Steel at 0°
}

# Step 4: Define nodes (4 corners of square)
points = np.array([
    [0.0, 0.0, 0.0],  # Node 0 (bottom-left)
    [1.0, 0.0, 0.0],  # Node 1 (bottom-right)
    [1.0, 1.0, 0.0],  # Node 2 (top-right)
    [0.0, 1.0, 0.0],  # Node 3 (top-left)
])

# Step 5: Define elements (2 triangles)
cells = [
    CellBlock(
        type='triangle',
        data=np.array([
            [0, 1, 2],  # Triangle 1 (bottom-right half)
            [0, 2, 3],  # Triangle 2 (top-left half)
        ])
    )
]

# Step 6: Assign properties to elements
cell_data = {
    'property_id': [
        np.array([1, 1])  # Both elements use property 1 (Steel)
    ]
}

# Step 7: Assemble mesh
sg.mesh = Mesh(
    points=points,
    cells=cells,
    cell_data=cell_data
)

# Step 8: Verify
print(f"Created: {sg.name}")
print(f"  Nodes: {sg.nnodes}")
print(f"  Elements: {sg.nelems}")
print(f"  Materials: {list(sg.materials.keys())}")

# Step 9: Write to SwiftComp format
sgio.write(
    sg=sg,
    fn='simple_plate.sc',
    file_format='swiftcomp',
    format_version='2.1',
    model_type='PL1'  # 2D plate, classical model
)

print("✓ Written to simple_plate.sc")
```

## Understanding the Example

**Step 1-2: Setup**
Create the StructureGene container and define your material. For a 2D plate,
use `sgdim=2`.

**Step 3: Mocombos**
Create the material-orientation combination. Property ID 1 maps to Steel at 0
degrees.

**Step 4: Nodes**
Define node coordinates. Always use 3 columns (`x`, `y`, `z`) even for 2D
problems. Use `z=0` for planar structures.

**Step 5: Elements**
Define elements by listing node indices. **CRITICAL**: Use 0-based indices
(`0`, `1`, `2`, `3`), not your original node IDs.

**Step 6: Property Assignment**
Each element gets a property ID that references a mocombo. Here both elements
use property 1.

**Step 7-9: Finish**
Assemble the mesh, verify the structure, and write to file.

## Key Points to Remember

1. **Indices are 0-based**: In the connectivity array, use indices `0`, `1`,
   `2`, `3` and not your original node IDs
2. **Property chain**: Element → `property_id` → mocombo → `(material, angle)`
3. **Material names must match**: The name in mocombos must exactly match a key
   in `sg.materials`
4. **Always 3D coordinates**: Use `[x, y, 0.0]` for 2D problems

## What's Next?

- Want multiple materials or orientations? See the composite laminate example
  in {ref}`custom_mesh_data_structures`
- Converting existing data? See {ref}`custom_mesh_conversion`
- Having issues? Check {ref}`custom_mesh_troubleshooting`

## 3D Solid Quick Example

For a 3D structure, just change `sgdim=3` and use 3D element types:

```python
sg = StructureGene(name='cube', sgdim=3, smdim=3)

# ... define material and mocombos ...

cells = [
    CellBlock(
        type='tetra',  # Tetrahedral element
        data=np.array([[0, 1, 2, 3]])  # 4 nodes per tetrahedron
    )
]

# Write with SD1 (3D solid) model type
sgio.write(
    sg=sg,
    fn='cube.sc',
    file_format='swiftcomp',
    format_version='2.1',
    model_type='SD1'
)
```

## Model Types

When writing files, choose the appropriate model type:

- **Beams (1D)**: `'BM1'` (Euler-Bernoulli), `'BM2'` (Timoshenko)
- **Plates/Shells (2D)**: `'PL1'` (Kirchhoff-Love), `'PL2'` (Reissner-Mindlin)
- **Solids (3D)**: `'SD1'` (classical), `'SD2'` (refined)

