# sgio

Structure Gene (SG) I/O

Python package interfacing VABS and SwiftComp.
The package is developed based on [meshio](https://github.com/nschloe/meshio), which is used for converting meshing data.

The package can be used to
- read/write SG data from/to different formats
- convert SG/mesh data between different formats
- read structural property from VABS/SwiftComp output
- create 1D SG from layup input


Supported data formats
- for complete SG data
  - VABS, SwiftComp, Abaqus
- for mesh data only
  - All formats supported by meshio


## Installation


## Usage

### I/O for SG

Read an SG:
```
import sgio

sg = sgio.read(
    filename,  # Name of the SG file.
    format, # Format of the SG data. See doc for more info.
    version, # Version of the data format. See doc for more info.
    sgdim, # Dimension of the SG.
    smdim, # Dimension of the structural model.
)
```

Write SG data to a file:
```
import sgio

sgio.write(
    sg,  # SG data
    filename,  # Name of the SG file.
    format, # Format of the SG data. See doc for more info.
    version, # Version of the data format. See doc for more info.
    analysis, # Type of SG analysis. See doc for more info.
)
```


### I/O for mesh data

#### Use sgio functions

Read a mesh:
```
import sgio

sg = sgio.read(
    filename,  # Name of the SG file.
    format, # Format of the SG data. See doc for more info.
    version, # Version of the data format. See doc for more info.
    sgdim, # Dimension of the SG.
    smdim, # Dimension of the structural model.
    mesh_only=True
)
```

Write a mesh:
```
import sgio

sgio.write(
    sg,  # SG data
    filename,  # Name of the SG file.
    format, # Format of the SG data. See doc for more info.
    version, # Version of the data format. See doc for more info.
    mesh_only=True
)
```

#### Use meshio functions

Read a mesh:
```
import sgio.meshio as meshio

mesh = meshio.read(
    ... # See meshio doc for instructions.
)
```

Write a mesh:
```
sg.mesh.write(
    ... # See meshio doc for instructions.
)
```


## License
