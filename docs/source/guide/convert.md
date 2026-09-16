# Convert SG Data

{func}`sgio.convert` reads one format and writes another in a single call. The
`sgio convert` CLI command exposes the same operation.

```python
import sgio

sgio.convert(
    file_name_in='input.inp',
    file_name_out='output.sg',
    file_format_in='abaqus',
    file_format_out='vabs',
    sgdim=2,
    model_type='BM2',
    model_space='xy',
)
```

```bash
sgio convert input.inp output.sg -ff abaqus -tf vabs -d 2 -m BM2 -ms xy
```

| Python | CLI | Purpose |
|---|---|---|
| `file_format_in` / `file_format_out` | `-ff` / `-tf` | source and target format |
| `file_version_in` / `file_version_out` | `-ffv` / `-tfv` | format version, e.g. VABS `4.0` → `4.1` |
| `model_type` | `-m` | structural model, when the input format does not imply it |
| `sgdim` | `-d` | SG dimension, when the input format does not imply it |
| `model_space` | `-ms` | input mesh axes of a 1D/2D SG (`x`/`y`/`z`, `xy`/`yz`/`zx`), when the input format does not imply it |
| `analysis` | `-a` | `h`, `d`, or `fi` |
| `mesh_only` | `-mo` | convert geometry only |

There are no defaults for these SG arguments: omitting one the input format
cannot supply raises `IncompleteModelDataError`.

Format identifiers and the conversion matrix are in {doc}`/ref/formats`; the
full signature is in {ref}`ref_io`.

See {doc}`/examples/index` for worked conversions.
