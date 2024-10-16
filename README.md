# SGIO

Structure Gene (SG) I/O

Python package interfacing VABS and SwiftComp.
The package is developed based on [meshio](https://github.com/nschloe/meshio), which is used for converting meshing data.

The package can be used to
- read/write SG data from/to different formats
- convert SG/mesh data between different formats
- read structural property from VABS/SwiftComp output
- create 1D SG from layup input

Supported data formats:
- for complete SG data
  - VABS, SwiftComp, Abaqus
- for mesh data only
  - all formats supported by meshio

A structure gene (SG) is defined as the smallest mathematical building block of a structure.[^1]
A cross-section (CS) is a type of 2D SG.


## Installation

Download the package.

Install dependencies.
```shell
pip install -r <INSTALL_DIR>/sgio/sgio/requirements.txt
```

Configure environment variables.
- Add the package root directory to `PYTHONPATH`.
- Add `<INSTALL_DIR>/sgio/bin` to `PATH`.


## Usage

Command line interface
```
usage: sgio [-h] {build,b,convert,c} ...

CS/SG I/O functions

positional arguments:
  {build,b,convert,c}  sub-command help
    build (b)          Build 1D SG
    convert (c)        Convert CS/SG data file

optional arguments:
  -h, --help           show this help message and exit
```

### Convert SG data

Command line interface
```
usage: sgio convert [-h] [-ff FROM_FORMAT] [-tf TO_FORMAT] [-d SGDIM] [-m MODEL] [-mo] from to

positional arguments:
  from                  CS/SG file to be read from
  to                    CS/SG file to be written to

optional arguments:
  -h, --help            show this help message and exit
  -ff FROM_FORMAT, --from-format FROM_FORMAT
                        CS/SG file format to be read from
  -tf TO_FORMAT, --to-format TO_FORMAT
                        CS/SG file format to be written to
  -d SGDIM, --sgdim SGDIM
                        SG dimension (SwiftComp only)
  -m MODEL, --model MODEL
                        CS/SG model
  -mo, --mesh-only      Mesh only conversion
```

#### Example: Convert cross-sectional data from Abaqus (.inp) to VABS input

Suppose a cross-section has been built in Abaqus and output to `cross-section.inp`.
To convert the data to the VABS input (Timoshenko model) `cross-section.sg`:
```
sgio convert cross-section.inp cross-section.sg -ff abaqus -tf vabs -m bm2
```

Check out the example `examples/convert_cs_from_abaqus_to_vabs` for more details.


## License


## Reference

[^1]: https://msp.org/jomms/2016/11-4/p03.xhtml
