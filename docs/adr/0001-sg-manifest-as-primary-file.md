---
status: accepted
---

# A JSON SG manifest is the primary on-disk form of a structure gene

No single file format fully describes an SG. Abaqus `.inp` and Gmsh `.msh` carry no `sgdim`,
`model_type` or model-space mapping; `.msh` carries no materials or sections; even a SwiftComp
input cannot tell its own `smdim` from its header. We decided that an SG on disk is a
**JSON SG manifest** that holds every SG-level parameter and references exactly one **model file**
(`.inp`, `.msh`, `.sc`, `.dat`, ...) by relative path. The manifest is primary; the model file is
referenced from it, not the other way round.

Reasons:

1. **Formats and third-party parsers stay untouched.** We neither extend `.inp`/`.msh` schemas
   (e.g. the non-standard `*Parameter, sgdim=2` that broke inpRW) nor patch vendored parsers.
2. **The extra data is required, so it must live somewhere.** The traditional place is comments
   in the model file, which a program cannot reliably extract and only a human or AI can
   interpret. A structured document makes the parameters machine-readable.
3. **The link between files must be data, not a naming convention.** Only the manifest can point
   at the model file: most mesh formats have nowhere to point back at a sidecar, and file-name
   pairing breaks silently on rename or move.
4. **One uniform shape for every SG.** Native solver inputs also need the manifest (for `smdim`),
   so there is no special case for "native" versus "foreign" formats.

## Considered Options

- **Peer files** (model file and JSON passed together, linked only by caller or file name):
  rejected by reason 3; there is no SG entity on disk.
- **Model file primary, JSON as sidecar:** same as peer files in practice, since the mesh format
  cannot reference the sidecar.

## Consequences

- The manifest is an sgio-owned format and needs a schema version; schema changes are format
  changes.
- Relative paths resolve against the manifest's directory; moving files must keep that layout.
- The Gmsh `main.msh + sections.json + config.json` bundle is replaced by one manifest.
- Each field has exactly one authority: data present in both the model file and the manifest is an
  error. API arguments (for in-process callers such as msg-abaqus-toolkit) may coexist with the
  manifest but must agree with it.
- `sgdim` and `model_type` are never inferred; if neither manifest nor API supplies them, reading
  fails. They are always manifest fields, even for SwiftComp/VABS whose headers partly encode them;
  there the header is checked for agreement, so a manifest alone tells what the SG is. Mesh dimension is not SG dimension (a strut lattice is `sgdim=3` with 1D elements).
- `model_space` moves from a write-time option to SG input data, because it describes how the
  model file's axes map to SG axes. It is stored on the SG; mesh coordinates stay as in the model
  file and writers project them.
- Overlap is judged per block, never per record. Each model file format declares the blocks it
  owns (Abaqus: materials, sections; SwiftComp/VABS: materials, sections, config, beam geometry
  and model space; Gmsh: none). The manifest writer omits owned blocks and the reader rejects them. Ownership is static
  per format, not probed from file content: an `.inp` without `*Material` cannot take `sections`
  from the manifest.
- Materials and sections are separate blocks: each material is declared once and sections
  reference it by name with a layup angle, so sections sharing a material do not duplicate it.
  Beam/shell section stiffness payloads are not part of version 1; no writer consumed them.
- The manifest is registered as an ordinary format (`sg_manifest`), so `read`/`write`/`convert` and
  the CLI handle it; `model_type` is stored as the same string the API takes (e.g. `"BM1"`).
- `write` loses its `model_space` argument; `read`/`convert` take `model_space` as read input and
  lose their `sgdim`/`model_type`/`model_space` defaults. VABS/SwiftComp readers set the model
  space themselves. This removes the silent `xy` projection that collapsed y-z cross-sections.
