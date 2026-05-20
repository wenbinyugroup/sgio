# SGIO


Structure Gene (SG) I/O

Python package interfacing VABS and SwiftComp.
The package is developed based on [meshio](https://github.com/nschloe/meshio), which is used for converting meshing data.

## Features

The package can be used to:
- Read/write SG data from/to different formats
- Convert SG/mesh data between different formats
- Read structural property from VABS/SwiftComp output
- Create 1D SG from layup input

**Supported Data Formats**

- For complete SG data:
  - VABS, SwiftComp, Abaqus
- For mesh data only:
  - All formats supported by meshio

A structure gene (SG) is defined as the smallest mathematical building block of a structure.[^1]
A cross-section (CS) is a type of 2D SG.

Online [documentation](https://wenbinyugroup.github.io/sgio/)

## Installation

### Option 1: Install via pip (Recommended)

```shell
pip install sgio
```

### Option 2: Standalone Executable (No Python Required)

Download and use the pre-built standalone executable that requires no Python installation:

1. Download the latest executable from the releases page
2. Run directly from command line:
   ```shell
   # Windows
   sgio.exe --help

   # Linux/macOS
   ./sgio --help
   ```

### Option 3: Build Your Own Executable

Build a standalone executable from source:

```shell
# Windows
build_executable.bat

# Linux/macOS
./build_executable.sh

# Or manually
python build_executable.py
```

See [BUILD_EXECUTABLE.md](BUILD_EXECUTABLE.md) for detailed instructions.

### Option 4: Manual Installation

1. [Download](https://github.com/wenbinyugroup/sgio) the package.
2. Install dependencies:
    ```shell
    pip install -r <INSTALL_DIR>/sgio/requirements.txt
    ```
3. Configure environment variables:
    - Add the package root directory to `PYTHONPATH`.
    - Add `<INSTALL_DIR>/sgio/bin` to `PATH`.

## Usage

### API

#### Example: Read Beam Properties from VABS Output File

```python
import sgio

model = sgio.readOutputModel('my_cross_section.sg.k', 'vabs', 'BM1')
```

### Command Line Interface

#### Example: Convert Cross-Sectional Data from Abaqus (.inp) to VABS Input

Suppose a cross-section has been built in Abaqus and output to `cross-section.inp`.
To convert the data to the VABS input (Timoshenko model) `cross-section.sg`:
```shell
python -m sgio convert cross-section.inp cross-section.sg -ff abaqus -tf vabs -m bm2
```

#### Complete Options

```text
usage: sgio [-h] [-v] {build,b,convert,c} ...

I/O library for VABS (cross-section) and SwiftComp (structural gene)

positional arguments:
  {build,b,convert,c}  sub-command help
    build (b)          Build 1D SG
    convert (c)        Convert CS/SG data file

optional arguments:
  -h, --help           show this help message and exit
  -v, --version        Show version number and exit
```

##### Convert SG Data

```text
usage: sgio convert [-h] [--loglevelcmd {debug,info,warning,error,critical}]
                    [--loglevelfile {debug,info,warning,error,critical}] [--logfile LOGFILE]      
                    [-ff FROM_FORMAT] [-ffv FROM_FORMAT_VERSION] [-tf TO_FORMAT]
                    [-tfv TO_FORMAT_VERSION] [-d {1,2,3}] [-ms {x,y,z,xy,yz,zx}] [-mry {x,y,z}]   
                    [-m {sd1,pl1,pl2,bm1,bm2}] [-mo] [-re]
                    from to

positional arguments:
  from                  CS/SG file to be read from
  to                    CS/SG file to be written to

optional arguments:
  -h, --help            show this help message and exit
  --loglevelcmd {debug,info,warning,error,critical}
                        Command line logging level
  --loglevelfile {debug,info,warning,error,critical}
                        File logging level
  --logfile LOGFILE     Logging file name
  -ff FROM_FORMAT, --from-format FROM_FORMAT
                        CS/SG file format to be read from
  -ffv FROM_FORMAT_VERSION, --from-format-version FROM_FORMAT_VERSION
                        CS/SG file format version to be read from
  -tf TO_FORMAT, --to-format TO_FORMAT
                        CS/SG file format to be written to
  -tfv TO_FORMAT_VERSION, --to-format-version TO_FORMAT_VERSION
                        CS/SG file format version to be written to
  -d {1,2,3}, --sgdim {1,2,3}
                        SG dimension (SwiftComp only)
  -ms {x,y,z,xy,yz,zx}, --model-space {x,y,z,xy,yz,zx}
                        Model space
  -mry {x,y,z}, --material-ref-y {x,y,z}
                        Axis used as the material reference y-axis
  -m {sd1,pl1,pl2,bm1,bm2}, --model {sd1,pl1,pl2,bm1,bm2}
                        CS/SG model
  -mo, --mesh-only      Mesh only conversion
  -re, --renumber-elements
                        Renumber elements
```

Check out the example `examples/convert_cs_from_abaqus_to_vabs` for more details.

## License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.

## Reference

[^1]: https://msp.org/jomms/2016/11-4/p03.xhtml
